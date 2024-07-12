from random import choice, randint
import discord

verification_states = {}

async def get_responses(user_input, message, clients):

    lowered = user_input.lower()
    author_mention = message.author.mention
    

    if lowered == '?':
       await message.channel.send("Say Something")

    elif '?hello' in lowered:
        await message.channel.send("Yo")
        
    elif '?verifyme' in lowered:

            tguild = message.guild
            trole = discord.utils.get(tguild.roles, name='TufGamer')
            tmember = await tguild.fetch_member(message.author.id)

            if trole in tmember.roles:
                await message.channel.send(f"{author_mention} You are already verified!")
                return

            await message.channel.send(author_mention+" Check your dm to start the verification process")

            verification_states[message.author.id] = {'step': 1}

            await message.author.send("Welcome to TufGamers. Let's start the verification process")

            await message.author.send("Please type your real name")

    elif '?clear' in lowered:

        try:
            parts = user_input.split()
            if(len(parts) != 2):
                    await message.channel.send("Usage: !clear <number>")
                    return

            amount = int(parts[1])
            if(amount <= 0):
                await message.channel.send("Please provide a number greater than 0.")
                return
            
            deleted = await message.channel.purge(limit=amount)
        except ValueError:
            await message.channel.send("Please provide a valid number.")

    elif message.channel.type == discord.ChannelType.private and message.author.id in verification_states:
        state = verification_states[message.author.id]

        if(state['step'] ==1):
            state['name'] = message.content
            state['step'] = 2
            await message.author.send("Please type your age")

        elif(state['step'] == 2):
            state['age'] = message.content
            state['step'] = 3
            await message.author.send("Verification complete. Assigning you the 'Verified' role.")

            sguild = discord.utils.get(clients.guilds, name='TUF GAMERS')
            print(sguild)
            srole = discord.utils.get(sguild.roles, name='TufGamer')
            print(srole)
            smember = await sguild.fetch_member(message.author.id)
            print(smember)

            if srole and smember:
                await smember.add_roles(srole)
                await message.author.send("You have been verified and assigned the 'TufGamer' role.")
                notification_channel = sguild.get_channel(1261370428027572244)
                if notification_channel:
                    await notification_channel.send(f"{message.author.mention} have earned the badge **TufGamer**")
            else:
                await message.author.send("Can't assign you the role right now. Please contant the Staffs.")
            
            # Remove user from verification_states
            del verification_states[message.author.id]


def verify_text(user_input):
    lowered = user_input.lower()

    if 'fuck' in user_input:
        return ["That's not something you should say", "Try that again and see my wrath"]