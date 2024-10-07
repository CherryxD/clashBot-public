import clash
import time
import pandas
import json


def load_mem(filename):
    file = open(filename, mode='r', encoding='utf-8')
    players = []
    line = file.readline()
    while line != "":
        line = line.strip("\n").split(",")
        player = []
        player_tag = line[1]
        player_name = line[0]
        player.append(player_name)
        player.append(player_tag)
        players.append(player)
        line = file.readline()
    file.close()
    return players

def check_new():
    old_members = load_mem('memberslist.txt')
    new_members = clash.get_clan()
    new_members = clash.member_cleanup(new_members)
    feeders = load_mem('feederlist.txt')
    new_feeders = clash.get_feeder()
    new_feeders = clash.member_cleanup(new_feeders)
    clash.feederlist_save(new_feeders)
    clash.memberlist_save(new_members)
    new_tags = []
    old_tags = []
    feed_tags = []
    for member in new_members:
        new_tags.append(member[1])
    for member in old_members:
        old_tags.append(member[1])
    for member in feeders:
        feed_tags.append(member[1])
    for tag in new_tags:
        if tag not in old_tags and tag not in feed_tags:
            return tag
    return "0"

def counter_espionage(tag):
    enemy_members = load_mem('enemylist.txt')
    blacklisted = load_mem('blacklist.txt')
    spy = 0
    for enemy in enemy_members:
        if tag == enemy[1]:
            spy = 1
    for mem in blacklisted:
        if tag == mem[1]:
            spy = 2
    return spy

def blacklistadd(info):
    info = info.replace("#", "")
    clash.blacklist_save(info)
    tag = info.split(",")
    print(tag)
    return tag[1]

def blacklistremove(info):
    found = False
    tag = info.replace("#", "")
    found = clash.blacklist_update(tag)
    return tag, found

# code; 0 = new member, 1 = enemy spy, 2 = blacklisted player, 99 = war start
def message(code, tag):
    message = ""
    pings = 0
    if code == 1:
        message = f"Spy Alert: New Member #{tag} is a possible enemy spy!"
        pings = 1
    elif code == 2:
        message = f"Blacklisted player #{tag} has joined the clan!"
        pings = 1
    elif code == 99:
        message = f"New war started against #{tag} !"
    else:
        message = f"New member #{tag} has joined the clan!"
    return message, pings, tag

def screening():
    tag = clash.war_check()
    pings = 0
    if tag != "Not in war!":
        file = open("enemylist.txt", mode='r', encoding='utf-8')
        line = file.readline()
        line = line.strip("\n")
        line = line.split(",")
        file.close()
        if line[1] != tag:
            print(line[1])
            enemies_of_allah = clash.get_enemyclan(tag)
            enemies = clash.member_cleanup(enemies_of_allah)
            clash.enemylist_save(enemies)
            return message(99, tag)
        else:
            newtag = check_new()
            status = counter_espionage(newtag)
            if status == 1:
                return message(1, newtag)
            elif status == 2:
                return message(2, newtag)
            elif newtag != "0":
                return message(0, newtag)
            else:
                return 201, pings, tag
    else:
        newtag = check_new()
        status = counter_espionage(newtag)
        if status == 2:
            return (message(2, newtag))
        elif newtag != "0":
            return (message(0, newtag))
        else:
            return 202, pings, tag
        
def save_player_info():
    member_list = load_mem("memberslist.txt")
    delay = 5
    for mem in member_list:
        player_json = clash.load_player_json(mem[1])
        clash.save_player_json(player_json, mem[1])
        print(f"\n\nSaved {mem[0]}, {mem[1]}, Waiting {delay} seconds to load next member.\n\n")
        time.sleep(delay)
    return

def enemy_lineup():
    enemy_lineup = clash.get_enemywar()
    opponents = []
    for enemy in enemy_lineup['members']:
        opponents.append(f"{enemy['mapPosition']:<2}, TH{enemy['townhallLevel']}, {enemy['tag']:<10}, {enemy['name']:<15}")
    unsorted = True
    while unsorted:
        unsorted = False
        i = 0
        while i < len(opponents) - 1:
            opp1 = int(opponents[i].split(",")[0])
            opp2 = int(opponents[i + 1].split(",")[0])
            if opp1 > opp2:
                hold = opponents[i]
                opponents[i] = opponents[i + 1]
                opponents[i + 1] = hold
                unsorted = True
            i += 1
    opponent_lineup = "```#, Name, Tag, TH Level\n"
    for opp in opponents:
        opponent_lineup += f"{opp}\n"
    opponent_lineup += "```"
    return opponent_lineup

def list_mem():
    members = load_mem("memberslist.txt")
    memberlist = "```"
    for m in members:
        memberlist += f"{m[0]}, {m[1]}\n"
    memberlist += "```"
    return memberlist

def detailed_view(tag):
    tag = tag.replace("#", "")
    tag = tag.upper()
    player = clash.load_player_json(tag)
    player_info = "```\n"
    player_info += f"{player['name']}, {player['tag']}, Town Hall {player['townHallLevel']}, [Clan War Status: {player['warPreference']}]\n"
    player_info += f"Tags: "
    for tag in player['labels']:
        player_info += f"{tag['name']}, "
    player_info = player_info[:-2]
    player_info += "\n"
    heroes = player['heroes']
    for hero in heroes:
        if hero['village'] == "home":
            equip1 = hero['equipment'][0]
            equip2 = hero['equipment'][1]
            player_info += f"{hero['name']}: Level {hero['level']} [Lvl {equip1['level']} {equip1['name']}, Lvl {equip2['level']} {equip2['name']}]\n"
    player_info += "```"
    return player_info

def create_scout(clantag, mode):
    if mode == 0:
        enemy_lineup = clash.get_enemywar()
    elif mode == 1:
        enemy_lineup = clash.get_cwlwar(0)
    lineup = []
    for enemy in enemy_lineup['members']:
        player = []
        player.append(enemy['mapPosition'])
        player.append(enemy['townhallLevel'])
        player.append(enemy['tag'])
        player.append(enemy['name'])
        tag = enemy['tag'].replace("#", "")
        player_json = clash.load_player_json(tag)
        player.append(player_json['trophies'])
        heroes = player_json['heroes']
        for hero in heroes:
            if hero['village'] == "home":
                equip1 = hero['equipment'][0]
                equip2 = hero['equipment'][1]
                player.append(f"Lvl {equip1['level']} {equip1['name']}, Lvl {equip2['level']} {equip2['name']}")
        lineup.append(player)
    unsorted = True
    while unsorted:
        unsorted = False
        i = 0
        while i < len(lineup) - 1:
            opp1 = int(lineup[i][0])
            opp2 = int(lineup[i + 1][0])
            if opp1 > opp2:
                hold = lineup[i]
                lineup[i] = lineup[i + 1]
                lineup[i + 1] = hold
                unsorted = True
            i += 1
    map_pos = []
    town_hall = []
    player_tag = []
    player_name = []
    trophies = []
    army = []
    king_equips = []
    queen_equips = []
    warden_equips = []
    champion_equips = []
    for mem in lineup:
        army.append("")
        map_pos.append(mem[0])
        town_hall.append(mem[1])
        player_tag.append(mem[2])
        player_name.append(mem[3])
        trophies.append(mem[4])
        if len(mem) > 5:
            king_equips.append(mem[5])
        else:
            king_equips.append("")
        if len(mem) > 6:
            queen_equips.append(mem[6])
        else:
            queen_equips.append("")
        if len(mem) > 7:
            warden_equips.append(mem[7])
        else:
            warden_equips.append("")
        if len(mem) > 8:
            champion_equips.append(mem[8])
        else:
            champion_equips.append("")
    d = {
        "Map Position": map_pos,
        "Town Hall": town_hall,
        "Player Tag": player_tag,
        "Player Name": player_name,
        "Trophy Count": trophies,
        "Army Comp": army,
        "King Equipment": king_equips,
        "Queen Equipment": queen_equips,
        "Warden Equipment": warden_equips,
        "Champion Equipment": champion_equips,
    }
    with open("scout.json", "w") as outfile: 
        json.dump(d, outfile)

    df = pandas.read_json("scout.json")
    df.to_excel(f"scout_report_{clantag}.xlsx")
    print(f"Saved file as scout_report_{clantag}.xlsx")
    return
