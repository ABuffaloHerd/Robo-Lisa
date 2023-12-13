from interactions import Client, Intents, listen
from interactions.api.events import MessageCreate
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Client(intents=Intents)

@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    print("Ready")
    print(f"This bot is owned by {bot.owner}.")


@listen()
async def on_message_create(event:MessageCreate):
    # This event is called when a message is sent in a channel the bot can see
    text = event.message.content
    print(f"message: {text}.")

bot.start(TOKEN)