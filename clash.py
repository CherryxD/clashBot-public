import requests 
import json 
from dotenv import load_dotenv
import os

load_dotenv()

headers = {
    'authorization': 'Bearer ' + os.getenv('CLASH_KEY'),
    'Accept': 'application/json'
}

def get_clan():
    response = requests.get('https://api.clashofclans.com/v1/clans/%23GQ29JVYY/members', headers=headers)
    clan_json = response.json()
    return clan_json

def get_feeder():
    response = requests.get('https://api.clashofclans.com/v1/clans/%232GJURLYYR/members', headers=headers)
    clan_json = response.json()
    return clan_json

def war_check():
    enemy = requests.get('https://api.clashofclans.com/v1/clans/%23GQ29JVYY/currentwar', headers=headers)
    enemy_json = enemy.json()
    war_status = str(enemy_json.get("state"))
    if war_status == 'notInWar':
        return "Not in war!"
    else:
        enemy_info = enemy_json.get("opponent")
        enemy_tag = enemy_info.get("tag")
        enemy_tag = str(enemy_tag)
        enemy_tag = enemy_tag[1 - len(enemy_tag):]
        return enemy_tag

def get_enemyclan(tag):
    enemy_clan = requests.get(f'https://api.clashofclans.com/v1/clans/%23{tag}/members', headers=headers)
    enemy_json = enemy_clan.json()
    return enemy_json

def get_clanname(tag):
    response = requests.get(f'https://api.clashofclans.com/v1/clans/%23{tag}', headers=headers)
    response_json = response.json()
    return response_json['name']

def get_enemywar():
    response = requests.get(f'https://api.clashofclans.com/v1/clans/%23GQ29JVYY/currentwar', headers=headers)
    full_lineup = response.json()
    enemy_lineup = full_lineup['opponent']
    return enemy_lineup

def get_cwlwar():
    response = requests.get(f'https://api.clashofclans.com/v1/clans/%23GQ29JVYY/currentwar/leaguegroup', headers=headers)
    data = response.json()
    war_tags = data['rounds']
    i = 0
    for tag in war_tags:
        if '#0' not in tag['warTags']:
            i += 1
    for war in war_tags[i - 1]['warTags']:
        war_tag = war.replace("#", "")
        lineup = requests.get(f'https://api.clashofclans.com/v1/clanwarleagues/wars/%23{war_tag}', headers=headers)
        lineup = lineup.json()
        if lineup['clan']['tag'] == "#GQ29JVYY":
            return lineup['opponent'], lineup['opponent']['tag']
        elif lineup['opponent']['tag'] == "#GQ29JVYY":
            return lineup['clan'], lineup['clan']['tag']
    return

def member_cleanup(clan_info):
    members_detailed = list(clan_info.get("items"))
    members_detailed = str(members_detailed)
    members_detailed = members_detailed.split('}}, {')

    members = []
    for member_info in members_detailed:

        # data cleanup
        member_info = member_info[:member_info.index('role') - 3]
        member_info = member_info[1 - len(member_info):]
        member_info = member_info.split(",")
        # cleanup tag
        tag = member_info[0]
        tag = tag[:len(tag) - 1]
        tag = tag[8 - tag.index("tag"):]
        # cleanup name
        name = member_info[1]
        name = name[:len(name) - 1]
        name = name[12 - name.index("name"):]
        # add to memberslist
        member = []
        member.append(name)
        member.append(tag)
        members.append(member)
        #print(members)

    # the first tag is always fucked
    hold = members[0][1]
    hold = hold[4 - len(hold):]
    members[0][1] = hold
    return members

def memberlist_save(members):
    file = open("memberslist.txt", mode='w', encoding='utf-8')
    for mem in members:
        line = mem[0] + "," + mem[1] + "\n"
        file.write(line)
    file.close()
    return

def feederlist_save(members):
    file = open("feederlist.txt", mode='w', encoding='utf-8')
    for mem in members:
        line = mem[0] + "," + mem[1] + "\n"
        file.write(line)
    file.close()
    return

def enemylist_save(enemies):
    file = open("enemylist.txt", mode='w', encoding='utf-8')
    file.write("Enemy clan," + war_check() + '\n')
    for enemy in enemies:
        line = enemy[0] + ',' + enemy[1] + '\n'
        file.write(line)
    file.close()
    return 

def blacklist_save(blacklisted):
    file = open("blacklist.txt", mode='a', encoding='utf-8')
    file.write(f"{blacklisted}\n")
    file.close()
    return

def blacklist_update(removed):
    found = False
    with open("blacklist.txt", "r") as f:
        lines = f.readlines()
    with open("blacklist.txt", "w") as f:
        for line in lines:
            if (line.strip("\n").split(","))[1] != removed:
                f.write(line)
            else:
                found = True
    return found

def validtag(info):
    info = info.split(",")
    if len(info) != 2:
        return False
    else: 
        return True 
    
def load_player_json(tag):
    response = requests.get(f"https://api.clashofclans.com/v1/players/%23{tag}", headers=headers)
    if response.status_code == 400:
        return "fake"
    # i hate cleanup
    player_json = response.json()
    player_json.pop('defenseWins')
    player_json.pop('bestBuilderBaseTrophies')
    if 'builderHallLevel' in player_json:
        player_json.pop('builderHallLevel')
        player_json.pop('builderBaseLeague')
    player_json.pop('builderBaseTrophies')
    if 'role' in player_json:
        player_json.pop('role')
    player_json.pop('achievements')
    if 'playerHouse' in player_json:
        player_json.pop('playerHouse')
    player_json['clan'].pop('badgeUrls')
    if 'league' in player_json:
        player_json['league'].pop('id')
        player_json['league'].pop('iconUrls')
    if 'label' in player_json:
        for label in player_json['labels']:
            label.pop('id')
            label.pop('iconUrls')
    return player_json

def save_player_json(player_json, tag):
    file = open(f"player_info_{tag}.txt", "w")
    json.dump(player_json, file, ensure_ascii=False, indent=4)
    return 
