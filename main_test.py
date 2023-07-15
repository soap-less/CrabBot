from main import main
from lib.dbconnector import DBConnector
import asyncio, sqlite3, unittest, os
from dotenv import load_dotenv


# Runs the bot file with a populated database
# python -m unittest lib.dbconnector_test.CreateTestDB
class CreateTestDB(unittest.TestCase):
    def setUp(self) -> None:
        # Creates a clean task table
        load_dotenv()
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS tasks;")
        cursor.execute(
            """CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                role_id INTEGER,
                title TEXT NOT NULL,
                min_hour INTEGER NOT NULL,
                max_hour INTEGER NOT NULL,
                timezone TEXT NOT NULL,
                start_of_week INTEGER NOT NULL
            );"""
        )
        conn.commit()
        cursor.close()
        conn.close()

        self.GUILD_ID = int(os.getenv("TEST_GUILD_ID"))
        self.CHANNEL_ID = int(os.getenv("TEST_CHANNEL_ID"))
        self.ROLE_ID = int(os.getenv("TEST_ROLE_ID"))

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
                dbConn.createTask(
                    self.GUILD_ID,
                    self.CHANNEL_ID,
                    self.ROLE_ID,
                    tz + " - Week Start: " + str(i),
                    8,
                    22,
                    tz,
                    i,
                )

        self.assertTrue(len(dbConn.getTasksByGuildId(self.GUILD_ID)) > 0)

    def tearDown(self) -> None:
        load_dotenv()
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS tasks;")
        cursor.execute(
            """CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                role_id INTEGER,
                title TEXT NOT NULL,
                min_hour INTEGER NOT NULL,
                max_hour INTEGER NOT NULL,
                timezone TEXT NOT NULL,
                start_of_week INTEGER NOT NULL
            );"""
        )
        conn.commit()
        cursor.close()
        conn.close()

    """Runs the bot with a filled DB"""

    def testBotWithDB(self):
        asyncio.run(main())
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
