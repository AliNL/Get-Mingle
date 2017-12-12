import unittest
from datetime import datetime

from src.card import calculate_days_from_time


class Test(unittest.TestCase):
    def test_calculate_work_days_not_in_working_hour(self):
        start = datetime(2017, 12, 12, 12, 0, 0)
        end = datetime(2017, 12, 13, 8, 0, 0)
        days = calculate_days_from_time(start, end)
        self.assertEqual(0.67, days)

    def test_calculate_work_days_with_weekends(self):
        start = datetime(2017, 12, 10, 12, 0, 0)
        end = datetime(2017, 12, 13, 9, 0, 0)
        days = calculate_days_from_time(start, end)
        self.assertEqual(2, days)


if __name__ == '__main__':
    unittest.main()
