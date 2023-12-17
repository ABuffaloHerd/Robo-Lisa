from interactions import Client, Intents, listen, ContextMenuContext, Message, message_context_menu
from interactions.api.events import MessageCreate
from dotenv import load_dotenv
import os
import pickle
import random
import asyncio

def load_pickle(file_name):
    with open(file_name, 'rb') as file:
        return pickle.load(file)

# Loading the serialized components
vectorizer = load_pickle('vectorizer.pkl')
classifier = load_pickle('classifier.pkl')
encoded_to_string = load_pickle('encoded_to_string.pkl')

# Your get_emoji_back function here
def get_emoji_back(encoded_number):
    return encoded_to_string.get(encoded_number, "Unknown")

def predict_emoji(text, classifier, vectorizer, threshold=0.1):
    # Preprocess and vectorize the input text
    text_vectorized = vectorizer.transform([text])
    
    # Get probabilities for each emoji
    probabilities = classifier.predict_proba(text_vectorized)[0]

    # Filter out predictions with probabilities above the threshold
    high_prob_indices = [i for i, prob in enumerate(probabilities) if prob > threshold]

    # Decode the emojis
    emojis = [get_emoji_back(index) for index in high_prob_indices]
    
    return emojis


load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Client(intents=Intents.ALL)

# count of how many replies the bot has before it stops.
count = 200

async def increment_count_every_2_hours():
    global count
    while True:
        count += 3
        await asyncio.sleep(3 * 60 * 60)  # 2 hours in seconds

@listen()
async def on_ready():
    print("Ready")
    print(f"This bot is owned by {bot.owner}.")
    asyncio.create_task(increment_count_every_2_hours())

@listen()
async def on_message_create(event: MessageCreate):
    if event.message.author.bot:  # Check if the message is from a bot
        return

    global count
    msg = event.message

    # Check if the bot is mentioned
    bot_mentioned = (
        f"@{bot.user.id}" in msg.content or
        f"<@{bot.user.id}>" in msg.content
    )
    if bot_mentioned:
        #gets rid of bot's name before running through the classifier
        text = msg.content.replace(f"@{bot.user.id}", "").replace(f"<@{bot.user.id}>", "").strip()

        #wakes the bot up for a bit
        count = count+3

    else: 
        text = msg.content

    # Determine whether to skip the count and random chance check
    skip_check = bot_mentioned or (count > 0 and random.randint(1, 10) == 1)

    if not skip_check:
        return #print(f"Check not passed. Exiting function. {bot_mentioned}, {count}")

    emoji_list = predict_emoji(text, classifier, vectorizer, threshold=0.1)

    if emoji_list:  # This is equivalent to checking if len(emoji_list) > 0
        guild_emojis = await event.message.guild.fetch_all_custom_emojis()

        emojis_to_send = ""

        for emoji_name in emoji_list:
            for guild_emoji in guild_emojis:
                if guild_emoji.name == emoji_name.replace(":",""):
                    emojis_to_send += str(guild_emoji)

        if emojis_to_send:
            if random.randint(1, 2) == 1:
                await event.message.reply(emojis_to_send)
            else:
                await event.message.channel.send(emojis_to_send)
        else:
            return

        count = count-1


bot.start(TOKEN)
