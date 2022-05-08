import unittest
import selenium

from utils import Mailbox
from config import Config

# tests
from test_admin import AdminTests
from test_user import UserTests
from test_doctor import DoctorTests

if __name__ == '__main__':
    Mailbox.debugLevel = 1
    Config.set_up()
    unittest.main(argv=Config.parse_test_args())
