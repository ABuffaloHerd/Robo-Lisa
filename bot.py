from interactions import Client, Intents, listen, ContextMenuContext, Message, message_context_menu
from interactions.api.events import MessageCreate
from dotenv import load_dotenv
import os
import pickle
import random
import asyncio
import bot_retrainer
import bot_recorder

def load_pickle(file_name):
    with open(file_name, 'rb') as file:
        return pickle.load(file)

# Loading the serialized components
vectorizer = load_pickle('vectorizer.pkl')
classifier = load_pickle('classifier.pkl')
encoded_to_string = load_pickle('encoded_to_string.pkl')
tfidf_transformer = ""

def get_emoji_back(encoded_number):
    return encoded_to_string.get(encoded_number, "Unknown")

def predict_emoji(text, classifier, vectorizer, tfidf_transformer, threshold=0.1):
    # Preprocess and vectorize the input text
    text_vectorized = vectorizer.transform([text])

    # TFIDF Convert
    text_tfidf = tfidf_transformer.transform(text_vectorized)

    # Get probabilities for each emoji
    probabilities = classifier.predict_proba(text_tfidf)[0]

    # Filter out predictions with probabilities above the threshold
    high_prob_indices = [i for i, prob in enumerate(probabilities) if prob > threshold]

    # Decode the emojis
    emojis = [get_emoji_back(index) for index in high_prob_indices]
    
    return emojis

def answer_question(message):
    #first check if message is a question directed at lisabot
    if message.strip().endswith('?'):
        if len(message) > 1:
            likert_scale = {
            "strong_agree": ["YES", "YESSSS", "Absolutely!"],
            "agree": ["yes", "yessir", "ya"],
            "neutral": ["I actually dont know", "not rn", "lol", "I wish I could but I don't want to"],
            "disagree": ["nope", "ewww no", "naurrr"],
            "strong_disagree": ["WHAT NO", "NO", "Absolutely not!!!"]
            }

            random_opinion = random.choice(list(likert_scale.keys()))
            likert_answer = random.choice(likert_scale[random_opinion])

            return likert_answer
        else:
            return "?"

# put canned responses
def response_to(message):
    reply = ""

    keywords = {
        "actually":     lambda: "https://tenor.com/view/nerd-dog-nerd-dog-gif-nerd-dog-alen-orbanic-gif-15562966513664309472",
        "lisa burger":  lambda: "https://media.discordapp.net/attachments/1113266262345273428/1187365137598922802/imageedit_9_9053779888.png?ex=65969ef4&is=658429f4&hm=8ea4ed39282ce942d2556cced752afcc23353607d02a60e7b5119a4ac9c8e43f&=&format=webp&quality=lossless&width=462&height=462",
        "opinion":      lambda: "https://cdn.discordapp.com/attachments/1168400523104358442/1193073645715734578/y147cc9pwqac1.png?ex=65ab636b&is=6598ee6b&hm=c081a2716fbb8415c6a8be0d8ad8fa24fbfa639a5d97d0d673b15c65e2b984ca&",
        "research":     lambda: "https://cdn.discordapp.com/attachments/1205091789195837502/1205099075494739978/image.png?ex=65d722f9&is=65c4adf9&hm=0d250958d796faf568f638b7fa9a260afeef7b439f9fafc4a02f3d0b776728af&",
        "are you the real lisa?": lambda: "I am the real Lisa :lisaCat:",
        # add here as required
    }

    for keyword, action in keywords.items():
        if keyword in message:
            reply = action()

    return reply

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Client(intents=Intents.ALL)

# count of how many replies the bot has before it stops.
count = 10

async def run_every_2_hours():
    global count, vectorizer, tfidf_transformer, classifier, encoded_to_string
    while True:
        count += 3

        vectorizer, tfidf_transformer, classifier, encoded_to_string = bot_retrainer.retrain_bot()

        await asyncio.sleep(3 * 60 * 60)  # 3 hours in seconds

@listen()
async def on_ready():
    print(f"This bot is owned by {bot.owner}.")
    asyncio.create_task(run_every_2_hours())

@listen()
async def on_message_create(event: MessageCreate):
    global count
    msg = event.message
    guild_emojis = await msg.guild.fetch_all_custom_emojis()

    if msg.author.bot:  # Check if the message is from a bot
        return

    #lisa38
    if msg.author == "lisa38":
        #print("lisa spoke")
        bot_recorder.record_msg(msg, guild_emojis)

    # this function gets run if the bot is mentioned
    likert_answer = ""

    #checks for trigger word and sends hardcoded reply
    trigger = response_to(msg.content)
    if trigger != "":
        await msg.reply(trigger)
        return

    # Check if the bot is mentioned
    bot_mentioned = (
        f"@{bot.user.id}" in msg.content or
        f"<@{bot.user.id}>" in msg.content
    )
    if bot_mentioned:
        #gets rid of bot's name before running through the classifier
        text = msg.content.replace(f"<@{bot.user.id}>", "").strip()

        #wakes the bot up for a bit
        count = count+3

        #now check if the message is a question for lisa
        likert_answer = answer_question(text)

    else: 
        text = msg.content

    text = str(msg.author)[1:] + " " + text

    # Determine whether to skip the count and random chance check
    skip_check = bot_mentioned or (count > 0 and random.randint(1, 15) == 1)

    if not skip_check:
        return #print(f"Check not passed. Exiting function. {bot_mentioned}, {count}")

    emoji_list = predict_emoji(text, classifier, vectorizer, tfidf_transformer,threshold=0.1)

    if emoji_list:  # This is equivalent to checking if len(emoji_list) > 0
        emojis_to_send = ""

        for emoji_name in emoji_list:
            for guild_emoji in guild_emojis:
                if guild_emoji.name == emoji_name.replace(":",""):
                    emojis_to_send += str(guild_emoji)

        if emojis_to_send or likert_answer:
            if random.randint(1, 2) == 1:
                await msg.reply(likert_answer + emojis_to_send)
            else:
                await msg.channel.send(likert_answer + " " + emojis_to_send)
        else:
            if random.randint(1, 2) == 1:
                await msg.channel.send("HUH")

        count = count-1

bot.start(TOKEN)
