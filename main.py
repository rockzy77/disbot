import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_responses, verify_text
from discord.ext import tasks
import pandas as pd
import discord 

#Token Loading
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


LEVELS = {
    'rookie': 0,
    "challenger": 100,
    "guardian": 300,
    "warrior": 600,
    "legend": 900,
    "mythic": 1200,
}

#Setup Bot
intents = Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

clients = Client(intents=intents)

#Message functionality

def load_data(data_file):
    try:
        return pd.read_csv(data_file, index_col=0)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["uid","points","level", "messages", "eventsParti", "eventWon", "clipsShare", "offense"])
        df.set_index("uid", inplace=True)
        return df

async def send_message(message, user_message):

    try:
        response = await get_responses(user_message, message, clients)
    except Exception as e:
        print(e)


#Start bot

@clients.event
async def on_ready():
    print(f'{clients.user} is now running')
    guild = clients.get_guild(1110517279394889771)
    if guild:
        print(f"Guild fetched: {guild.name}")
        display_rank_table_task.start(guild) 


@clients.event
async def on_message(message):
    if message.author == clients.user:
        return


    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)

   

    print(f'[{channel}] {username}: "{user_message}"')

    await send_message(message, user_message)

@tasks.loop(minutes=3)  
async def display_rank_table_task(guild):
    ldf = load_data('user_levels.csv')
    channel = guild.get_channel(1262260377325015071)
    if channel:
        await display_rank_table(channel, ldf)

async def display_rank_table(channel, ldf):

    embed = discord.Embed(title="Rank Table", description="Current ranks of all users", color=discord.Color.red())
    
    # Iterate over the levels in reverse order
    for level in reversed(LEVELS.keys()):
        users_in_level = ""
        for user_id in ldf[ldf['level'] == level].index:
            member = await channel.guild.fetch_member(int(user_id))
            if member:
                users_in_level += f"{member.display_name}\n"
        
        if not users_in_level:
            users_in_level = "No users in this rank"
        
        embed.add_field(name=level.capitalize(), value=users_in_level, inline=False)
    
    msg = await channel.fetch_message(1262424440415846537)
    await msg.edit(embed=embed)

    # 1262421018773815356
def main():
    clients.run(token=TOKEN)
    
    

if __name__ == '__main__':
    main()