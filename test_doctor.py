import unittest
import mysql.connector
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime

from config import Config
from utils import Mailbox
from utils import wait_til_loaded


class DoctorTests(unittest.TestCase):
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
        self.driver.find_elements(by=By.CSS_SELECTOR,
                                  value='.p-button.p-component.p-button-link.align-self-end.mb-6.p-0')[0].click()
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-menuitem')[0].click()
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.w-full.w-full')[0].send_keys(
            "john@doctor.com")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.w-full.w-full')[1].send_keys(
            "password")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component')[1].click()

        wait_til_loaded(3, self.driver,
                        '.p-button.p-component.p-button-text.p-button-plain')  # wait for the changes in the browser to take place

    def tearDown(self):
        self.cursor.close()
        self.db.close()
        self.driver.close()

    def test01_doctor_login(self):
        time.sleep(3)
        # if self.setUp executes without failure, that means we are logged in
        self.assertTrue('Add new vaccination slot' in self.driver.page_source)

    def test02_doctor_add_vaccination_slot(self):
        # open calendar
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-icon-only.p-datepicker-trigger')[
            0].click()

        # go ten months into the future
        for i in range(1):
            self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-datepicker-next.p-link')[0].click()

        time.sleep(2)

        # click a random date
        self.driver.find_elements(by=By.CSS_SELECTOR, value='td')[-7].click()

        # submit
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component')[5].click()

        time.sleep(3)

        self.cursor.execute('SELECT * FROM VaccinationSlots')
        query_raw = self.cursor.fetchall()[-1][1]

        Mailbox.debug(query_raw)

        chosen_date = datetime.strptime(self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component')[0].get_attribute('value'), '%m/%d/%Y %H:%M')
        query_date = datetime.strptime(f"{query_raw.day}/{query_raw.month}/{query_raw.year} {query_raw.hour}:{query_raw.minute}", '%d/%m/%Y %H:%M')

        self.assertEqual(chosen_date.minute, query_date.minute)
        self.assertEqual(chosen_date.hour, query_date.hour)

    def test03_doctor_delete_vaccination_slot(self):
        """
        assumes that there is a VaccinationSlot in the DB
        """
        time.sleep(3)

        # get the last slot data
        table = self.driver.find_elements(by=By.CSS_SELECTOR, value='td')
        idx = ((len(table) / 6) - 1) * 6 + 2
        date = datetime.strptime(table[int(idx)].text, '%d.%m.%Y')

        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-icon-only.p-button-danger.p-button-rounded')[-1].click()
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-text')[-1].click()

        time.sleep(1)

        self.cursor.execute('SELECT * FROM VaccinationSlots')
        query_raw = self.cursor.fetchall()

        if len(query_raw) > 0:
            query_raw = query_raw[-1][1]
            query_date = datetime.strptime(
                f"{query_raw.day}/{query_raw.month}/{query_raw.year} {query_raw.hour}:{query_raw.minute}", '%d/%m/%Y %H:%M')

            self.assertNotEqual((date.year, date.month, date.day), (query_date.year, query_date.month, query_date.day))
        else:
            self.assertTrue(True)

    def test04_doctor_report_a_bug(self):
        # click settings
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-text.p-button-plain')[
            3].click()

        # fill in the form
        form_inputs = self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.w-full.w-full')
        form_inputs[-2].send_keys('test_name')
        form_inputs[-1].send_keys('test_description')

        # click send
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component')[-1].click()

        # TODO: add verification


Config.set_up()
