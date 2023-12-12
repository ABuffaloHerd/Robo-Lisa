import interactions
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = interactions.Client()

@interactions.listen()
async def on_startup():
    print("bot ready")

bot.start(TOKEN)