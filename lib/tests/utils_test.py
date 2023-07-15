import unittest, datetime, pytz
from lib.utils import *


# cd CrabBot
# python -m unittest lib/tests/utils_test.py
class TestUtils(unittest.TestCase):
    def testCreateTimeArray(self):
        """
        Tests for valid array of time from .createTimeArray()
        """
        self.assertEqual(
            createTimeArray(
                datetime.datetime(2023, 7, 14, 0, 0, 1, 1, datetime.UTC), 12, 18
            ),
            [
                "1200-14072023",
                "1300-14072023",
                "1400-14072023",
                "1500-14072023",
                "1600-14072023",
                "1700-14072023",
                "1200-15072023",
                "1300-15072023",
                "1400-15072023",
                "1500-15072023",
                "1600-15072023",
                "1700-15072023",
                "1200-16072023",
                "1300-16072023",
                "1400-16072023",
                "1500-16072023",
                "1600-16072023",
                "1700-16072023",
                "1200-17072023",
                "1300-17072023",
                "1400-17072023",
                "1500-17072023",
                "1600-17072023",
                "1700-17072023",
                "1200-18072023",
                "1300-18072023",
                "1400-18072023",
                "1500-18072023",
                "1600-18072023",
                "1700-18072023",
                "1200-19072023",
                "1300-19072023",
                "1400-19072023",
                "1500-19072023",
                "1600-19072023",
                "1700-19072023",
                "1200-20072023",
                "1300-20072023",
                "1400-20072023",
                "1500-20072023",
                "1600-20072023",
                "1700-20072023",
            ],
        )
        # Shout out to Arizona not dealing with DST, the singular good thing to come out of that state
        self.assertEqual(
            createTimeArray(
                datetime.datetime(
                    2023, 7, 4, 0, 0, 1, 1, pytz.timezone("America/Phoenix")
                ),
                10,
                16,
            ),
            [
                "1700-04072023",
                "1800-04072023",
                "1900-04072023",
                "2000-04072023",
                "2100-04072023",
                "2200-04072023",
                "1700-05072023",
                "1800-05072023",
                "1900-05072023",
                "2000-05072023",
                "2100-05072023",
                "2200-05072023",
                "1700-06072023",
                "1800-06072023",
                "1900-06072023",
                "2000-06072023",
                "2100-06072023",
                "2200-06072023",
                "1700-07072023",
                "1800-07072023",
                "1900-07072023",
                "2000-07072023",
                "2100-07072023",
                "2200-07072023",
                "1700-08072023",
                "1800-08072023",
                "1900-08072023",
                "2000-08072023",
                "2100-08072023",
                "2200-08072023",
                "1700-09072023",
                "1800-09072023",
                "1900-09072023",
                "2000-09072023",
                "2100-09072023",
                "2200-09072023",
                "1700-10072023",
                "1800-10072023",
                "1900-10072023",
                "2000-10072023",
                "2100-10072023",
                "2200-10072023",
            ],
        )

        self.assertEqual(
            createTimeArray(
                datetime.datetime(
                    2023, 7, 4, 0, 0, 1, 1, pytz.timezone("America/Phoenix")
                ),
                0,
                24,
            ),
            [
                "0700-04072023",
                "0800-04072023",
                "0900-04072023",
                "1000-04072023",
                "1100-04072023",
                "1200-04072023",
                "1300-04072023",
                "1400-04072023",
                "1500-04072023",
                "1600-04072023",
                "1700-04072023",
                "1800-04072023",
                "1900-04072023",
                "2000-04072023",
                "2100-04072023",
                "2200-04072023",
                "2300-04072023",
                "0000-05072023",
                "0100-05072023",
                "0200-05072023",
                "0300-05072023",
                "0400-05072023",
                "0500-05072023",
                "0600-05072023",
                "0700-05072023",
                "0800-05072023",
                "0900-05072023",
                "1000-05072023",
                "1100-05072023",
                "1200-05072023",
                "1300-05072023",
                "1400-05072023",
                "1500-05072023",
                "1600-05072023",
                "1700-05072023",
                "1800-05072023",
                "1900-05072023",
                "2000-05072023",
                "2100-05072023",
                "2200-05072023",
                "2300-05072023",
                "0000-06072023",
                "0100-06072023",
                "0200-06072023",
                "0300-06072023",
                "0400-06072023",
                "0500-06072023",
                "0600-06072023",
                "0700-06072023",
                "0800-06072023",
                "0900-06072023",
                "1000-06072023",
                "1100-06072023",
                "1200-06072023",
                "1300-06072023",
                "1400-06072023",
                "1500-06072023",
                "1600-06072023",
                "1700-06072023",
                "1800-06072023",
                "1900-06072023",
                "2000-06072023",
                "2100-06072023",
                "2200-06072023",
                "2300-06072023",
                "0000-07072023",
                "0100-07072023",
                "0200-07072023",
                "0300-07072023",
                "0400-07072023",
                "0500-07072023",
                "0600-07072023",
                "0700-07072023",
                "0800-07072023",
                "0900-07072023",
                "1000-07072023",
                "1100-07072023",
                "1200-07072023",
                "1300-07072023",
                "1400-07072023",
                "1500-07072023",
                "1600-07072023",
                "1700-07072023",
                "1800-07072023",
                "1900-07072023",
                "2000-07072023",
                "2100-07072023",
                "2200-07072023",
                "2300-07072023",
                "0000-08072023",
                "0100-08072023",
                "0200-08072023",
                "0300-08072023",
                "0400-08072023",
                "0500-08072023",
                "0600-08072023",
                "0700-08072023",
                "0800-08072023",
                "0900-08072023",
                "1000-08072023",
                "1100-08072023",
                "1200-08072023",
                "1300-08072023",
                "1400-08072023",
                "1500-08072023",
                "1600-08072023",
                "1700-08072023",
                "1800-08072023",
                "1900-08072023",
                "2000-08072023",
                "2100-08072023",
                "2200-08072023",
                "2300-08072023",
                "0000-09072023",
                "0100-09072023",
                "0200-09072023",
                "0300-09072023",
                "0400-09072023",
                "0500-09072023",
                "0600-09072023",
                "0700-09072023",
                "0800-09072023",
                "0900-09072023",
                "1000-09072023",
                "1100-09072023",
                "1200-09072023",
                "1300-09072023",
                "1400-09072023",
                "1500-09072023",
                "1600-09072023",
                "1700-09072023",
                "1800-09072023",
                "1900-09072023",
                "2000-09072023",
                "2100-09072023",
                "2200-09072023",
                "2300-09072023",
                "0000-10072023",
                "0100-10072023",
                "0200-10072023",
                "0300-10072023",
                "0400-10072023",
                "0500-10072023",
                "0600-10072023",
                "0700-10072023",
                "0800-10072023",
                "0900-10072023",
                "1000-10072023",
                "1100-10072023",
                "1200-10072023",
                "1300-10072023",
                "1400-10072023",
                "1500-10072023",
                "1600-10072023",
                "1700-10072023",
                "1800-10072023",
                "1900-10072023",
                "2000-10072023",
                "2100-10072023",
                "2200-10072023",
                "2300-10072023",
                "0000-11072023",
                "0100-11072023",
                "0200-11072023",
                "0300-11072023",
                "0400-11072023",
                "0500-11072023",
                "0600-11072023",
            ],
        )

        self.assertEqual(
            createTimeArray(
                datetime.datetime(
                    2023, 7, 4, 0, 0, 1, 1, pytz.timezone("America/Phoenix")
                ),
                23,
                24,
            ),
            [
                "0600-05072023",
                "0600-06072023",
                "0600-07072023",
                "0600-08072023",
                "0600-09072023",
                "0600-10072023",
                "0600-11072023",
            ],
        )

        self.assertEqual(
            createTimeArray(
                datetime.datetime(
                    2023, 7, 4, 0, 0, 1, 1, pytz.timezone("America/Phoenix")
                ),
                0,
                1,
            ),
            [
                "0700-04072023",
                "0700-05072023",
                "0700-06072023",
                "0700-07072023",
                "0700-08072023",
                "0700-09072023",
                "0700-10072023",
            ],
        )


if __name__ == "__main__":
    unittest.main()
