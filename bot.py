import os
import discord
from discord import app_commands
from discord.ext import commands
import subprocess
import csv

# ⚠️ Replace with your bot token
TOKEN = "YOUR_REAL_BOT_TOKEN"

# Path to your console exe
EXE = "./calc_cli"

# --- Load tanks and weapons from CSV files ---
def read_names_from_csv(path):
    names = []
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.reader(f):
            if not row or row[0].strip().startswith('#'):  # skip empty/comment
                continue
            names.append(row[0].strip())
    return names

tanks = read_names_from_csv("tanks.txt")
weaps = read_names_from_csv("weapons.txt")

# Fixed choices (like your QComboBoxes)
armor_choices = [("0%", "0.0"), ("20%", "0.2"), ("40%", "0.4"),
                 ("50%", "0.5"), ("60%", "0.6"), ("75%", "0.75"), ("90%", "0.9"), ("100%", "1.0")]

# Range and angle are free numeric inputs; calc_cli turns them into bonuses:
#   range bonus = 40 * max(0, 1 - (d + 5) / 40)^1.5 %   (+32.74% at 0 m, 0 from 35 m)
#   angle bonus = 40 * cos(angle) %                    (0 deg = square to the side, 90 = head-on)

velocity_choices = [("-20%", "0.8"), ("0%", "1.0"),
                    ("+10%x", "1.1"), ("+20%", "1.2"), ("+30%", "1.3"), ("+75%", "1.75")]

# --- Discord bot setup ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await bot.tree.sync()   # 🌍 Global sync
    print("🌍 Commands synced globally")

@bot.tree.command(name="calculate", description="Kill probability calculator")
@app_commands.describe(
    tank="Tank name",
    weapon="Weapon name",
    armor="Armor fraction",
    range_m="Distance in metres (+32.7% at 0 m, falling to 0 at 35 m+)",
    velocity="Velocity modifier",
    angle="Hit angle in degrees: 0 = square to the side (+40%), 90 = head-on (default, +0%)",
)
@app_commands.choices(
    armor=[app_commands.Choice(name=n, value=v) for n, v in armor_choices],
    velocity=[app_commands.Choice(name=n, value=v) for n, v in velocity_choices],
)
async def calculate(interaction: discord.Interaction,
    tank: str, weapon: str, armor: str,
    range_m: app_commands.Range[float, 0.0, 200.0],
    velocity: str,
    angle: app_commands.Range[float, 0.0, 90.0] = 90.0):

    try:
        out = subprocess.check_output(
            [EXE, tank, weapon, armor, str(range_m), str(angle), velocity],
            text=True
        )
        if len(out) > 1900:  # Discord message limit ~2000
            out = out[:1900] + "\n..."
        await interaction.response.send_message(f"```\n{out}\n```")

    except subprocess.CalledProcessError as e:
        await interaction.response.send_message(
            f"Error running calculator:\n```\n{e}\n```",
            ephemeral=True
        )

# --- Autocomplete for tank ---
@calculate.autocomplete("tank")
async def tank_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=name, value=name)
        for name in tanks if current.lower() in name.lower()
    ][:25]  # Discord only allows 25 suggestions

# --- Autocomplete for weapon ---
@calculate.autocomplete("weapon")
async def weapon_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=name, value=name)
        for name in weaps if current.lower() in name.lower()
    ][:25]

bot.run(TOKEN)


