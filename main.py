import discord
import os
import requests
from discord.ext import commands, tasks
from dotenv import load_dotenv

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
    try:
        await interaction.response.send_message(f"Aide TeamTracker \n\nCommandes : \n**/helpme ** : Afficher aide bot TT \n**/ping ** : Ping TT \n**/define ** : Ajouter utilisateur discord dans TT \n**/display ** : Afficher utilisateur TT \n**/erase ** : Effacer mémoire TT \n**/infos** : Afficher stats actuelles mention Discord ")
    except:
        await interaction.response.send_message(f"Erreur lors de l'affichage de l'aide")

@bot.tree.command(name="ping", description="Effectuer un ping vers le bot TeamTracker")
async def ping(interaction):
    try:
        await interaction.response.send_message(f"TftTracker est bien opérationnel !")
    except:
        await interaction.response.send_message(f"Erreur lors du ping")

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

@bot.tree.command(name="showsecret", description="show")
async def showsecret(interaction):
    try:
        await interaction.response.send_message(user_secret)
    except:
        interaction.response.send_message(f"Erreur lors de l'affichage de user_secret")

@bot.tree.command(name="display", description="Afficher les données de TftTracker")
async def display(interaction):
    try:
        await interaction.response.send_message(user_data)
    except:
        interaction.response.send_message("Erreur lors de l'affichage des données avec cmd display")

@bot.tree.command(name="erase", description="Effacer les données de TeamTracker (DEBUG)")
async def erase(interaction):
    try:
        global user_data
        await interaction.response.send_message(f"Mémoire effacée !")
        user_data = {}
    except:
        interaction.response.send_message("Erreur lors de la suppresion de user_data")

@bot.tree.command(name="infos", description="Afficher les statistiques générales de la mention")
async def infos(interaction, member: discord.Member):
    try:
        try:
            id = user_id[member.id][0]['id']
        except:
            interaction.response.send_message(f"Erreur lors de la définition de l'ID")
        try:
            profile_data = 'https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/' + id + '?api_key=' + riot_key
            res = requests.get(profile_data, timeout=127)
            user_profile = res.json()
        except:
            interaction.response.send_message(f"Erreur lors de la requete API pour la récupération et/ou l'affichage des infos")
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
    except:
        interaction.response.send_message(f"Erreur de récupération et/ou affichage infos joueur")

@bot.tree.command(name="infosdoubleup", description="Afficher les statistiques générales de la mention")
async def infosdoubleup(interaction, member: discord.Member):
    try:
        try:
            id = user_id[member.id][0]['id']
        except:
            interaction.response.send_message(f"Erreur lors de la définition de l'ID")
        try:
            profile_data = 'https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/' + id + '?api_key=' + riot_key
            res = requests.get(profile_data, timeout=127)
            user_profile = res.json()
        except:
            interaction.response.send_message(f"Erreur lors de la requete API pour la récupération et/ou l'affichage des infos")
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
    except:
        interaction.response.send_message(f"Erreur de récupération et/ou affichage infos joueur")


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
        temp.append(str(user_profile[-1]['tier']))
        temp.append(str(user_profile[-1]['rank']))
        temp.append(str(user_profile[-1]['leaguePoints']) + " LP")
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


# @tasks.loop(seconds = 60)
# async def autoTracker():
#     print("autoTracker")


bot.run(discord_key)

# ------------------------------------------------------------------------------------------

# Si les joueurs sont en game, alors afficher les datas de manière automatique sans commandes