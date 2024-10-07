import discord, clash, clanupdate, random
from discord.ext import tasks
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

botToken = os.getenv('BOT_KEY')
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
# ready check
async def on_ready():
    print(f'We have logged in as {client.user}')
    check_update.start()

# general help message
def help():
    message = """
        Available commands:\n```$help - Lists all available commands
$hello - Replies with 'Hello!'
$pingabletest - Pings leadership (Elder, Co-Leader, Leader)
$test - Replies with a ping to the message sender
$blacklistadd - Adds a player to the blacklist
$blacklistremove - Removes a player form the blacklist
$lineup - Shows the enemy clan's war lineup
$members - Lists current clan members
$lookup - Look up a player tag
$scout - Generates a scout report for the current war
$forcescout - Forcefully re-scouts the current war
```
"""
    return message

@client.event
# message responses
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("$help"):
        await message.channel.send(help())
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    if message.content.startswith('$pingabletest'):
        await message.channel.send('Ping test -> <@&1091886420060283031> <@&1091886707768557668> <@&1091886829122371616>')
    if message.content.startswith('$test'):
        await message.channel.send(f"Ping test -> <@{message.author.id}>")
    if message.content.startswith("$blacklistadd") or message.content.startswith("$bka"):
        line = message.content
        splitline = line.split()
        if line == splitline[0]:
            valid = False
        else:
            valid = clash.validtag(splitline[1])
        if valid:
            tag = clanupdate.blacklistadd(splitline[1])
            await message.channel.send(f"Player #{tag} successfully added to the blacklist.")
        else:
            await message.channel.send("Invalid command syntax, please use `$blacklistadd <name>,<tag>`\nNote that the name is not actually important, it is only there to make the database more human readable.")
    if message.content.startswith("$blacklistremove") or message.content.startswith("$bkr"):
        line = message.content
        splitline = line.split()
        valid = True
        if line == splitline[0]:
            valid = False
        if valid:
            tag, found = clanupdate.blacklistremove(splitline[1])
            if found:
                await message.channel.send(f"Player #{tag} successfully removed from the blacklist.")
            else:
                await message.channel.send(f"Player #{tag} was not found in the blacklist.")
        else:
            await message.channel.send("Invalid command syntax, please use `$blacklistremove <tag>`")
    if message.content.startswith("$lineup"):
        await message.channel.send(clanupdate.enemy_lineup())
    if message.content.startswith("$members"):
        await message.channel.send(clanupdate.list_mem())
    if message.content.startswith("$lookup"):
        line = message.content
        splitline = line.split()
        valid = True
        if line == splitline[0]:
            valid = False
        if valid:
            splitline[1] = splitline[1].upper()
            player = clanupdate.detailed_view(splitline[1])
            await message.channel.send(player)
        else:
            await message.channel.send("Invalid command syntax, please use `$lookup <tag>`")
    if message.content.startswith("$scout"):
        tag = clash.war_check()
        if tag != "Not in war!":
            if Path(f"scout_report_{tag}.xlsx").exists():
                await message.channel.send("Scout report:", file=discord.File(f'scout_report_{tag}.xlsx'))
            else:
                await message.channel.send("This will take a bit, please wait!")
                clanupdate.create_scout(tag, 0)
                await message.channel.send("Scout report:", file=discord.File(f'scout_report_{tag}.xlsx'))
        else:
            await message.channel.send("Can't scout a war that isn't happening! [no active war]")
    if message.content.startswith("$forcescout"):
        await message.channel.send("This will take a bit, please wait!")
        tag = clash.war_check()
        if tag != "Not in war!":
            clanupdate.create_scout(tag, 0)
            await message.channel.send("Scout report:", file=discord.File(f'scout_report_{tag}.xlsx'))
        else:
            await message.channel.send("Can't scout a war that isn't happening! [no active war]")
    if message.content.startswith("$cwlscout"):
        tag = clash.get_cwlwar(1)
        if Path(f"scout_report_{tag}.xlsx").exists():
            await message.channel.send("Cached scout report:", file=discord.File(f'scout_report_{tag}.xlsx'))
        else:
            await message.channel.send("This will take a bit, please wait!")
            clanupdate.create_scout(tag, 1)
            await message.channel.send("Scout report:", file=discord.File(f'scout_report_{tag}.xlsx'))
    if message.content.startswith("$forcecwl"):
        tag = clash.get_cwlwar(1)
        await message.channel.send("This will take a bit, please wait!")
        clanupdate.create_scout(tag, 1)
        await message.channel.send("Scout report:", file=discord.File(f'scout_report_{tag}.xlsx'))


        
@tasks.loop(minutes=1)
# loop tasks
async def check_update():
    channel = client.get_channel(1284535769343459380)
    print(f"60 seconds in Africa have passed. {random.randint(0,100)}")
    # calling the parser
    newmem, pings, tag = clanupdate.screening()
    if newmem == 201 or newmem == 202:
        print("Not in war/no new members")
    elif pings == 1:
        await channel.send(f"{newmem} <@&1091886420060283031> <@&1091886707768557668> <@&1091886829122371616>")
    elif pings == -1:
        await channel.send("Error somewhere! <@216927748080402432>")
    else:
        await channel.send(f"{newmem}")
        await channel.send(clanupdate.detailed_view(tag))
    
client.run(botToken)
