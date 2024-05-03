# IMPORT PKG
import discord
import os
import requests
from discord.ext import commands, tasks
from discord import File
from dotenv import load_dotenv
from easy_pil import Editor, load_image_async, Font
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import asyncio
import io

# PARAMS
load_dotenv()
intents = discord.Intents.default()
intents.members =True
bot = commands.Bot(command_prefix='/', intents=intents)

# KEYS
riot_key = os.getenv("RIOT_KEY")
discord_key = os.getenv("DISCORD_KEY")

# INIT DICTIONARIES
user_id = {}
user_secret = {}
user_data = {}
user_profile = {}

# ON BOT STARTUP, DO...
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="/help"))
    # autoTracker.start()
    synced = await bot.tree.sync()
    print(f"Synchronisation de {len(synced)} commandes")

# HELP CMD
@bot.tree.command(name="help", description="Afficher l'aide du bot TeamTracker")
async def helpme(interaction):
    try:
        await interaction.response.send_message(
                    f"Aide TeamTracker \n\nCommandes : \n"
                    "**/define** : Ajouter membre Discord dans TT \n"
                    "**/display** : Afficher utilisateur(s) TT \n"
                    "**/erase** : Effacer mémoire TT \n"
                    "**/game @** : Afficher les stats du joueur mentionné en partie \n"
                    "**/helpme** : Afficher aide bot TT \n"
                    "**/image @** : Afficher une carte personnalisée pour le membre \n"
                    "**/infos @** : Afficher stats actuelles mention Discord \n"
                    "**/infosdoubleup @** : Afficher stats DBup actuelles mention Discord \n"
                    "**/ingame** : Voir les joueurs en partie \n"
                    "**/ladder** : Afficher le classement des joueurs \n"
                    "**/matches @** : Afficher les détails de la dernière partie jouée par le joueur"
                    "**/ping** : Ping TT \n"
                    "**/showsecret** : Ping TT \n"
                )
    except:
        await interaction.response.send_message(f"Erreur lors de l'affichage de l'aide")

# PING CMD
@bot.tree.command(name="ping", description="Effectuer un ping vers le bot TeamTracker")
async def ping(interaction):
    try:
        await interaction.response.send_message(f"TftTracker est bien opérationnel !")
    except:
        await interaction.response.send_message(f"Erreur lors du ping")

# DEFINE CMD
@bot.tree.command(name="define", description="Ajouter un utilisateur Discord à TeamTracker")
async def define(interaction, member: discord.Member, riot_name: str, tag: str, region: str, status: bool):
    try:
        global user_secret
        if status != False:
            status = False
        user_data[member.id] = {"riot_name": riot_name, "tag": tag, "region": region, "status": status}
        try:
            puid = 'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/' + riot_name + "/" + tag + '?api_key=' + riot_key
            res = requests.get(puid, timeout = 127)
            user_secret[member.id] = [dict(res.json())]
        except:
            interaction.response.send_message(f"Erreur lors de la requete API pour user_secret")
        try:
            puid = user_secret[member.id][0]['puuid']
        except:
            interaction.response.send_message(f"Erreur lors de la manipulation du PUUID RIOT")
        try:
            id = 'https://euw1.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/' + puid + '?api_key=' + riot_key
            res2 = requests.get(id, timeout=127)
            user_id[member.id] = [dict(res2.json())]
        except:
            interaction.response.send_message(f"Erreur lors de la requete API pour user_id")
        try:
            username = member.name
            user_id[member.id][0]["discord_member"] = username
        except:
            interaction.response.send_message(f"Erreur lors de l'ajout du nom utilisateur Discord dans user_id")
        try:
            user_secret = {}
        except:
            interaction.response.send_message(f"Erreur lors de la suppression de la lib user_secret")
        try:
            await interaction.response.send_message(f"Id du membre Discord : {member.display_name} \nRiot username = {riot_name}\nTag = {tag}\nRegion = {region}\nStatus = {status}")
        except:
            interaction.response.send_message("Erreur lors de l'envoie du message de la commande define")
    except:
        interaction.response.send_message("Erreur majeure lors de l'ajout de la mention Discord")

# IMAGE CMD
@bot.tree.command(name="infos", description="Infos du joueur en Ranked Solo")
async def infos(interaction, member: discord.Member):
    id = user_id[member.id][0]['id']
    profile_data = 'https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/' + id + '?api_key=' + riot_key
    res = requests.get(profile_data, timeout=127)
    user_profile = res.json()
    for profile in user_profile:
        if profile["queueType"] == "RANKED_TFT":
            ranked_profile = profile
            break
    else:
        await interaction.response.send_message("Profil RANKED_TFT introuvable.")
        return

    totalGame = str(ranked_profile['wins'] + ranked_profile['losses'])
    winGame = str(ranked_profile['wins'])
    topGame = str(round(ranked_profile['wins'] / int(totalGame) * 100, 1)) + "%"

    label = ImageFont.truetype("./assets/fonts/Inter-ExtraBold.ttf", 15)
    userfont = ImageFont.truetype("./assets/fonts/Inter-ExtraBold.ttf", 25)
    descfont = ImageFont.truetype("./assets/fonts/Inter-ExtraBold.ttf", 25)
    banner = Editor("./assets/png/banner.png")
    tier = ""
    print()
    
    if ranked_profile['tier'].capitalize() == "Grandmaster":
        tier = "GrandMaster"
    else :
        tier = ranked_profile['tier'].capitalize()

    response = requests.get("https://ddragon.leagueoflegends.com/cdn/14.8.1/img/tft-regalia/TFT_Regalia_" + tier + ".png")
    image_data = Image.open(io.BytesIO(response.content))

    x_position_for_tier = 550
    y_position_for_tier = 150

    x_position_for_rank_lp = 720
    y_position_for_rank_lp = 150

    color_rank = ""
    
    if ranked_profile['tier'].capitalize() == "Iron":
        color_rank = "#582B0A"
        x_position_for_rank_lp = 620
    elif ranked_profile['tier'].capitalize() == "Bronze":
        color_rank = "#B64D01"
        x_position_for_rank_lp = 620
    elif ranked_profile['tier'].capitalize() == "Silver":
        color_rank = "#8A8A8A"
        x_position_for_rank_lp = 630
    elif ranked_profile['tier'].capitalize() == "Gold":
        color_rank = "#FFC700"
        x_position_for_rank_lp = 619
    elif ranked_profile['tier'].capitalize() == "Platinum":
        color_rank = "#2c7f8b"
        x_position_for_rank_lp = 665
    elif ranked_profile['tier'].capitalize() == "Emerald":
        color_rank = "#02E750"
        x_position_for_rank_lp = 657
    elif ranked_profile['tier'].capitalize() == "Diamond":
        color_rank = "#5E6EFF"
        x_position_for_rank_lp = 665
    elif ranked_profile['tier'].capitalize() == "Master":
        color_rank = "#B251D3"
        x_position_for_rank_lp = 643
    elif ranked_profile['tier'].capitalize() == "Grandmaster":
        color_rank = "#9e3836"
        x_position_for_rank_lp = 725
    elif ranked_profile['tier'].capitalize() == "Challenger":
        color_rank = "#226581"
        x_position_for_rank_lp = 695
    else:
        color_rank = "#fff"

    total_pos_x = 900
    win_pos_x = 1027
    top_pos_x = 1125

    if len(totalGame) == 1:
        total_pos_x = 918
    elif len(totalGame) == 2:
        total_pos_x = 900
    elif len(totalGame) == 3:
        total_pos_x = 892

    if len(winGame) == 1:
        win_pos_x = 1035
    elif len(winGame) == 2:
        win_pos_x = 1027
    elif len(winGame) == 3:
        win_pos_x = 1019

    if len(topGame) == 1:
        top_pos_x = 1133
    elif len(topGame) == 2:
        top_pos_x = 1125
    elif len(topGame) == 3:
        top_pos_x = 1117

    banner.ellipse((90, 70), width=120,height=120, fill=color_rank)

    new_width = 300
    new_height = 250
    resized_image = image_data.resize((new_width, new_height))
    image_position = (225, 0)
    banner.paste(resized_image, image_position)

    icon_url = requests.get("https://ddragon.leagueoflegends.com/cdn/14.8.1/img/profileicon/" + str(user_id[member.id][0]["profileIconId"]) + ".png")
    icon_data = Image.open(io.BytesIO(icon_url.content))
    new_width = 110
    new_height = 110
    resized_icon = icon_data.resize((new_width, new_height))

    mask = Image.new("L", (new_width, new_height), 0)
    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0, new_width, new_height), fill=255)
    resized_icon.putalpha(mask)

    image_position = (95, 75)
    banner.paste(resized_icon, image_position)

    banner.text((550,80), text=f"Ranked Solo", color="#A3A3A3", font=label)
    banner.text((550,100), text=f"{user_data[member.id]['riot_name']}#{user_data[member.id]['region']}", color="#ffffff", font=userfont)

    tier_text = ranked_profile['tier'].capitalize()
    rank_lp_text = f"{ranked_profile['rank']} {ranked_profile['leaguePoints']} LP"
    

    banner.text((x_position_for_tier, y_position_for_tier), text=tier_text, color=color_rank, font=userfont)
    banner.text((x_position_for_rank_lp, y_position_for_rank_lp), text=rank_lp_text, color="#ffffff", font=userfont)
    banner.text((total_pos_x, 110), text=totalGame, color="#D0D0D0", font=descfont)
    banner.text((win_pos_x, 110), text=winGame, color="#D0D0D0", font=descfont)
    banner.text((top_pos_x, 110), text=topGame, color="#D0D0D0", font=descfont)


    file = File(fp=banner.image_bytes, filename="pic.png")
    await interaction.response.send_message(file=file)

@bot.tree.command(name="infosdoubleup", description="Infos du joueur en Ranked DoubleUp")
async def infosdoubleup(interaction, member: discord.Member):
    id = user_id[member.id][0]['id']
    profile_data = 'https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/' + id + '?api_key=' + riot_key
    res = requests.get(profile_data, timeout=127)
    user_profile = res.json()
    for profile in user_profile:
        if profile["queueType"] == "RANKED_TFT_DOUBLE_UP":
            ranked_profile = profile
            break
    else:
        await interaction.response.send_message("Profil RANKED_TFT_DOUBLE_UP introuvable.")
        return
        
    totalGame = str(ranked_profile['wins'] + ranked_profile['losses'])
    winGame = str(ranked_profile['wins'])
    topGame = str(round(ranked_profile['wins'] / int(totalGame) * 100, 1)) + "%"

    label = ImageFont.truetype("./assets/fonts/Inter-ExtraBold.ttf", 15)
    userfont = ImageFont.truetype("./assets/fonts/Inter-ExtraBold.ttf", 25)
    descfont = ImageFont.truetype("./assets/fonts/Inter-ExtraBold.ttf", 25)
    banner = Editor("./assets/png/banner.png")
    tier = ""
    
    if ranked_profile['tier'].capitalize() == "Grandmaster":
        tier = "GrandMaster"
    else :
        tier = ranked_profile['tier'].capitalize()

    response = requests.get("https://ddragon.leagueoflegends.com/cdn/14.8.1/img/tft-regalia/TFT_Regalia_" + tier + ".png")
    image_data = Image.open(io.BytesIO(response.content))

    x_position_for_tier = 550
    y_position_for_tier = 150

    x_position_for_rank_lp = 720
    y_position_for_rank_lp = 150

    color_rank = ""
    
    if ranked_profile['tier'].capitalize() == "Iron":
        color_rank = "#582B0A"
        x_position_for_rank_lp = 620
    elif ranked_profile['tier'].capitalize() == "Bronze":
        color_rank = "#B64D01"
        x_position_for_rank_lp = 620
    elif ranked_profile['tier'].capitalize() == "Silver":
        color_rank = "#8A8A8A"
        x_position_for_rank_lp = 630
    elif ranked_profile['tier'].capitalize() == "Gold":
        color_rank = "#FFC700"
        x_position_for_rank_lp = 619
    elif ranked_profile['tier'].capitalize() == "Platinum":
        color_rank = "#2c7f8b"
        x_position_for_rank_lp = 665
    elif ranked_profile['tier'].capitalize() == "Emerald":
        color_rank = "#02E750"
        x_position_for_rank_lp = 657
    elif ranked_profile['tier'].capitalize() == "Diamond":
        color_rank = "#5E6EFF"
        x_position_for_rank_lp = 665
    elif ranked_profile['tier'].capitalize() == "Master":
        color_rank = "#B251D3"
        x_position_for_rank_lp = 643
    elif ranked_profile['tier'].capitalize() == "Grandmaster":
        color_rank = "#9e3836"
        x_position_for_rank_lp = 725
    elif ranked_profile['tier'].capitalize() == "Challenger":
        color_rank = "#9DF9FF"
        x_position_for_rank_lp = 695
    else:
        color_rank = "#fff"

    banner.ellipse((90, 70), width=120,height=120, fill=color_rank)

    total_pos_x = 900
    win_pos_x = 1027
    top_pos_x = 1125

    if len(totalGame) == 1:
        total_pos_x = 908
    elif len(totalGame) == 2:
        total_pos_x = 900
    elif len(totalGame) == 3:
        total_pos_x = 892

    if len(winGame) == 1:
        win_pos_x = 1035
    elif len(winGame) == 2:
        win_pos_x = 1027
    elif len(winGame) == 3:
        win_pos_x = 1019

    if len(topGame) == 1:
        top_pos_x = 1133
    elif len(topGame) == 2:
        top_pos_x = 1125
    elif len(topGame) == 3:
        top_pos_x = 1117

    new_width = 300
    new_height = 250
    resized_image = image_data.resize((new_width, new_height))
    image_position = (225, 0)
    banner.paste(resized_image, image_position)

    icon_url = requests.get("https://ddragon.leagueoflegends.com/cdn/14.8.1/img/profileicon/" + str(user_id[member.id][0]["profileIconId"]) + ".png")
    icon_data = Image.open(io.BytesIO(icon_url.content))
    new_width = 110
    new_height = 110
    resized_icon = icon_data.resize((new_width, new_height))

    mask = Image.new("L", (new_width, new_height), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, new_width, new_height), fill=255)
    resized_icon.putalpha(mask)

    image_position = (95, 75)
    banner.paste(resized_icon, image_position)

    banner.text((550,80), text=f"Ranked DoubleUp", color="#A3A3A3", font=label)
    banner.text((550,100), text=f"{user_data[member.id]['riot_name']}#{user_data[member.id]['region']}", color="#ffffff", font=userfont)

    tier_text = ranked_profile['tier'].capitalize()
    rank_lp_text = f"{ranked_profile['rank']} {ranked_profile['leaguePoints']} LP"


    banner.text((x_position_for_tier, y_position_for_tier), text=tier_text, color=color_rank, font=userfont)
    banner.text((x_position_for_rank_lp, y_position_for_rank_lp), text=rank_lp_text, color="#ffffff", font=userfont)
    banner.text((total_pos_x, 110), text=totalGame, color="#D0D0D0", font=descfont)
    banner.text((win_pos_x, 110), text=winGame, color="#D0D0D0", font=descfont)
    banner.text((top_pos_x, 110), text=topGame, color="#D0D0D0", font=descfont)


    file = File(fp=banner.image_bytes, filename="pic.png")
    await interaction.response.send_message(file=file)
    
# SHOWSECRET CMD
@bot.tree.command(name="showsecret", description="show")
async def showsecret(interaction):
    try:
        await interaction.response.send_message(user_secret)
    except:
        interaction.response.send_message(f"Erreur lors de l'affichage de user_secret")

# DISPLAY CMD
@bot.tree.command(name="display", description="Afficher les données de TftTracker")
async def display(interaction):
    try:
        await interaction.response.send_message(user_data)
    except:
        interaction.response.send_message("Erreur lors de l'affichage des données avec cmd display")

# ERASE CMD
@bot.tree.command(name="erase", description="Effacer les données de TeamTracker (DEBUG)")
async def erase(interaction):
    try:
        global user_data
        await interaction.response.send_message(f"Mémoire effacée !")
        user_data = {}
    except:
        interaction.response.send_message("Erreur lors de la suppresion de user_data")


# INGAME CMD
@bot.tree.command(name="ingame", description="Voir les joueurs ingame")
async def ingame(interaction):
    ladder = []
    players = []
    ingame = []
    compt = 0

    for user_key in user_id.keys():
        temp = []
        name = user_id[user_key][0]["discord_member"]
        puuid = user_id[user_key][0]["puuid"]

        temp.append(name)
        temp.append(puuid)
        players.append(temp)

    for player in players:
        current = 'https://euw1.api.riotgames.com/lol/spectator/tft/v5/active-games/by-puuid/' + player[1] + '?api_key=' + riot_key
        res = requests.get(current, timeout = 127)
        res = [dict(res.json())]

        try:
            message = res[0]['status']['message']
        except KeyError:
            message = res[0]['gameId']

        if message == "Data not found - spectator game info isn't found":
            ingame.append(player[0])
            ingame.append(False)
        else :
            ingame.append(player[0])
            ingame.append(True)
            compt += 1

    await interaction.response.send_message(ingame)

# LADDER CMD
@bot.tree.command(name="ladder", description="Classement des joueurs")
async def ladder(interaction):
    ladder = []
    compt = 0
    for user_key in user_id.keys():
        id = user_id[user_key][0]["id"]
        profile_data = 'https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/' + id + '?api_key=' + riot_key
        res = requests.get(profile_data, timeout=127)
        user_profile = res.json()

        temp = []
        temp.append(str(user_id[list(user_id.keys())[compt]][0]["discord_member"]).capitalize())
        temp.append(str(user_profile[len(user_profile) - 1]['tier']))
        temp.append(str(user_profile[len(user_profile) - 1]['rank']))
        temp.append(str(user_profile[len(user_profile) - 1]['leaguePoints']) + " LP")
        ladder.append(temp)
        compt += 1


    division_order = {'CHALLENGER': 10, 'GRANDMASTER': 9, 'MASTER': 8, 'DIAMOND': 7, 'EMERALD': 6, 'PLATINUM': 5, 'GOLD': 4, 'SILVER': 3, 'BRONZE': 2, 'IRON': 1}

    def custom_sort(player):
        division_rank = division_order.get(player[1], 0)
        division_level = {'I': 4, 'II': 3, 'III': 2, 'IV': 1}.get(player[2], 0)
        lp = int(player[3].split()[0])
        return (division_rank, division_level, lp)

    sorted_ladder = sorted(ladder, key=custom_sort, reverse=True)
    await interaction.response.send_message(sorted_ladder)

# @bot.tree.command(name="image", description="Afficher tous les joueurs de la partie")
# async def image(interaction, member: discord.Member):
#     puuid = user_id[member.id][0]['puuid']
#     current = f"https://euw1.api.riotgames.com/lol/spectator/tft/v5/active-games/by-puuid/{puuid}?api_key={riot_key}"


# GAME CMD
@bot.tree.command(name="game", description="Afficher les statistiques générales de la mention")
async def game(interaction, member: discord.Member):
    puuid = user_id[member.id][0]['puuid']
    current = f"https://euw1.api.riotgames.com/lol/spectator/tft/v5/active-games/by-puuid/{puuid}?api_key={riot_key}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(current) as response:
            res = await response.json()

        if 'status' in res:
            message = res['status'].get('message')
            if message:
                await interaction.response.send_message(f"{user_id[member.id][0]['discord_member'].capitalize()} n'est actuellement pas en game !")
        else:
            players_ingame = []
            tasks = []
            for participant in res['participants']:
                player_id = participant['summonerId']
                task = asyncio.create_task(get_player_info(session, riot_key, player_id))
                tasks.append(task)

            player_infos = await asyncio.gather(*tasks)

            for participant, info in zip(res['participants'], player_infos):
                temp = [
                    participant['riotId'],
                    info[len(info) - 1]['tier'],
                    info[len(info) - 1]['rank'],
                    f"{info[len(info) - 1]['leaguePoints']} LP"
                ]
                players_ingame.append(temp)

            label = ImageFont.truetype("./assets/fonts/Inter-ExtraBold.ttf", 15)
            game = Editor("./assets/png/game_summary.png")
            await interaction.response.send_message(players_ingame)


            # game.text((total_pos_x, 110), text=totalGame, color="#D0D0D0", font=descfont)
            

            # file = File(fp=game.image_bytes, filename="pic.png")
            # await interaction.response.send_message(file=file)

async def get_player_info(session, riot_key, player_id):
    url = f"https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/{player_id}?api_key={riot_key}"
    async with session.get(url) as response:
        return await response.json()

# MATCHES CMD
@bot.tree.command(name="matches", description="Afficher les détails de la dernière partie jouée par le joueur")
async def matches(interaction, member: discord.Member, last: int):
    puuid = user_id[member.id][0]['puuid']
    matches_url = f"https://europe.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start=0&count=10&api_key={riot_key}"

    async with aiohttp.ClientSession() as session:
        async with session.get(matches_url) as response:
            matches_array = await response.json()

    match_details_url = f"https://europe.api.riotgames.com/tft/match/v1/matches/{matches_array[last]}?api_key={riot_key}"

    async with aiohttp.ClientSession() as session:
        async with session.get(match_details_url) as response:
            match_details = await response.json()

    participant_data = get_participant_data(match_details, puuid)
    participant_info = extract_participant_info(participant_data)

    print(participant_info)
    # await interaction.response.send_message(participant_info)
    await interaction.response.send_message("Data trop longue ! Check ton terminal.")

def get_participant_data(data, puuid):
    for participant in data['info']['participants']:
        if participant['puuid'] == puuid:
            return participant
    return None

def extract_participant_info(participant_data):
    extracted_info = {
        "augments": participant_data["augments"],
        "level": participant_data["level"],
        "placement": participant_data["placement"],
        "traits": participant_data["traits"],
        "units": participant_data["units"]
    }
    return extracted_info


# @tasks.loop(seconds = 60)
# async def autoTracker():
#     print("autoTracker")


bot.run(discord_key)

# ------------------------------------------------------------------------------------------

# Si les joueurs sont en game, alors afficher les datas de manière automatique sans commandes