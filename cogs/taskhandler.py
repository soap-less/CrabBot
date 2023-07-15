import discord, datetime, pytz, logging, asyncio
from discord.ext import tasks, commands
from pytz import timezone
from lib.dbconnector import DBConnector, Task
import lib.utils


class TaskHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dbConnector = DBConnector()
        self.executeScheduledTasks.start()

    async def cog_load(self):
        print("Scheduler loaded!")
        logging.info("Schedule/Task Handler loaded.")

    # Returns the tasks in the current hour that need to be executed
    # Takes now(datetime.now()) as a parameter to ensure the same hour is used all the way through
    async def getCurrentTasks(self, now: datetime.datetime) -> list[Task]:
        # Creates a list of all midnight timezones in a dict where the key = tomorrow's weekday(start of cr.fit week) as an int (0-6)
        # This is done to handle cases where its midnight on opposite sides of the tz line
        # { int: tz[] }
        logging.debug("Beginning task fetch...")
        tomorrow = now + datetime.timedelta(days=1)
        midnightTzByWeekday = {}
        for tz in pytz.all_timezones_set:
            tommorrowAsTz = tomorrow.astimezone(timezone(tz))
            if tommorrowAsTz.hour == 0:
                logging.debug("Adding timezone: " + tz)
                if tommorrowAsTz.weekday() in midnightTzByWeekday.keys():
                    midnightTzByWeekday[tommorrowAsTz.weekday()].append(tz)
                else:
                    midnightTzByWeekday[tommorrowAsTz.weekday()] = [tz]
        logging.debug("Current Midnight Timezones: " + str(midnightTzByWeekday))

        tasks = []  # Get tasks from timezones
        for key in midnightTzByWeekday.keys():
            tasks += self.dbConnector.getTasks(midnightTzByWeekday[key], key)
        return tasks

    @tasks.loop(hours=1)
    async def executeScheduledTasks(self):
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)
        tasks = await self.getCurrentTasks(today)

        logging.info("Starting the following tasks: " + str(tasks))
        for task in tasks:
            startDate = tomorrow.astimezone(timezone(task.timezone))
            endDate = startDate + datetime.timedelta(days=6)

            res = await lib.utils.createCrabFit(
                title=task.title,
                minimumHour=task.minHour,
                maximumHour=task.maxHour,
                localTz=task.timezone,
                initDate=startDate,
            )
            if res.ok:
                logging.debug(
                    "Successfully created Crab.fit for Task #"
                    + str(task.id)
                    + " with response "
                    + str(res)
                )

                embed = discord.Embed(
                    title=f"Schedule: {startDate.strftime('%m/%d')} - {endDate.strftime('%m/%d')}",
                    url=f"https://crab.fit/{res.json()['id']}",
                    color=0x00FFFF,
                )
                embed.set_footer(
                    text="Enter your availability at the link above!",
                    icon_url="https://crab.fit/logo192.png",
                )
                await self.bot.get_channel(task.channelId).send(
                    content=f"<@&{task.roleId}>" if task.roleId else "",
                    embed=embed,
                )

            else:
                logging.error(
                    "Crab.fit API call failed! Here is the response "
                    + str(res)
                    + ": \n"
                    + res.text
                )

                embed = discord.Embed(
                    title="Something went wrong making the crab.fit.",
                    description="Crab.fit servers are most likely down.",
                    color=0xFF4444,
                )

                resText = res.text
                if len(resText) > 1000:
                    resText = resText[:1000] + "..."

                embed.add_field(name="Full Error:", value="```" + resText + "```")
                await self.bot.get_channel(task.channelId).send(embed=embed)

        logging.info("Finished tasks:" + str(tasks))

    # Waits until the nearest hour before starting the task loop
    @executeScheduledTasks.before_loop
    async def beforeTaskExecuter(self):
        await self.bot.wait_until_ready()
        secondsUntilSharpHour = (60 - datetime.datetime.now().minute) * 60
        await asyncio.sleep(secondsUntilSharpHour)
