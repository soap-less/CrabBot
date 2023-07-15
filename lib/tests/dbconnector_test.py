import os, asyncio
from dotenv import load_dotenv
import unittest, sqlite3
from lib.dbconnector import Task, DBConnector
from main import main


class TestTaskObject(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv()
        self.GUILD_ID = int(os.getenv("TEST_GUILD_ID"))
        self.CHANNEL_ID = int(os.getenv("TEST_CHANNEL_ID"))
        self.ROLE_ID = int(os.getenv("TEST_ROLE_ID"))

    def testEqualWithOtherTask(self):
        self.assertEqual(
            Task(
                0,
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
            Task(
                0,
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
        )
        self.assertNotEqual(
            Task(
                1,
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
            Task(
                0,
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
        )
        self.assertNotEqual(
            Task(
                1,
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
            Task(
                1,
                self.GUILD_ID,
                self.CHANNEL_ID,
                None,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
        )
        self.assertNotEqual(
            Task(
                1,
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
            Task(
                1,
                self.GUILD_ID,
                self.CHANNEL_ID,
                None,
                "Real Title!!!",
                8,
                24,
                "America/Los_Angeles",
                1,
            ),
        )
        self.assertNotEqual(
            Task(
                1,
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
            Task(
                1,
                self.GUILD_ID,
                self.CHANNEL_ID,
                None,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                0,
            ),
        )

    def testEqualWithDBRow(self):
        self.assertEqual(
            Task(
                0,
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
            (
                0,
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
        )
        self.assertNotEqual(
            Task(
                1,
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
            (
                0,
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
        )
        self.assertNotEqual(
            Task(
                1,
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
            (
                1,
                self.GUILD_ID,
                self.CHANNEL_ID,
                None,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
        )
        self.assertNotEqual(
            Task(
                1,
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
            (
                1,
                self.GUILD_ID,
                self.CHANNEL_ID,
                None,
                "Real Title!!!",
                8,
                24,
                "America/Los_Angeles",
                1,
            ),
        )
        self.assertNotEqual(
            Task(
                1,
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                1,
            ),
            (
                1,
                self.GUILD_ID,
                self.CHANNEL_ID,
                None,
                "Real Title!!!",
                0,
                24,
                "America/Los_Angeles",
                0,
            ),
        )


class TestDBConnector(unittest.TestCase):
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

        self.dbConnector = DBConnector()
        self.GUILD_ID = int(os.getenv("TEST_GUILD_ID"))
        self.CHANNEL_ID = int(os.getenv("TEST_CHANNEL_ID"))
        self.ROLE_ID = int(os.getenv("TEST_ROLE_ID"))

    def testCreateTask(self):
        """
        Tests if .createTask() properly adds row to database
        """
        with self.subTest(i=0):
            """
            Test with not null Role ID
            """
            taskToAdd = self.dbConnector.createTask(
                self.GUILD_ID,
                self.CHANNEL_ID,
                self.ROLE_ID,
                "Title With Role",
                0,
                24,
                "America/Los_Angeles",
                0,
            )

            isTaskReturnedWithId: bool = taskToAdd.id == 1

            cursor = self.dbConnector.connection.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = 1;")
            row = cursor.fetchone()

            isRowInfoEqualToTaskObj: bool = taskToAdd == row

            self.assertTrue(isTaskReturnedWithId and isRowInfoEqualToTaskObj)

        with self.subTest(i=1):
            """
            Test with NULL Role ID
            """
            taskToAdd = self.dbConnector.createTask(
                self.GUILD_ID,
                self.CHANNEL_ID,
                None,
                "Title With Role",
                0,
                24,
                "America/Los_Angeles",
                0,
            )

            isTaskReturnedWithId: bool = taskToAdd.id == 2

            cursor = self.dbConnector.connection.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = 2;")
            row = cursor.fetchone()

            isRowInfoEqualToTaskObj: bool = taskToAdd == row

            self.assertTrue(
                isTaskReturnedWithId and isRowInfoEqualToTaskObj and row[3] == None
            )

    def testDatabaseRowToObject(self):
        """
        Test converting a tuple given by sqlite into a Task type object.
        """
        task = self.dbConnector.createTask(
            os.getenv("TEST_GUILD_ID"),
            os.getenv("TEST_CHANNEL_ID"),
            os.getenv("TEST_ROLE_ID"),
            "title",
            0,
            24,
            "timezone",
            1,
        )
        cursor = self.dbConnector.connection.cursor()
        cursor.execute(f"SELECT * FROM tasks WHERE id = {task.id};")

        tupl = cursor.fetchone()
        taskObject = self.dbConnector.dbRowToTaskObj(tupl)
        self.assertEqual(tupl, taskObject)
