import discord, requests, json, datetime, pytz, countrywrangler, logging, asyncio, calendar
from discord.interactions import Interaction
from discord.ext import tasks, commands
from pytz import timezone
from lib.dbconnector import DBConnector


class TaskHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dbConnector = DBConnector()
        self.executeScheduledTasks.start()

    async def cog_load(self):
        print("Scheduler loaded!")
        logging.info("Schedule/Task Handler loaded.")

    # Creates the Crab.Fit and Returns the API Response
    @staticmethod
    async def createCrabFit(
        title: str = "",
        minimumHour: int = 9,
        maximumHour: int = 22,
        localTz: str = "America/Los_Angeles",
        initDate: datetime = (datetime.datetime.today() + datetime.timedelta(days=1)),
    ) -> requests.Response:
        logging.debug("Beginning Crab.fit request build with title: '" + title + "'")
        logging.debug("Datetime.today() = " + str(datetime.datetime.today()))
        logging.debug(
            "today() + 1 = "
            + str(datetime.datetime.today() + datetime.timedelta(days=1))
        )
        logging.debug("Initial date parameter: " + str(initDate))

        # Build Crab.fit Information
        localTz = timezone(localTz)
        initDate = initDate.astimezone(localTz).replace(
            hour=minimumHour, minute=0, second=0, microsecond=0
        )
        logging.debug("Beginning iteration with date: " + str(initDate))
        timeIterative = initDate
        times = []
        for i in range(7):  # For each hour in the week
            timeIterative = initDate + datetime.timedelta(days=i)
            for i in range(maximumHour - minimumHour):
                times.append(
                    timeIterative.astimezone(datetime.timezone.utc).strftime(
                        "%H00-%d%m%Y"
                    )
                )
                timeIterative += datetime.timedelta(hours=1)

        # API Call for Crab.fit
        payload = json.dumps(
            {
                "name": f"{title} {initDate.strftime('%m/%d')}-{(initDate + datetime.timedelta(weeks=1)).strftime('%m/%d')}",
                "times": times,
                "timezone": str(localTz),
            }
        )
        logging.debug(
            "Sending Crab.fit API request with the following data: " + str(payload)
        )
        response = requests.request(
            "POST",
            "https://api.crab.fit/event",
            headers={"Content-Type": "application/json"},
            data=payload,
        )

        return response

    @tasks.loop(hours=1)
    async def executeScheduledTasks(self):
        midnightTimezones = [
            tz
            for tz in pytz.all_timezones_set
            if datetime.datetime.now().astimezone(timezone(tz)).hour == 0
        ]  # Creates a list of all timezones where it is currently midnight

        startOfWeek = (
            datetime.datetime.now().astimezone(timezone(midnightTimezones[0]))
            + datetime.timedelta(days=1)
        ).weekday()  # Gets the weekday (0-6) of the following day (Beginning of the Crab.fit)
        tasks = self.dbConnector.getTasks(midnightTimezones, startOfWeek)
        logging.info("Starting the following tasks: " + str(tasks))
        for task in tasks:
            res = await self.createCrabFit(
                title=task[4],
                minimumHour=task[5],
                maximumHour=task[6],
                localTz=task[7],
            )
            if res.ok:
                logging.debug(
                    "Successfully created Crab.fit for Task #"
                    + str(task[0])
                    + " with response "
                    + str(res)
                )

                initDate = datetime.datetime.now().astimezone(
                    timezone(task[7])
                ) + datetime.timedelta(days=1)

                embed = discord.Embed(
                    title=f"Schedule: {initDate.strftime('%m/%d')} - {(initDate + datetime.timedelta(days=6)).strftime('%m/%d')}",
                    url=f"https://crab.fit/{res.json()['id']}",
                    color=0x00FFFF,
                )
                embed.set_footer(
                    text="Enter your availability at the link above!",
                    icon_url="https://crab.fit/logo192.png",
                )
                rolePing = ""
                if task[3]:
                    rolePing = f"<@&{task[3]}>"
                await self.bot.get_channel(task[2]).send(
                    content=rolePing,
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
                await self.bot.get_channel(task[2]).send(embed=embed)

    # Waits until the nearest hour before starting the task loop
    @executeScheduledTasks.before_loop
    async def beforeTaskExecuter(self):
        await self.bot.wait_until_ready()
        secondsUntilSharpHour = (60 - datetime.datetime.now().minute) * 60
        await asyncio.sleep(secondsUntilSharpHour)
