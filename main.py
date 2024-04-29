import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members =True

bot = commands.Bot(command_prefix='/', intents=intents)

riot_key = os.getenv("RIOT_KEY")
discord_key = os.getenv("DISCORD_KEY")

user_data = {}

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="/help"))
    synced = await bot.tree.sync()
    print(f"Synchronisation de {len(synced)} commandes")

@bot.tree.command(name="help", description="Afficher l'aide du bot TeamTracker")
async def helpme(interaction):
    await interaction.response.send_message(f"Aide TeamTracker \n\nCommandes : \n**/helpme ** : Afficher aide bot TT \n**/ping ** : Ping TT \n**/define @MentionDiscord NomUtilisateurRiot Region ** : Ajouter utilisateur discord dans TT \n**/display ** : Afficher utilisateur TT \n**/erase ** : Effacer mémoire TT \n**/stats @MentionDiscord ** : Afficher stats actuelles mention Discord ")

@bot.tree.command(name="ping", description="Effectuer un ping vers le bot TeamTracker")
async def ping(interaction):
  await interaction.response.send_message(f"TftTracker est bien opérationnel !")

@bot.tree.command(name="define", description="Ajouter un utilisateur Discord à TeamTracker")
async def define(interaction, member: discord.Member, riot_name: str, region: str, status: bool):
    user_data[member.id] = {"riot_name": riot_name, "region": region, "status": status}
    await interaction.response.send_message(f"{member.display_name} : Riot username = {riot_name}; Region = {region}; Status = {status}")

@bot.tree.command(name="display", description="Afficher les données de TeamTracker")
async def display(interaction):
    await interaction.response.send_message(user_data)

@bot.tree.command(name="erase", description="Effacer les données de TeamTracker (DEBUG)")
async def erase(interaction):
    global user_data
    await interaction.response.send_message(f"Mémoire effacée !")
    user_data = {}

@bot.tree.command(name="stats", description="Afficher les statistiques générales de la mention")
async def stats(interaction, member: discord.Member):
    if member.id in user_data:
        data = user_data[member.id]
        await interaction.response.send_message(f"Informations pour {member.display_name} : Nom d'utilisateur Riot = {data['riot_name']}, Région = {data['region']}")
    else:
        await interaction.response.send_message(f"Aucune information trouvée pour {member.display_name}. \nMerci de l'ajouter via la commande suivante : \n**!define @Mention NomUtilisateurRiot Region **")

bot.run(discord_key)

# ------------------------------------------------------------------------------------------

# Si les joueurs sont en game, alors afficher les datas de manière automatique sans commande