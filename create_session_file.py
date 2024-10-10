import os

from pyrogram import Client
from dotenv import load_dotenv

load_dotenv()

app = Client('my_account', api_id=os.getenv('API_ID'), api_hash=os.getenv('API_HASH'))

app.run()