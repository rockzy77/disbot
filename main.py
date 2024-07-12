import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_responses, verify_text

#Token Loading
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


#Setup Bot
intents = Intents.default()
intents.message_content = True

clients = Client(intents=intents)

#Message functionality

async def send_message(message, user_message):

    if not user_message:
        print("Message empty intents not enabled")
        return
        
    try:
        response = await get_responses(user_message, message, clients)
    except Exception as e:
        print(e)


#Start bot

@clients.event
async def on_ready():
    print(f'{clients.user} is now running')

@clients.event
async def on_message(message):
    if message.author == clients.user:
        return

    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')

    await send_message(message, user_message)

def main():
    clients.run(token=TOKEN)

if __name__ == '__main__':
    main()