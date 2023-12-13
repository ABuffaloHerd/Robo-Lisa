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

@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    print("Ready")
    print(f"This bot is owned by {bot.owner}.")


@listen()
async def on_message_create(event:MessageCreate):
    if event.message.author == bot.user:
        return

    text = event.message.content

    emoji_list = predict_emoji(text, classifier, vectorizer, threshold=0.1)

    await event.message.reply(
        emoji_list
    )



bot.start(TOKEN)