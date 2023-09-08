import sqlite3, os, pytz
from typing import Union


class Task:
    id: int
    guildId: int
    channelId: int
    roleId: Union[int, None]
    title: str
    minHour: int
    maxHour: int
    timezone: str
    startOfWeek: int

    def __init__(
        self,
        id: int,
        guildId: int,
        channelId: int,
        roleId: Union[int, None],
        title: str,
        minHour: int,
        maxHour: int,
        timezone: str,
        startOfWeek: int,
    ) -> None:
        self.id = id
        self.guildId = guildId
        self.channelId = channelId
        self.roleId = roleId
        self.title = title
        self.minHour = minHour
        self.maxHour = maxHour
        self.timezone = timezone
        self.startOfWeek = startOfWeek

    # Mostly for Test Cases
    def __eq__(self, other):
        if isinstance(other, Task):
            return False not in [
                self.id == other.id,
                self.guildId == other.guildId,
                self.channelId == other.channelId,
                self.roleId == other.roleId,
                self.title == other.title,
                self.minHour == other.minHour,
                self.maxHour == other.maxHour,
                self.timezone == other.timezone,
                self.startOfWeek == other.startOfWeek,
            ]
        elif isinstance(other, tuple):
            return False not in [
                self.id == other[0],
                self.guildId == other[1],
                self.channelId == other[2],
                self.roleId == other[3],
                self.title == other[4],
                self.minHour == other[5],
                self.maxHour == other[6],
                self.timezone == other[7],
                self.startOfWeek == other[8],
            ]

    def __repr__(self) -> str:
        return (
            "<Task #"
            + str(self.id)
            + " tz="
            + self.timezone
            + " strtOfWk="
            + str(self.startOfWeek)
            + ">"
        )

    def __str__(self) -> str:
        return self.title + " (#" + str(self.id) + ")"


class DBConnector:
    def __init__(self) -> None:
        self.connection: sqlite3.Connection = sqlite3.connect(os.getenv("DB_PATH"))

    def dbRowToTaskObj(
        self, row: tuple[int, int, int, Union[int, None], str, int, int, str, int]
    ) -> Task:
        return Task(
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
        )

    def getTasks(
        self, timezones: list = pytz.all_timezones, startOfWeek: int = -1
    ) -> list[Task]:
        cursor = self.connection.cursor()
        if startOfWeek >= 0:
            cursor.execute(
                "SELECT * FROM tasks WHERE timezone IN ("
                + str(timezones)[1:-1]
                + ") AND start_of_week = "
                + str(startOfWeek)
                + ";"
            )
        else:  # If start of week is not specified, returns all possible values
            cursor.execute(
                "SELECT * FROM tasks WHERE timezone IN (" + str(timezones)[1:-1] + ");"
            )
        tasks = cursor.fetchall()
        cursor.close()
        return [self.dbRowToTaskObj(task) for task in tasks]

    def getTasksByGuildId(self, guildId: int) -> list[Task]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tasks WHERE guild_id = " + str(guildId) + ";")
        tasks = cursor.fetchall()
        cursor.close()
        return [self.dbRowToTaskObj(task) for task in tasks]

    def createTask(
        self,
        guildId: int,
        channelId: int,
        roleId: Union[int, None],
        title: str,
        minHour: int,
        maxHour: int,
        timezone: str,
        startOfWeek: int,
    ) -> Task:
        cursor = self.connection.cursor()

        sql = "INSERT INTO tasks(guild_id, channel_id, role_id, title, min_hour, max_hour, timezone, start_of_week) VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
        data = (
            guildId,
            channelId,
            roleId,
            title,
            minHour,
            maxHour,
            timezone,
            startOfWeek,
        )
        cursor.execute(sql, data)

        self.connection.commit()
        taskId: int = cursor.lastrowid
        cursor.close()

        return Task(
            taskId,
            guildId,
            channelId,
            roleId,
            title,
            minHour,
            maxHour,
            timezone,
            startOfWeek,
        )

    def isAtTaskLimit(
        self, guildId: int
    ):  # This limit should never be raised above 25 since it'll cause issues with the edit Select Menu
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tasks WHERE guild_id = " + str(guildId) + ";")
        tasks = cursor.fetchall()
        cursor.close()
        return len(tasks) >= 4

    def removeTaskById(self, taskId: int):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = " + str(taskId) + ";")
        self.connection.commit()
        cursor.close()
