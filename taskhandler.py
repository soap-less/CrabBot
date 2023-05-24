import discord, requests, json, datetime, pytz, countrywrangler, logging, asyncio, calendar
from discord.interactions import Interaction
from discord.ext import tasks, commands
from discord import app_commands
from pytz import timezone
from dbconnector import DBConnector


class TaskHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dbConnector = DBConnector()
        self.executeScheduledTasks.start()

    async def cog_load(self):
        print("Scheduler loaded!")
        logging.info("Schedule/Task Handler loaded.")

    # Creates the Crab.Fit and Returns the API Response
    async def createCrabFit(
        self,
        title: str = "",
        minimumHour: int = 9,
        maximumHour: int = 22,
        localTz: str = "America/Los_Angeles",
    ):
        # Build Crab.fit Information
        localTz = timezone(localTz)
        initDate = datetime.datetime.today().astimezone(datetime.timezone.utc).replace(
            hour=minimumHour, minute=0, second=0, microsecond=0
        ) + datetime.timedelta(days=1)
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
                "event": {
                    "name": f"{title} {initDate.strftime('%m/%d')}-{(initDate + datetime.timedelta(weeks=1)).strftime('%m/%d')}",
                    "times": times,
                    "timezone": str(localTz),
                }
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
                    title=f"Schedule: {initDate.strftime('%m/%d')} - {(initDate + datetime.timedelta(weeks=1)).strftime('%m/%d')}",
                    url=f"https://crab.fit/{res.json()['id']}",
                    color=0x00FFFF,
                )
                embed.set_footer(
                    text="Enter your availability at the link above!",
                    icon_url="https://crab.fit/logo192.png",
                )
                await self.bot.get_channel(task[2]).send(
                    content=f"<@&{task[3]}>",
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

    @app_commands.command(
        name="new-schedule",
        description="Set up a new schedule for weekly crab.fits. You can set up multiple weekly schedules.",
    )
    @app_commands.describe(
        channel="The channel to post to. Default: this channel",
        title="The default crab.fit title. Default: server name.",
        minHour="Beginning of the range of valid times. Must be a number 0-23 (24-hour format). Default: 8 (8AM)",
        maxHour="End of the range of valid times. Must be a number 1-24 (24-hour format). Default: 24 (end of day)",
        startOfWeek="The weekday you want each crab.fit to start on. Default: Monday",
        roleToPing="The role to ping when sending a new crab.fit. Default: None",
    )
    @app_commands.rename(
        channel="channel",
        title="default-title",
        minHour="time-range-start",
        maxHour="time-range-end",
        startOfWeek="starting-weekday",
        roleToPing="role-to-ping",
    )
    @app_commands.choices(
        startOfWeek=[
            app_commands.Choice(name="Monday", value=0),
            app_commands.Choice(name="Tuesday", value=1),
            app_commands.Choice(name="Wednesday", value=2),
            app_commands.Choice(name="Thursday", value=3),
            app_commands.Choice(name="Friday", value=4),
            app_commands.Choice(name="Saturday", value=5),
            app_commands.Choice(name="Sunday", value=6),
        ]
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def newSchedule(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,
        roleToPing: discord.Role = None,
        title: str = None,
        minHour: int = 8,
        maxHour: int = 24,
        startOfWeek: app_commands.Choice[int] = 0,
    ):
        # Check if guild has too many tasks
        if self.dbConnector.isAtTaskLimit(interaction.guild_id):
            embed = discord.Embed(
                title="Limit reached!",
                description="This server already has too many schedules :c",
                color=0xFF4444,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Input Validation
        channelId: int = 0
        if channel:
            channelId = channel.id
        else:
            channelId = interaction.channel_id

        roleId: int = None
        if roleToPing:
            roleId = roleToPing.id

        if not title:  # Set default title if not given
            title = interaction.guild.name

        if (
            minHour >= maxHour
            or maxHour > 24
            or maxHour < 1
            or minHour > 23
            or minHour < 0
        ):
            await interaction.response.send_message(
                embed=discord.Embed(color=0xFF4444, title="Invalid time range."),
                description="Please ensure that the values are within the proper range and that the end of the time range is after the start.",
                ephemeral=True,
            )
            return  # If time range invalid, exit.

        embed = discord.Embed(
            title="Hey, one more thing!",
            description="I need to know your regional timezone. Let's start by filtering by country.",
            color=0xFFFF00,
        )
        embed.set_footer(
            text='Want to type it in manually? Hit "Skip Search" below and enter it AS SHOWN in crab.fit, case-sensitive.'
        )

        # UI View that handles Timezone Input
        # The Timezone Filter is composed of 2 buttons: the Manual Input and the Search.
        # The Manual Input button promts the user with a modal to manually input their timezone according to crab.fit.
        # The Search button prompts the user with a series of modals to help them find their most accurate timezone name.
        class TimezoneFilter(discord.ui.View):
            # Button + Logic for Manual Timezone Input
            class ManualInputHandler(discord.ui.Button):
                # User Input Prompt
                class ManualInputModal(discord.ui.Modal, title="Input timezone."):
                    def __init__(self, dbConnector):
                        self.dbConnector = dbConnector
                        super().__init__()

                    # Timezone Input Field
                    tz = discord.ui.TextInput(
                        label="Timezone as shown in Crab.fit",
                        style=discord.TextStyle.short,
                        min_length=3,
                        row=0,
                        default="America/Los_Angeles",
                        placeholder="Timezone (Case-Sensitive)",
                    )

                    # Set inputted timezone on Submit
                    async def on_submit(self, interaction: Interaction):
                        # Re-prompt while timezone entry is invalid
                        if self.tz.value not in pytz.all_timezones:
                            embed = discord.Embed(
                                title="Invalid timezone!",
                                description="Make sure it's the same as in Crab.fit, including capitalization.",
                                color=0xFF4444,
                            ).set_footer(
                                text='If you\'re not sure of how to find it, hit "Search by Country" to search for it.'
                            )
                            await interaction.response.send_message(
                                embed=embed, view=TimezoneFilter(), ephemeral=True
                            )
                        else:
                            rowId = self.dbConnector.addTask(
                                interaction.guild_id,
                                channelId,
                                roleId,
                                title,
                                minHour,
                                maxHour,
                                self.tz.value,
                                startOfWeek,
                            )

                            embed = discord.Embed(
                                color=0x44FF44,
                                title="New schedule created!",
                                description=f'A crab.fit titled "{title}" will be now posted weekly!!',
                            ).set_footer(
                                text="Task #" + str(rowId),
                                icon_url="https://crab.fit/logo192.png",
                            )

                            await interaction.response.edit_message(content=str(rowId))

                # Initialize Button
                def __init__(self, dbConnector):
                    self.dbConnector = dbConnector
                    super().__init__(label="Skip Search")

                # Open Input Modal On Button Press
                async def callback(self, interaction: Interaction):
                    await interaction.response.send_modal(
                        TimezoneFilter.ManualInputHandler.ManualInputModal(
                            self.dbConnector
                        )
                    )

            # Button + Logic for Timezone Search
            class SearchHandler(discord.ui.Button):
                def __init__(self, dbConnector):  # Initialize Button + Set Label
                    self.dbConnector = dbConnector
                    super().__init__(
                        label="Search by Country", style=discord.ButtonStyle.primary
                    )

                # User Country Prompt Object
                class CountrySearchModal(discord.ui.Modal, title="Search by Country"):
                    countryName = discord.ui.TextInput(
                        label="Country Name or Two-letter Abbreviation",
                        style=discord.TextStyle.short,
                        min_length=2,
                        row=0,
                        default="US",
                    )

                    def __init__(self, dbConnector):
                        self.dbConnector = dbConnector
                        super().__init__()

                    # On Country Prompt Submit
                    async def on_submit(self, interaction: Interaction):
                        countryCode = self.countryName.value
                        # Standardize input to 2-letter country code
                        if len(countryCode) == 2 or len(countryCode) == 3:
                            countryCode = countrywrangler.Normalize.code_to_alpha2(
                                text=self.countryName.value
                            )
                        else:
                            countryCode = countrywrangler.Normalize.name_to_alpha2(
                                text=self.countryName.value, use_fuzzy=True
                            )

                        # if input invalid then re-prompt
                        if not countryCode:
                            await interaction.sendModal(self.__class__())

                        # Create a list of all possible times in selected country
                        possibleTimezones = pytz.country_timezones[countryCode]
                        possibleTimes = []
                        now = datetime.datetime.now()
                        for tz in possibleTimezones:
                            nowAsTz = now.astimezone(timezone(tz)).replace(tzinfo=None)
                            if nowAsTz not in possibleTimes:
                                possibleTimes.append(nowAsTz)
                        possibleTimes.sort()

                        # Map possible times to Discord UI Select Options
                        possibleTimeChoices = list(
                            map(
                                lambda time: discord.SelectOption(
                                    label=time.strftime("%I:%M %p"),
                                    value=time.hour,
                                ),
                                possibleTimes,
                            )
                        )

                        # Object for Current Time Prompt
                        class CurrentTimeSelection(
                            discord.ui.View,
                        ):
                            def __init__(self, dbConnector):
                                self.dbConnector = dbConnector
                                super().__init__()

                            @discord.ui.select(
                                placeholder="Select your current time.",
                                options=possibleTimeChoices,
                            )
                            async def select_callback(
                                self,
                                interaction: discord.Interaction,
                                select: discord.ui.Select,
                            ):
                                # Gets timezones that match selected hour from possible timezones
                                finalTzOptions = [
                                    tz
                                    for tz in possibleTimezones
                                    if now.astimezone(timezone(tz)).hour
                                    == int(select.values[0])
                                ]

                                finalTzOptions = list(
                                    map(
                                        lambda tz: discord.SelectOption(
                                            label=tz,
                                            value=tz,
                                        ),
                                        finalTzOptions,
                                    )
                                )

                                class FinalTimezoneSelection(discord.ui.View):
                                    def __init__(self, dbConnector):
                                        self.dbConnector: DBConnector = dbConnector
                                        super().__init__()

                                    @discord.ui.select(
                                        placeholder="Select your timezone.",
                                        options=finalTzOptions,
                                    )
                                    async def select_callback(
                                        self,
                                        interaction: discord.Interaction,
                                        select: discord.ui.Select,
                                    ):
                                        rowId = self.dbConnector.addTask(
                                            interaction.guild_id,
                                            channelId,
                                            roleId,
                                            title,
                                            minHour,
                                            maxHour,
                                            select.values[0],
                                            startOfWeek,
                                        )

                                        embed = discord.Embed(
                                            color=0x44FF44,
                                            title="New schedule created!",
                                            description=f'A crab.fit titled "{title}" will be now posted every {calendar.day_name[(startOfWeek - 1)%7]}!',
                                        ).set_footer(
                                            text="Task #" + str(rowId),
                                            icon_url="https://crab.fit/logo192.png",
                                        )

                                        await interaction.response.send_message(
                                            embed=embed, ephemeral=True
                                        )

                                await interaction.response.send_message(
                                    view=FinalTimezoneSelection(self.dbConnector),
                                    ephemeral=True,
                                )

                        await interaction.response.send_message(
                            view=CurrentTimeSelection(self.dbConnector), ephemeral=True
                        )

                # Open the country search prompt on button press
                async def callback(self, interaction: Interaction):
                    await interaction.response.send_modal(
                        TimezoneFilter.SearchHandler.CountrySearchModal(
                            self.dbConnector
                        )
                    )

            # Add Handlers to UI View
            def __init__(self, dbConnector):
                self.dbConnector = dbConnector
                super().__init__()
                self.add_item(self.SearchHandler(self.dbConnector)).add_item(
                    self.ManualInputHandler(self.dbConnector)
                )

        await interaction.response.send_message(
            embed=embed, view=TimezoneFilter(self.dbConnector), ephemeral=True
        )

    @newSchedule.error
    async def newScheduleError(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            embed = discord.Embed(
                title="You can't do that!",
                description="Only a server admin can run this command.",
                color=0xFF4444,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            errorStr = (
                "```"
                + (str(error)[:1015] + "..." if len(str(error)) >= 1018 else str(error))
                + "```"
            )
            embed = discord.Embed(
                title="Sorry, something went wrong!",
                description="An error occurred.",
                color=0xFF4444,
            ).add_field(name=f"Error ({error.__class__})", value=errorStr)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            raise error
