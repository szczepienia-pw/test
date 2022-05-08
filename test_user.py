import unittest
import mysql.connector
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from config import Config
from utils import Mailbox


class UserTests(unittest.TestCase):
    def setUp(self):
        # initiate selenium
        options = Options()

        if Config.headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.driver.get(Config.frontUrl)

        # initiate a connection with the DB
        self.db = mysql.connector.connect(
            host=Config.dbAddress,
            database=Config.dbName,
            user=Config.dbUser,
            password=Config.dbPass
        )
        self.cursor = self.db.cursor()

        # login as admin
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.w-full.w-full')[0].send_keys(
            "john@patient.com")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.w-full.w-full')[1].send_keys(
            "password")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component')[1].click()

        time.sleep(1)  # wait for the changes in the browser to take place

    def tearDown(self):
        self.cursor.close()
        self.db.close()
        self.driver.close()

    def test01_user_login(self):
        # if self.setUp executes without failure, that means we are logged in as admin
        self.assertTrue('History of vaccinations' in self.driver.page_source)


Config.set_up()
