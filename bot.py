import os
import csv
import subprocess
import discord
import io
import barlen
from PIL import Image
from discord import app_commands
from discord.ext import commands

# ====== CONFIG ======
DEV_GUILD_ID = 1059186847827370134  # <-- put YOUR server ID (integer)
TOKEN = os.environ.get("DISCORD_TOKEN", "YOUR_REAL_BOT_TOKEN")  # set DISCORD_TOKEN, or paste the token here on the server
EXE = "./calc_cli"                 # Linux binary in same folder
# ====================

# --- load names from CSV-like files (first column = name) ---
def read_names_from_csv(path: str):
    names = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if not row or row[0].strip().startswith("#"):
                continue
            names.append(row[0].strip())
    return names

tanks = read_names_from_csv("tanks.txt")
weaps = read_names_from_csv("weapons.txt")
print(f"Loaded {len(tanks)} tanks, {len(weaps)} weapons")

# Fixed choices (schema-level; these DO require re-sync)
armor_choices = [("0%", "0.0"), ("20%", "0.2"), ("40%", "0.4"),
                 ("50%", "0.5"), ("60%", "0.6"), ("75%", "0.75"),
                 ("90%", "0.9"), ("100%", "1.0")]

# Range and angle are free numeric inputs; calc_cli turns them into bonuses:
#   range bonus = 40 * max(0, 1 - (d + 5) / 40)^1.5 %   (+32.74% at 0 m, 0 from 35 m)
#   angle bonus = 40 * cos(angle) %                    (0 deg = square to the side, 90 = head-on)

velocity_choices = [("-20%", "0.8"), ("0%", "1.0"),
                    ("+10%", "1.1"), ("+20%", "1.2"),
                    ("+30%", "1.3"), ("+75%", "1.75")]

# --- discord bot ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------- COMMAND --------------------
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
async def calculate(
    interaction: discord.Interaction,
    tank: str,
    weapon: str,
    armor: str,
    range_m: app_commands.Range[float, 0.0, 200.0],
    velocity: str,
    angle: app_commands.Range[float, 0.0, 90.0] = 90.0,
):
    try:
        out = subprocess.check_output(
            [EXE, tank, weapon, armor, str(range_m), str(angle), velocity],
            text=True,
        )
        if len(out) > 1900:
            out = out[:1900] + "\n..."
        await interaction.response.send_message(f"```\n{out}\n```")
    except subprocess.CalledProcessError as e:
        await interaction.response.send_message(
            f"Error running calculator:\n```\n{e}\n```",
            ephemeral=True,
        )

# --------- AUTOCOMPLETE (runtime; should fire while typing) ---------
@calculate.autocomplete("tank")
async def tank_autocomplete(interaction: discord.Interaction, current: str):
    print("tank_autocomplete called with:", repr(current))
    pool = tanks or []
    subset = pool if not current else [n for n in pool if current.lower() in n.lower()]
    return [app_commands.Choice(name=n, value=n) for n in subset[:25]]

@calculate.autocomplete("weapon")
async def weapon_autocomplete(interaction: discord.Interaction, current: str):
    print("weapon_autocomplete called with:", repr(current))
    pool = weaps or []
    subset = pool if not current else [n for n in pool if current.lower() in n.lower()]
    return [app_commands.Choice(name=n, value=n) for n in subset[:25]]

# -------------------- SYNC (guild-only, fresh) --------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    guild = discord.Object(id=DEV_GUILD_ID)
    try:
        bot.tree.clear_commands(guild=guild)
        await bot.tree.sync(guild=guild)
        print("🧹 Guild commands removed")
        # Push the current command schema (new range_m / angle options) globally.
        synced = await bot.tree.sync()
        print(f"🌍 Synced {len(synced)} global commands")
    except Exception as e:
        print("Sync error:", e)
MAX_IMAGE_BYTES = 8 * 1024 * 1024
 
 
@bot.tree.command(name="progress", description="Read a progress bar from a screenshot")
@app_commands.describe(
    image="Screenshot cropped to the bar",
    horizontal="Bar runs left-to-right instead of top-to-bottom",
    check="Attach an annotated image showing what was measured",
)
async def progress(interaction: discord.Interaction,
                   image: discord.Attachment,
                   horizontal: bool = False,
                   check: bool = True):
 
    if not (image.content_type or "").startswith("image/"):
        await interaction.response.send_message(
            "That attachment is not an image.", ephemeral=True)
        return
 
    if image.size > MAX_IMAGE_BYTES:
        await interaction.response.send_message(
            f"Image is too large ({image.size / 1e6:.1f} MB).", ephemeral=True)
        return
 
    # Downloading the attachment is network I/O and can exceed Discord's
    # 3-second window, so acknowledge the interaction first.
    await interaction.response.defer()
 
    try:
        raw = await image.read()
        img = Image.open(io.BytesIO(raw))
        pct, annotated, info = barlen.measure(img, horizontal=horizontal)
    except ValueError as e:
        await interaction.followup.send(f"Could not read a bar: {e}", ephemeral=True)
        return
    except Exception as e:
        await interaction.followup.send(
            f"Failed to process that image: {type(e).__name__}: {e}", ephemeral=True)
        return
 
    text = f"**{pct:.1f}%**  ({info['length']:.0f} px bar)"
 
    if not check:
        await interaction.followup.send(text)
        return
 
    buf = io.BytesIO()
    annotated.save(buf, format="PNG")
    buf.seek(0)
    await interaction.followup.send(text, file=discord.File(buf, filename="checked.png"))
    
bot.run(TOKEN)
