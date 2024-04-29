import discord
import os
import requests
from discord.ext import commands, tasks
from discord import File
from dotenv import load_dotenv
from easy_pil import Editor, load_image_async, Font

load_dotenv()

intents = discord.Intents.default()
intents.members =True

bot = commands.Bot(command_prefix='/', intents=intents)

riot_key = os.getenv("RIOT_KEY")
discord_key = os.getenv("DISCORD_KEY")

user_id = {}
user_secret = {}
user_data = {}
user_profile = {}

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="/help"))
    # autoTracker.start()
    synced = await bot.tree.sync()
    print(f"Synchronisation de {len(synced)} commandes")

@bot.tree.command(name="help", description="Afficher l'aide du bot TeamTracker")
async def helpme(interaction):
    await interaction.response.send_message(f"Aide TeamTracker \n\nCommandes : \n**/helpme ** : Afficher aide bot TT \n**/ping ** : Ping TT \n**/define ** : Ajouter utilisateur discord dans TT \n**/display ** : Afficher utilisateur TT \n**/erase ** : Effacer mémoire TT \n**/infos** : Afficher stats actuelles mention Discord ")

@bot.tree.command(name="ping", description="Effectuer un ping vers le bot TeamTracker")
async def ping(interaction):
  await interaction.response.send_message(f"TftTracker est bien opérationnel !")

@bot.tree.command(name="image", description="Image")
async def image(interaction, member: discord.Member):
    background = Editor("./fond.png")
    background.ellipse((325, 90), 150, 150, outline="black", stroke_width=5)
    background.text((10,10), text=member.name)
    file = File(fp=background.image_bytes, filename="pic.png")
    await interaction.response.send_message(file=file)

@bot.tree.command(name="define", description="Ajouter un utilisateur Discord à TeamTracker")
async def define(interaction, member: discord.Member, riot_name: str, tag: str, region: str, status: bool):
    global user_secret
    user_data[member.id] = {"riot_name": riot_name, "tag": tag, "region": region, "status": status}
    puid = 'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/' + riot_name + "/" + tag + '?api_key=' + riot_key
    res = requests.get(puid, timeout = 127)
    user_secret[member.id] = [dict(res.json())]
    puid = user_secret[member.id][0]['puuid']
    id = 'https://euw1.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/' + puid + '?api_key=' + riot_key
    res2 = requests.get(id, timeout=127)
    user_id[member.id] = [dict(res2.json())]
    username = member.name
    user_id[member.id][0]["discord_member"] = username
    user_secret = {}
    await interaction.response.send_message(f"Id du membre Discord : {member.display_name} \nRiot username = {riot_name}\nTag = {tag}\nRegion = {region}\nStatus = {status}")

@bot.tree.command(name="showsecret", description="show")
async def showsecret(interaction):
    await interaction.response.send_message(user_secret)

@bot.tree.command(name="display", description="Afficher les données de TeamTracker")
async def display(interaction):
    await interaction.response.send_message(user_data)

@bot.tree.command(name="erase", description="Effacer les données de TeamTracker (DEBUG)")
async def erase(interaction):
    global user_data
    await interaction.response.send_message(f"Mémoire effacée !")
    user_data = {}

@bot.tree.command(name="infos", description="Afficher les statistiques générales de la mention")
async def infos(interaction, member: discord.Member):
    id = user_id[member.id][0]['id']
    profile_data = 'https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/' + id + '?api_key=' + riot_key
    res = requests.get(profile_data, timeout=127)
    user_profile = res.json()
    for item in user_profile:
        temp_dict = {
            "queueType": item["queueType"],
            "tier": item["tier"],
            "rank": item["rank"],
            "leaguePoints": item["leaguePoints"],
            "wins": item["wins"],
            "losses": item["losses"]
        }
    await interaction.response.send_message(temp_dict)

@bot.tree.command(name="infosdoubleup", description="Afficher les statistiques générales de la mention")
async def infosdoubleup(interaction, member: discord.Member):
    id = user_id[member.id][0]['id']
    profile_data = 'https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/' + id + '?api_key=' + riot_key
    res = requests.get(profile_data, timeout=127)
    user_profile = res.json()
    for item in user_profile:
        temp_dict = {
            "queueType": item["queueType"],
            "tier": item["tier"],
            "rank": item["rank"],
            "leaguePoints": item["leaguePoints"],
            "wins": item["wins"],
            "losses": item["losses"]
        }
        await interaction.response.send_message(temp_dict)

# @bot.tree.command(name="ingame", description="Voir les joueurs ingame")
# async def ingame(interaction):
#     ladder = []
#     for i in range(len(user_id)):
#         temp = []
#         temp.append([user_id[i]['summon']])

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
        temp.append(user_profile[1]['tier'])
        temp.append(user_profile[1]['rank'])
        temp.append(user_profile[1]['leaguePoints'])
        ladder.append(temp)
        compt += 1

    await interaction.response.send_message(ladder)


# @tasks.loop(seconds = 60)
# async def autoTracker():
#     print("autoTracker")


bot.run(discord_key)

# ------------------------------------------------------------------------------------------

# Si les joueurs sont en game, alors afficher les datas de manière automatique sans commande