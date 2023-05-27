import discord, asyncio, dotenv, logging, os
from discord.ext import commands
from cogs.taskhandler import TaskHandler

dotenv.load_dotenv()

intents = discord.Intents.all()
intents.presences = False
intents.members = False
bot = commands.Bot(command_prefix="c!", intents=intents, status=discord.Status.idle)


@bot.event
async def on_ready():
    # await bot.tree.sync()  # Only run when changing or adding a slash command
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="with they crab",
        ),
        status=discord.Status.online,
    )
    print("Ready!")


async def main():
    discord.utils.setup_logging(
        handler=logging.FileHandler(filename="debug.log", encoding="utf-8", mode="w"),
        level=logging.DEBUG,
    )
    logging.basicConfig()
    await bot.add_cog(TaskHandler(bot))
    await bot.start(token=os.getenv("BOT_TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
