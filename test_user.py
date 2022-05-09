import unittest
import mysql.connector
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from config import Config
from utils import Mailbox
from utils import wait_til_loaded
from datetime import datetime


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

    def tearDown(self):
        self.cursor.close()
        self.db.close()
        self.driver.close()

    def login(self, login, password):
        # login as admin
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.w-full.w-full')[0].send_keys(
            login)
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.w-full.w-full')[1].send_keys(
            password)
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component')[1].click()

        wait_til_loaded(3, self.driver, '.p-button.p-component.p-button-text.p-button-plain')  # wait for the changes in the browser to take place

    def test01_user_register(self):
        # click register
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-link.mt-2.p-0.h-2rem')[
            0].click()

        # fill in the form
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component')[2].send_keys("test")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component')[3].send_keys("test")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component')[4].send_keys("72081711168")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component')[5].send_keys("test@test.com")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component')[6].send_keys("test")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component')[7].send_keys("test")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component')[8].send_keys("6")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component')[9].send_keys("6")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component')[10].send_keys("test")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component')[11].send_keys("00-000")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.mt-2')[0].click()

        time.sleep(1)

        self.cursor.execute("SELECT * FROM patients")
        query = self.cursor.fetchall()
        doctor = query[-1]

        self.assertEqual(doctor[1], "72081711168")
        self.assertEqual(doctor[3], "test@test.com")

    def test02_user_login(self):
        self.login("test@test.com", "test")
        self.assertTrue('History of vaccinations' in self.driver.page_source)

    def test03_user_register_for_a_vaccination(self):
        self.login("test@test.com", "test")

        self.cursor.execute("SELECT id FROM doctors WHERE isdeleted = 0")
        doctorsId = self.cursor.fetchall()[-1][0]
        self.db.commit()

        self.cursor.execute(f"INSERT INTO `vaccinationslots` (`Id`, `Date`, `Reserved`, `DoctorId`) VALUES (NULL, '2022-06-30 12:24:14.000000', '0', '{doctorsId}')")
        self.db.commit()

        time.sleep(1)

        # click register
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component')[0].click()

        time.sleep(1)

        # hardcoded part // loses validity after 06/30/22
        if datetime.now().month == 5:
            self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-datepicker-next.p-link')[0].click()

        # click the date
        table = self.driver.find_elements(by=By.CSS_SELECTOR, value='td')
        idx = ((len(table) / 7) - 1) * 7 + 4
        table[int(idx)].click()

        # choose a slot
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-outlined.m-2')[0].click()

        # click next
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.mt-5')[0].click()

        time.sleep(1)

        # choose the disease
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component')[5].click()

        # click next
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.ml-1')[0].click()

        time.sleep(1)

        # choose a vaccine type
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-dropdown-trigger')[0].click()
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-dropdown-item')[0].click()

        # click confirm
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.ml-1')[0].click()

        # click confirm
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.ml-1')[0].click()

        self.db.commit()

        time.sleep(1)

        self.cursor.execute("SELECT * FROM vaccinationslots")
        query = self.cursor.fetchall()[-1]
        id = query[0]

        # check if slot is reserved
        self.assertEqual(1, query[2])

        self.cursor.execute(f"SELECT * FROM vaccinations WHERE vaccinationslotid = {id}")
        query = self.cursor.fetchall()

        self.assertTrue(len(query) > 0)

    def test04_user_reschedule_vaccination(self):
        self.login("test@test.com", "test")

        self.cursor.execute("SELECT id FROM doctors WHERE isdeleted = 0")
        doctorsId = self.cursor.fetchall()[-1][0]
        self.db.commit()

        self.cursor.execute(f"INSERT INTO `vaccinationslots` (`Id`, `Date`, `Reserved`, `DoctorId`) VALUES (NULL, '2022-06-29 12:24:14.000000', '0', '{doctorsId}')")
        self.db.commit()

        time.sleep(1)

        # click on a date
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.history-item')[0].click()

        # click reschedule
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component')[-2].click()

        time.sleep(1)

        # hardcoded part // loses validity after 06/30/22
        if datetime.now().month == 5:
            self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-datepicker-next.p-link')[0].click()

        # click the date
        table = self.driver.find_elements(by=By.CSS_SELECTOR, value='td')
        idx = ((len(table) / 7) - 1) * 7 + 3
        table[int(idx)].click()

        time.sleep(1)

        # choose a slot
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-outlined.m-2')[0].click()

        # click reschedule
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-text')[-1].click()

        time.sleep(1)

        self.cursor.execute("SELECT * FROM vaccinationslots")
        query = self.cursor.fetchall()[-1]
        id = query[0]

        # check if slot is reserved
        self.assertEqual(1, query[2])

        self.cursor.execute(f"SELECT * FROM vaccinations WHERE vaccinationslotid = {id}")
        query = self.cursor.fetchall()

        self.assertTrue(len(query) > 0)

    def test05_user_cancel_vaccination(self):
        self.login("test@test.com", "test")

        time.sleep(1)

        # click on a date
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.history-item')[0].click()

        # click cancel
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component')[-1].click()

        time.sleep(1)

        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-text')[-1].click()

    def test06_user_edit_personal_data(self):
        self.login("test@test.com", "test")

        # click personal data
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component')[2].click()

        time.sleep(1)

        # change name
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inplace-display')[0].click()

        prev_text = self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.p-filled')[0].get_attribute("value")

        for i in range(len(prev_text)):
            self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.p-filled')[0].send_keys(Keys.BACKSPACE)

        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component')[0].send_keys(
            "test2")

        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.confirm-button')[0].click()

        time.sleep(1)

        self.cursor.execute("SELECT * FROM patients")
        query = self.cursor.fetchall()[-1]

        self.assertEqual("test2", query[5])

    def test07_user_report_a_bug(self):
        self.login("test@test.com", "test")

        # click settings
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-text.p-button-plain')[4].click()

        # fill in the form
        form_inputs = self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.w-full.w-full')
        form_inputs[-2].send_keys('test_name')
        form_inputs[-1].send_keys('test_description')

        # click send
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component')[-1].click()

        # TODO: add verification


Config.set_up()
