import os
import discord
from discord import app_commands
from discord.ext import commands
import subprocess
import csv

# ⚠️ Replace with your bot token
TOKEN = os.environ.get("DISCORD_TOKEN")

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
                 ("50%", "0.5"), ("75%", "0.75"), ("100%", "1.0")]

range_choices = [("5m (+25%)", "0.25"), ("10m (+20%)", "0.20"),
                 ("20m (+10%)", "0.10"), ("30m+ (0%)", "0.0")]

angle_choices = [("75° (+40%)", "0.40"), ("45° (+30%)", "0.30"),
                 ("Front (0%)", "0.0")]

velocity_choices = [("0.5x", "0.5"), ("1.0x", "1.0"),
                    ("1.5x", "1.5"), ("2.0x", "2.0")]

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
    rbonus="Range bonus",
    abonus="Angle bonus",
    velocity="Velocity modifier"
)
@app_commands.choices(
    armor=[app_commands.Choice(name=n, value=v) for n, v in armor_choices],
    rbonus=[app_commands.Choice(name=n, value=v) for n, v in range_choices],
    abonus=[app_commands.Choice(name=n, value=v) for n, v in angle_choices],
    velocity=[app_commands.Choice(name=n, value=v) for n, v in velocity_choices],
)
async def calculate(interaction: discord.Interaction,
    tank: str, weapon: str, armor: str, rbonus: str, abonus: str, velocity: str):

    try:
        out = subprocess.check_output(
            [EXE, tank, weapon, armor, rbonus, abonus, velocity],
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
