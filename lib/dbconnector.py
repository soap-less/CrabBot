import sqlite3, os, pytz
from dotenv import load_dotenv


class DBConnector:
    def __init__(self) -> None:
        self.connection: sqlite3.Connection = sqlite3.connect(os.getenv("DB_PATH"))

    def getTasks(
        self, timezones: list = pytz.all_timezones, startOfWeek: int = -1
    ) -> list:
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
        return tasks

    def getTasksByGuildId(self, guildId: int):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tasks WHERE guild_id = " + str(guildId) + ";")
        tasks = cursor.fetchall()
        cursor.close()
        return tasks

    def addTask(
        self,
        guildId: int,
        channelId: int,
        roleId: int,
        title: str,
        minHour: int,
        maxHour: int,
        timezone: str,
        startOfWeek: int,
    ) -> int:
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

        return taskId

    def isAtTaskLimit(
        self, guildId: int
    ):  # This limit should never be raised above 25 since it'll cause issues with the edit Select Menu
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tasks WHERE guild_id = " + str(guildId) + ";")
        tasks = cursor.fetchall()
        return len(tasks) >= 4


# Run file individually to populate database with test data! !!MAKE SURE TO CHANGE PARAMETERS BELOW!!
if __name__ == "__main__":
    TEST_GUILD_ID = 741602067956629534
    TEST_CHANNEL_ID = 1108703829932916748

    load_dotenv()

    timezones = [
        "Etc/GMT+0",
        "Etc/GMT+1",
        "Etc/GMT+2",
        "Etc/GMT+3",
        "Etc/GMT+4",
        "Etc/GMT+5",
        "Etc/GMT+6",
        "Etc/GMT+7",
        "Etc/GMT+8",
        "Etc/GMT+9",
        "Etc/GMT+10",
        "Etc/GMT+11",
        "Etc/GMT-1",
        "Etc/GMT-2",
        "Etc/GMT-3",
        "Etc/GMT-4",
        "Etc/GMT-5",
        "Etc/GMT-6",
        "Etc/GMT-7",
        "Etc/GMT-8",
        "Etc/GMT-9",
        "Etc/GMT-10",
        "Etc/GMT-11",
        "Etc/GMT-12",
    ]

    dbConn = DBConnector()

    for tz in timezones:
        for i in range(7):
            dbConn.addTask(
                TEST_GUILD_ID,
                TEST_CHANNEL_ID,
                None,
                tz + " - Week Start: " + str(i),
                0,
                24,
                tz,
                i,
            )
