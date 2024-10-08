import discord, clanupdate, random, commands
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
        await message.channel.send(commands.help())
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    if message.content.startswith('$pingabletest'):
        await message.channel.send('Ping test -> <@&1091886420060283031> <@&1091886707768557668> <@&1091886829122371616>')
    if message.content.startswith('$test'):
        await message.channel.send(f"Ping test -> <@{message.author.id}>")
    if message.content.startswith("$blacklistadd") or message.content.startswith("$bka"):
        await message.channel.send(commands.blacklistadd(message.content))
    if message.content.startswith("$blacklistremove") or message.content.startswith("$bkr"):
        await message.channel.send(commands.blacklistremove(message.content))
    if message.content.startswith("$lineup"):
        await message.channel.send(clanupdate.enemy_lineup())
    if message.content.startswith("$members"):
        await message.channel.send(clanupdate.list_mem())
    if message.content.startswith("$lookup"):
        await message.channel.send(commands.lookup(message))
    if message.content.startswith("$scout"):
        await commands.scout(message.channel)
    if message.content.startswith("$forcescout"):
        await commands.scout(message.channel)
    if message.content.startswith("$cwlscout"):
        await commands.cwlscout(message.channel)
    if message.content.startswith("$forcecwl"):
        await commands.forcecwl(message.channel)

        
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
