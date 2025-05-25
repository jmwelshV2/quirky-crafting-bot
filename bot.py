import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
from craft import perform_crafting_check, item_names

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synced {len(synced)} commands.")
    except Exception as e:
        print(f"❌ Sync error: {e}")

@bot.tree.command(name="craft", description="Craft an item with modifiers and magical enhancements")
@app_commands.describe(
    attempts="Number of items to craft",
    item="Name of the item to craft",
    bonus="Crafting bonus modifier",
    adv="Advantage: adv, dis, or none",
    magic="Magical item used")
@app_commands.choices(magic=[
    app_commands.Choice(name="None", value="none"),
    app_commands.Choice(name="Forgekeeper's Spark", value="Forgekeeper's Spark")
])
async def craft(
    interaction: discord.Interaction,
    attempts: app_commands.Range[int, 1, 20] = 1,
    item: str = "",
    bonus: int = 0,
    adv: str = "none",
    magic: str = "none"
):
    if adv not in ["adv", "dis", "none"]:
        await interaction.response.send_message("❌ Advantage must be one of: `adv`, `dis`, or `none`.", ephemeral=True)
        return

    results = []
    for _ in range(attempts):
        result = perform_crafting_check(item, bonus, adv, magic)
        results.append(result)

    await interaction.response.send_message("\n\n".join(results))

@craft.autocomplete("item")
async def item_autocomplete(interaction: discord.Interaction, current: str):
    matches = [app_commands.Choice(name=name, value=name) for name in item_names if current.lower() in name.lower()][:25]
    return matches

bot.run(os.getenv("DISCORD_TOKEN"))
