from unittest import TestCase
from hm_wrapper import _utils
import _datetime


class Test(TestCase):
    def test_parse_date_input(self):
        c1 = _datetime.datetime(2020, 1, 27, 0).isoformat()
        t1 = _utils.parse_date_input("01/27/2020")
        t2 = _utils.parse_date_input("1/27/20")
        self.assertEqual(c1, t1)
        self.assertEqual(c1, t2)

