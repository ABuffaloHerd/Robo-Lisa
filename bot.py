from interactions import Client, Intents, listen, ContextMenuContext, Message, message_context_menu
from interactions.api.events import MessageCreate
from dotenv import load_dotenv
import os
import pickle

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

@listen()
async def on_ready():
    print("Ready")
    print(f"This bot is owned by {bot.owner}.")

@listen()
async def on_message_create(event: MessageCreate):
    if event.message.author.bot:  # Check if the message is from a bot
        return

    text = event.message.content
    emoji_list = predict_emoji(text, classifier, vectorizer, threshold=0.4)
    emoji_name = emoji_list[0]

    emojis = await event.message.guild.fetch_all_custom_emojis()
    emoji = ""

    print(emojis)

    for guild_emoji in emojis:
        print(guild_emoji)
        if guild_emoji.name == emoji_name:
            emoji = guild_emoji

    if emoji:
        await event.message.channel.send(str(emoji))
    else:
        await event.message.channel.send("No Emoji " + str(emoji_list))


bot.start(TOKEN)
