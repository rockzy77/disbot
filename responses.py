from random import choice, randint
import discord
import csv
import os
import re
import asyncio 
import pandas as pd


verification_states = {}

user_det = {}

user_details_csv = './user_det.csv'
blacklist_csv = './blacklist.csv'
user_level_csv = "user_levels.csv"

LEVELS = {
    'rookie': 0,
    "challenger": 100,
    "guardian": 300,
    "warrior": 900,
    "legend": 1500,
    "mythic": 2500,
}

LEVELSARRAY = ['rookie', 'challenger', 'guardian', 'warrior', 'legend', 'mythic']


def load_data(data_file):
    try:
        return pd.read_csv(data_file, index_col=0)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["uid","points","level", "messages", "eventsParti", "eventWon", "clipsShare", "offense"])
        df.set_index("uid", inplace=True)
        return df

def save_data(df, data_file):
    print("saving")
    df.to_csv(data_file)

email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Function to validate email
def validate_email(email):
    if re.match(email_pattern, email):
        return True
    else:
        return False

async def get_responses(user_input, message, clients):

    lowered = user_input.lower()

    new_profile_data = [0, "rookie", 0, 0, 0, 0, 0]

    author_mention = message.author.mention

    sguild = discord.utils.get(clients.guilds, name='TUF GAMERS')

    srole = discord.utils.get(sguild.roles, name='TufGamer👾')

    ldf = load_data(user_level_csv)
    
    if '?say' in lowered:
        if isinstance(message.channel, discord.DMChannel):
            return 
        
        checkA = await checkIfAdmin(message, 3)
        if(not checkA):
            await message.delete()
            return

        announcement = user_input.replace("?say ", "")

        await message.delete()

        await message.channel.send(announcement)

        

    elif '?hello' in lowered:
        if isinstance(message.channel, discord.DMChannel):
            return 
        await message.channel.send("Yo")
        
    elif '?verifyme' in lowered:
        if isinstance(message.channel, discord.DMChannel):
            return 
        if(message.channel.id != 1261357943434117141):
            return

        if(is_uid_blacklisted(message.author.id, blacklist_csv)):
            await message.channel.send(message.author.mention+", you have been blacklisted from verifying. Please contact admins to get whitelisted.")
            
            return 


        tguild = message.guild
        trole = discord.utils.get(tguild.roles, name='TufGamer👾')
        tmember = await tguild.fetch_member(message.author.id)

        if trole in tmember.roles:
            msg = await message.channel.send(f"{author_mention} You are already verified!")
            await asyncio.sleep(5)
            await msg.delete()
            await message.delete()
            return

        msg2 = await message.channel.send(author_mention+" Check your dm to start the verification process")
       
        verification_states[message.author.id] = {'step': 1}

        await message.author.send("-----------------------------------------------------------")
        await message.author.send("Welcome to TufGamers. Let's start the verification process")

        await message.author.send("Please type your real name")

        await asyncio.sleep(5)
        await message.delete()
        await msg2.delete()



    elif '?whitelist' in lowered:
        if isinstance(message.channel, discord.DMChannel):
            return 
        if(message.channel.id != 1261524708306845826):
            return

        checkA = await checkIfAdmin(message, 2)
        if(not checkA):
            return


        try:
            parts = user_input.split()
            if(len(parts) != 2):
                    await message.channel.send("Usage: ?whitelist <id/mention>")
                    return

            uid = 0

            match = re.search(r'\d+', parts[1])

            if match:
                number = match.group()
                uid = number
            else:
                print("No number found")

            smember = await sguild.fetch_member(uid)

            rows = []

            # Read the CSV file and store its contents
            with open(blacklist_csv, mode='r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['uid'] != uid:
                        rows.append(row)

            # Write the updated contents back to the CSV file
            with open(blacklist_csv, mode='w', newline='') as csvfile:
                fieldnames = ['uid']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            await message.channel.send(smember.mention+" have been whitelisted")


        except ValueError:
            await message.channel.send("Please provide a valid id")


    elif '?blacklist' in lowered:
        if isinstance(message.channel, discord.DMChannel):
            return 
        if(message.channel.id != 1261524708306845826):
            return

        checkA = await checkIfAdmin(message, 2)
        if(not checkA):
            return


        try:
            parts = user_input.split()
            if(len(parts) != 3):
                    await message.channel.send("Usage: ?blacklist <id/mention> <reason>")
                    return

            uid = 0

            reason = parts[2]

            match = re.search(r'\d+', parts[1])

            if match:
                number = match.group()
                uid = number
            else:
                print("No number found")

            smember = await sguild.fetch_member(uid)

            fileExist = os.path.isfile(blacklist_csv)

            fieldnames = ['uid']

            with open(blacklist_csv, mode='a' if fileExist else 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write the header only if the file does not exist
                if not fileExist:
                    writer.writeheader()
                
                # Write the data
                writer.writerow({
                    'uid': uid  
                })


            await message.channel.send(smember.mention+" have been blacklisted\nReason: "+reason)


        except ValueError:
            await message.channel.send("Please provide a valid id")

    elif '?clear' in lowered:
        if isinstance(message.channel, discord.DMChannel):
            return 
        if(not await checkIfAdmin(message, 3)):
            await message.delete()
            return

        try:
            parts = user_input.split()
            if(len(parts) != 2):
                    await message.channel.send("Usage: ?clear <number>")
                    return

            amount = int(parts[1])
            if(amount <= 0):
                await message.channel.send("Please provide a number greater than 0.")
                return
            
            deleted = await message.channel.purge(limit=amount)
        except ValueError:
            await message.channel.send("Please provide a valid number.")


    elif '?vaccept' in lowered:
        if isinstance(message.channel, discord.DMChannel):
            return 
        if(message.channel.id != 1261524708306845826):
            return

        checkA = await checkIfAdmin(message, 3)
        if(not checkA):
            return

        try:
            parts = user_input.split()
            if(len(parts) != 2):
                await message.channel.send("Usage: ?vaccept <id/mention>")
                return

            uid = 0

            match = re.search(r'\d+', parts[1])

            if match:
                number = match.group()
                uid = number
            else:
                print("No number found")

            smember = await sguild.fetch_member(uid)

            rrole = discord.utils.get(sguild.roles, name='Rookie')
            
            if srole and smember:
                await smember.add_roles(srole)
                await smember.add_roles(rrole)
                await smember.send("You have been verified and assigned the 'TufGamer' role.")
                notification_channel = sguild.get_channel(1261370428027572244)
                v_p_channel = sguild.get_channel(1261524708306845826)
                print(ldf)
                ldf.loc[uid] = new_profile_data
                print(ldf)
                save_data(ldf, user_level_csv)
                if notification_channel:
                    await notification_channel.send(f"{smember.mention} have earned the badge **TufGamer**")
                    
            else:
                await v_p_channel.send("Can't assign the role right now.")

        except ValueError:
            await message.channel.send("Please provide a valid id.")

    elif '?revoketg' in lowered:
        if isinstance(message.channel, discord.DMChannel):
            return 
        if(message.channel.id != 1261524708306845826):
            return

        if(not await checkIfAdmin(message, 2)):
            return

        try:
            parts = user_input.split()
            if(len(parts) != 3):
                await message.channel.send("Usage: ?revokeTG <id/mention> <reason>")
                return

            uid = 0

            reason = parts[2]

            match = re.search(r'\d+', parts[1])
            

            if match:
                number = match.group()
                uid = number
            else:
                print("No number found")

            smember = await sguild.fetch_member(uid)

            srole = discord.utils.get(sguild.roles, name="TufGamer👾")

            if(reason == 'INVALID_DETAILS'):
                fieldnames = ['uid']

                fileExist = os.path.isfile(blacklist_csv)

                with open(blacklist_csv, mode='a' if fileExist else 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    # Write the header only if the file does not exist
                    if not fileExist:
                        writer.writeheader()
                    
                    # Write the data
                    writer.writerow({
                        'uid': uid
                    })

            await smember.remove_roles(srole)

            await message.channel.send(smember.mention+"'s TufGamer badge has been revoked.\nReason: "+reason)

            await smember.send("Your TufGamer badge have been revoked.\nReason: "+reason)

        except ValueError:
            await message.channel.send("Please provide a valid id.")


    elif '?vreject' in lowered:
        if isinstance(message.channel, discord.DMChannel):
            return 
        if(message.channel.id != 1261524708306845826):
            return

        if(not await checkIfAdmin(message, 3)):
            return

        try:
            parts = user_input.split()
            if(len(parts) != 3):
                await message.channel.send("Usage: ?vreject <id/mention> <reason>")
                return

            uid = 0

            reason = parts[2]

            match = re.search(r'\d+', parts[1])
            

            if match:
                number = match.group()
                uid = number
            else:
                print("No number found")

            smember = await sguild.fetch_member(uid)

            uid_to_remove = smember.id

            fieldnames = []

            rows = []
            with open(user_details_csv, mode='r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                for row in reader:
                    if row['uid'] != uid_to_remove:
                        rows.append(row)

            # Write the modified data back to the CSV file
            with open(user_details_csv, mode='w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            print(rows)

            bmap = {
                'uid': uid
            }

            if(reason == 'INVALID_DETAILS'):
                fileExist = os.path.isfile(blacklist_csv)

                fieldnames = bmap.keys()

                with open(blacklist_csv, mode='a' if fileExist else 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    # Write the header only if the file does not exist
                    if not fileExist:
                        writer.writeheader()
                    
                    # Write the data
                    writer.writerow(bmap)



            notification_channel = sguild.get_channel(1261466967835938866)

            if notification_channel:
                await notification_channel.send(smember.mention+", your verification request was rejected\nReason: "+reason)

            await smember.send("Your verification was failed.\nReason: "+reason)
        except ValueError:
            await message.channel.send("Please provide a valid id.")


    elif '?profile' in lowered:

        if isinstance(message.channel, discord.DMChannel):
            return 

        if(message.channel.id != 1262260282126893067):
            return

        parts = user_input.split(' ')

        pmember = await sguild.fetch_member(message.author.id)

        uid = message.author.id

        if(len(parts) > 1):
            match = re.search(r'\d+', parts[1])
            if match:
                number = match.group()
                pmember = await sguild.fetch_member(number)
                uid = pmember.id
            else:
                print("No number found")

        trole = discord.utils.get(sguild.roles, name='TufGamer👾')
        
        if trole not in pmember.roles:
            await message.channel.send("Please verify yourself to earn rank badge")
            return 

        if(uid not in ldf.index):
            ldf.loc[uid] = new_profile_data
            save_data(ldf, user_level_csv)

        points = ldf.at[uid, "points"]
        level = ldf.at[uid, "level"]
        msg = ldf.at[uid, "messages"]
        eventParti = ldf.at[uid, "eventsParti"]
        eventWon = ldf.at[uid, "eventWon"]
        clipShare = ldf.at[uid, "clipsShare"]
        offense = ldf.at[uid, "offense"]


        embed = discord.Embed(title=pmember.display_name+"'s Profile", color=discord.Color.red())
        embed.set_thumbnail(url=pmember.display_avatar.url)
        embed.add_field(name="Points", value=points, inline=True)
        embed.add_field(name="Rank", value=level, inline=True)
        embed.add_field(name="Messages", value=msg, inline=True)
        embed.add_field(name="Events Participated", value=eventParti, inline=True)
        embed.add_field(name="Events Won", value=eventWon, inline=True)
        embed.add_field(name="Clips Shared", value=clipShare, inline=True)
        embed.add_field(name="Offence", value=offense, inline=True)
        embed.set_footer(text=f"Requested by {message.author.name}", icon_url=message.author.display_avatar.url)

        await message.channel.send(embed=embed)

    elif '?offence' in lowered:
        if isinstance(message.channel, discord.DMChannel):
            return 

        if(not await checkIfAdmin(message, 2)):
            return

        parts = user_input.split(" ")

        if(len(parts) != 3):
            await message.channel.send("Usage: ?offence <id/mention> <reason>")
            return

        uid = 0

        reason = parts[2]

        match = re.search(r'\d+', parts[1])
        if match:
            number = match.group()
            uid = number
        else:
            print("No number found")

        pmember = await sguild.fetch_member(uid)

        ldf.at[int(uid), "points"] -= 1
        ldf.at[int(uid), "offense"] += 1

        prev_level = ldf.at[int(uid), "level"]

        downgrade_needed, new_level = check_level_downgrade(ldf.at[int(uid), "points"], ldf.at[int(uid), "level"])

        await message.channel.send(pmember.mention+" has been charged with offence of \""+reason+"\". -1 point deducted")

        print(downgrade_needed)
        if(downgrade_needed):
            ldf.at[int(uid), "level"] = new_level
            rrole = discord.utils.get(sguild.roles, name=new_level.capitalize())
            prole = discord.utils.get(sguild.roles, name=prev_level.capitalize())
            if(prole in pmember.roles):
                await pmember.remove_roles(prole)
            await pmember.add_roles(rrole)

            dchannel = sguild.get_channel(1262280847852310558)

            await dchannel.send(pmember.mention+" has been demoted to "+new_level)

        save_data(ldf, user_level_csv)

    
    elif '?demote' in lowered:
        if isinstance(message.channel, discord.DMChannel):
            return 

        if(not await checkIfAdmin(message, 1)):
            return

        parts = user_input.split(" ")

        if(len(parts) != 2):
            await message.channel.send("Usage: ?demote <id/mention>")
        
        uid = 0

        match = re.search(r'\d+', parts[1])
        if match:
            number = match.group()
            uid = number
        else:
            print("No number found")

        pmember = await sguild.fetch_member(uid)

        prev_level = ldf.at[int(uid), "level"]
        print(prev_level)
        index = LEVELSARRAY.index(prev_level)
        print(index)
        index = index - 1
        new_level = LEVELSARRAY[index]

        ldf.at[int(uid), "level"] = new_level
        ldf.at[int(uid), "points"] = LEVELS[new_level]
         

        rrole = discord.utils.get(sguild.roles, name=new_level.capitalize())
        prole = discord.utils.get(sguild.roles, name=prev_level.capitalize())
        if(prole in pmember.roles):
            await pmember.remove_roles(prole)
        await pmember.add_roles(rrole)

        dchannel = sguild.get_channel(1262280847852310558)

        await dchannel.send(pmember.mention+" has been demoted to "+new_level)

        save_data(ldf, user_level_csv)

    elif '?promote' in lowered:
        if isinstance(message.channel, discord.DMChannel):
            return 

        if(not await checkIfAdmin(message, 1)):
            return

        parts = user_input.split(" ")

        if(len(parts) != 2):
            await message.channel.send("Usage: ?promote <id/mention>")
        
        uid = 0

        match = re.search(r'\d+', parts[1])
        if match:
            number = match.group()
            uid = number
        else:
            print("No number found")

        pmember = await sguild.fetch_member(uid)

        prev_level = ldf.at[int(uid), "level"]

        index = LEVELSARRAY.index(ldf.at[int(uid), "level"])
        index = index + 1
        new_level = LEVELSARRAY[index]

        ldf.at[int(uid), "level"] = new_level
        ldf.at[int(uid), "points"] = LEVELS[new_level]
         

        rrole = discord.utils.get(sguild.roles, name=new_level.capitalize())
        prole = discord.utils.get(sguild.roles, name=prev_level.capitalize())
        if(prole in pmember.roles):
            await pmember.remove_roles(prole)
        await pmember.add_roles(rrole)

        dchannel = sguild.get_channel(1262280788632670289)

        await dchannel.send(pmember.mention+" has been promoted to "+new_level.capitalize())

        save_data(ldf, user_level_csv)

    
    elif '?createvc' in lowered:
        if isinstance(message.channel, discord.DMChannel):
            return 

        vc_name = user_input.replace("?createvc", "")

        if(vc_name == ""):
            await message.channel.send("Usage: ?createvc <vc_name>")
            return

        pmember = await sguild.fetch_member(message.author.id)

        rank = ldf.at[message.author.id, "level"]

        index = LEVELSARRAY.index(rank)

        print(index)

        if(index < 2):  
            await message.channel.send(message.author.mention+", Only rank above guardian can use this function")
            return 

        category = sguild.get_channel(1262454472072892437)

        temp_vc = await sguild.create_voice_channel(name=vc_name, category=category)

        await message.channel.send(f"{message.author.mention}, your voice channel ({vc_name} ) is ready and waiting for you.")

        await wait_for_empty_channel(temp_vc, clients)

        await temp_vc.delete()

        await message.channel.send(f"{message.author.mention}, your voice channel ({vc_name} ) is terminated")

        
    elif message.channel.type == discord.ChannelType.private and message.author.id in verification_states:
        state = verification_states[message.author.id]

        if(state['step'] ==1):
            state['name'] = message.content
            state['step'] = 2
            await message.author.send("Please type your age")

        elif(state['step'] == 2):
            age = message.content
            if(age.isdigit()):
                state['age'] = message.content
                state['step'] = 3
                await message.author.send("Please type your email address")
            else:
                await message.author.send("Please type a valid age")

        elif(state['step'] == 3):
            email = message.content
            if(validate_email(email)):
                state['email'] = message.content
                state['step'] = 4
                await message.author.send("Verification submitted and sent for review. You will recieve the badge after admin review.")
            else:
                await message.author.send("Please type a valid email")
            
            umap = {
                'uid': message.author.id,
                'name': state['name'],
                'email': state['email'],
                'age': state['age']
            }

            fieldnames = umap.keys()

         

            existFile = os.path.isfile(user_details_csv)

            with open(user_details_csv, mode='a' if existFile else 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write the header only if the file does not exist
                if not existFile:
                    writer.writeheader()
                
                # Write the data
                writer.writerow(umap)

            

            v_p_channel = sguild.get_channel(1261524708306845826)

            if v_p_channel:
                print(v_p_channel)
                await v_p_channel.send("**Verification Request**\n"+str(message.author.id)+"\n"+message.author.mention+"\nName: "+state['name']+"\nAge: "+state['age']+"\nEmail: "+state['email'])

            del verification_states[message.author.id]

    else:
        helpchannel = sguild.get_channel(1261235367604916304)
        general_channel = sguild.get_channel(1257705320327680210)
        v_p_channel = sguild.get_channel(1261357943434117141)
        if (message.channel.id == 1261357943434117141):
            await message.delete()
            await general_channel.send(message.author.mention+", Please only use "+v_p_channel.mention+" **channel** for verification purpose. If you are facing any doubt related to verification please use "+helpchannel.mention+" **channel**")

        else:
            if isinstance(message.channel, discord.DMChannel):
                await message.author.send("Sorry. I am not a personal bot 🤗")
                return 

            print(message.channel.id)

            pic_channel = sguild.get_channel(1120387475844640890)
            vid_channel = sguild.get_channel(1252995922808274944)

            print(message.channel.id)

            uid = message.author.id

            if(uid not in ldf.index):
                ldf.loc[uid] = new_profile_data
                save_data(ldf, user_level_csv)

            if message.channel.id in [1120387475844640890, 1252995922808274944]:
                print("here")
                if message.attachments:
                    print("have")
                    for attachment in message.attachments:
                        if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'mp4', 'mkv', 'avi', 'mov', 'wmv']):
                            ldf.at[message.author.id, "clipsShare"] += 1
                            print('d')
                        else:
                            await message.delete()


            print("Message: "+user_input)
            ldf.at[message.author.id, "messages"] += 1

            if(ldf.at[message.author.id, "messages"] % 10 == 0): 
                ldf.at[message.author.id, "points"] += 1

            if(ldf.at[message.author.id, "messages"] % 2 == 0):
                ldf.at[message.author.id, "points"] += 1

            prev_lev = ldf.at[message.author.id, "level"]
            
            upgrade_needed, new_level = check_level_upgrade(ldf.at[message.author.id, "points"], ldf.at[message.author.id, "level"])


            if(upgrade_needed):
                ldf.at[message.author.id, "level"] = new_level
                rrole = discord.utils.get(sguild.roles, name=new_level.capitalize())
                prole = discord.utils.get(sguild.roles, name=prev_lev.capitalize())
                pmember = await sguild.fetch_member(message.author.id)
                if(prole in pmember.roles):
                    await pmember.remove_roles(prole)
                await pmember.add_roles(rrole)
                pchannel = sguild.get_channel(1262280788632670289)
                await pchannel.send(message.author.mention+" has been promoted as "+new_level.capitalize())


            save_data(ldf, user_level_csv)



async def wait_for_empty_channel(channel, client):
    def check_empty():
        return len(channel.members) == 0

    # Wait until the channel is empty
    await client.wait_for('voice_state_update', check=lambda m, before, after: check_empty())
    # Wait a few seconds to ensure the channel is truly empty
    await asyncio.sleep(5)
    if check_empty():
        return


def check_level_upgrade(current_points, current_level):
    upgrade_needed = False
    new_level = current_level
    
    # Sort levels based on points
    sorted_levels = sorted(LEVELS.items(), key=lambda x: x[1])
    
    for level, points in sorted_levels:
        if current_points >= points:
            if LEVELS[current_level] < points:  # Compare current level points with threshold
                new_level = level
                upgrade_needed = True
        else:
            break
    
    return upgrade_needed, new_level

def verify_text(user_input):
    lowered = user_input.lower()

    if 'fuck' in user_input:
        return ["That's not something you should say", "Try that again and see my wrath"]


def check_level_downgrade(current_points, current_level):
    downgrade_needed = False
    new_level = current_level
    
    if(current_points < LEVELS[current_level]):
        downgrade_needed = True
        if(current_points >= 2500):
            new_level = 'mythic'    
        elif(current_points >= 1500):
            new_level = 'legend'
        elif(current_points >= 900):
            new_level = 'warrior'
        elif(current_points >= 300):
            new_level = 'guardian'
        elif(current_points >= 100):
            new_level = 'challenger'
        else:
            new_level = 'rookie'
    
    return downgrade_needed, new_level


async def checkIfAdmin(message, level):
    tguild = message.guild
    sarole = discord.utils.get(tguild.roles, name='Supreme 🗿')
    arole = discord.utils.get(tguild.roles, name='Admin👁️')
    # srole = discord.utils.get(tguild.roles, name='Staff')
    tmember = await tguild.fetch_member(message.author.id)
    print(tmember.name)
    if(level == 1):
        if sarole in tmember.roles:
            return True
    elif(level == 2):
        if(sarole in tmember.roles or sarole in tmember.roles):
            return True
        else:
            return False
    elif(level == 3):
        if(sarole in tmember.roles or sarole in tmember.roles or srole in tmember.roles):
            return True
        else:
            return False
    else:
        return False


def is_uid_blacklisted(uid, user_details_csv):
    with open(user_details_csv, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['uid'] == str(uid):
                return True
    return False

