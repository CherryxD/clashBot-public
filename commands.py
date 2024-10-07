import clash, clanupdate, discord
from pathlib import Path

def validate(message):
    splitline = message.split()
    if message == splitline[0]:
        return False
    else:
        return True

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
$cwlscout - Generates a scout report for the next CWL war
$forcecwl - Forcefully re-scouts the next CWL war
```
"""
    return message

def blacklistadd(message):
    splitline = message.split()
    if validate(message):
        tag = clanupdate.blacklistadd(splitline[1])
        return f"Player #{tag} successfully added to the blacklist."
    else:
        return "Invalid command syntax, please use `$blacklistadd <name>,<tag>`\nNote that the name is not actually important, it is only there to make the database more human readable."
    

def blacklistremove(message):
    splitline = message.split()
    if validate(message):
        tag, found = clanupdate.blacklistremove(splitline[1])
        if found:
            return f"Player #{tag} successfully removed from the blacklist."
        else:
            return f"Player #{tag} was not found in the blacklist."
    else:
        return "Invalid command syntax, please use `$blacklistremove <tag>`"
    

def lookup(message):
    splitline = message.split()
    if validate(message):
        return clanupdate.detailed_view(splitline[1].upper())
    else:
        return "Invalid command syntax, please use `$lookup <tag>`"
    

async def scout(channel):
    tag = clash.war_check()
    if tag != "Not in war!":
        if Path(f"scout_report_{tag}.xlsx").exists():
            await channel.send("Cached scout report:", file=discord.File(f'scout_report_{tag}.xlsx'))
        else:
            await channel.send("This will take a bit, please wait!")
            lineup = clash.get_enemywar()
            clanupdate.create_scout(lineup, tag)
            await channel.send("New scout report:", file=discord.File(f'scout_report_{tag}.xlsx'))
    else:
        await channel.send("Can't scout a war that isn't happening! [no active war]")
    return 


async def forcescout(channel):
    tag = clash.war_check()
    if tag != "Not in war!":
        await channel.send("This will take a bit, please wait!")
        lineup = clash.get_enemywar()
        clanupdate.create_scout(lineup, tag)
        await channel.send("New scout report:", file=discord.File(f'scout_report_{tag}.xlsx'))
    else:
        await channel.send("Can't scout a war that isn't happening! [no active war]")
    return 


async def cwlscout(channel):
    lineup, tag = clash.get_cwlwar()
    if Path(f"scout_report_{tag}.xlsx").exists():
        await channel.send("Cached scout report:", file=discord.File(f'scout_report_{tag}.xlsx'))
    else:
        await channel.send("This will take a bit, please wait!")
        clanupdate.create_scout(lineup, tag)
        await channel.send("New scout report:", file=discord.File(f'scout_report_{tag}.xlsx'))
    return


async def forcecwl(channel):
    lineup, tag = clash.get_cwlwar()
    await channel.send("This will take a bit, please wait!")
    clanupdate.create_scout(lineup, tag)
    await channel.send("New scout report:", file=discord.File(f'scout_report_{tag}.xlsx'))
    return