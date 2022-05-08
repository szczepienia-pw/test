import unittest
import mysql.connector
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from config import Config
from utils import Mailbox
from utils import wait_til_loaded


class AdminTests(unittest.TestCase):
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
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-link.align-self-end.mb-6.p-0')[0].click()
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-menuitem')[1].click()
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.w-full.w-full')[0].send_keys("john@admin.com")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.w-full.w-full')[1].send_keys("password")
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component')[1].click()

        wait_til_loaded(3, self.driver, '.p-button.p-component.p-button-text.p-button-plain')  # wait for the changes in the browser to take place

    def tearDown(self):
        self.cursor.close()
        self.db.close()
        self.driver.close()

    def get_last_doctors_id(self):
        table_cells = self.driver.find_elements(by=By.CSS_SELECTOR, value='td')
        return table_cells[int(((len(table_cells) / 6) - 1) * 6 + 1)].text

    def test01_admin_login(self):
        # if self.setUp executes without failure, that means we are logged in as admin
        self.assertTrue('Manage doctors' in self.driver.page_source)

    def test02_admin_add_doctor(self):
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.mr-2')[0].click()

        form_inputs = self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component')
        form_inputs[1].send_keys('test')  # first name
        form_inputs[2].send_keys('test')  # last name
        form_inputs[3].send_keys('test@test.com')  # email
        form_inputs[4].send_keys('test')  # password

        buttons = self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-text')
        buttons[-1].click()  # save

        time.sleep(1)  # wait for the changes in the browser to take place
        _id = self.get_last_doctors_id()

        # verify the db changes
        self.cursor.execute(f"SELECT FirstName, LastName, Email FROM Doctors WHERE Id = {_id}")
        res = self.cursor.fetchall()[-1]
        self.assertEqual(res[0], 'test')
        self.assertEqual(res[1], 'test')
        self.assertEqual(res[2], 'test@test.com')

    def test03_admin_edit_doctor(self):
        time.sleep(1)

        _id = self.get_last_doctors_id()

        # edit the last doctor
        buttons = self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-icon-only.p-button-rounded.mr-2')
        buttons[-1].click()

        time.sleep(1)  # wait for the changes in the browser to take place

        form_inputs = self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.p-filled')

        form_inputs[0].clear()
        form_inputs[0].send_keys("_test")  # edit first name

        form_inputs[1].clear()
        form_inputs[1].send_keys("_test")  # edit last name

        form_inputs[2].clear()
        form_inputs[2].send_keys("test@test.com")  # edit email name

        time.sleep(1)  # wait for the changes in the browser to take place

        buttons = self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-text')
        buttons[-1].click()  # save

        time.sleep(1)  # wait for the changes in the browser to take place

        # refresh db
        self.db.commit()

        # verify the db changes
        self.cursor.execute(f"SELECT FirstName, LastName, Email FROM Doctors WHERE Id = {_id}")
        res = self.cursor.fetchall()[0]
        self.assertEqual(res[0], '_test')
        self.assertEqual(res[1], '_test')
        self.assertEqual(res[2], 'test@test.com')

    def test04_admin_delete_doctor(self):
        time.sleep(1)

        _id = self.get_last_doctors_id()

        # select the last doctor
        doctors = self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-checkbox.p-component')
        doctors[-1].click()

        # click delete
        buttons = self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-danger')
        buttons[0].click()

        # click yes
        buttons = self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-text')
        buttons[-1].click()

        time.sleep(1)  # wait for the changes in the browser to take place
        self.db.commit()  # refresh db

        # verify
        self.cursor.execute(f"SELECT IsDeleted FROM Doctors WHERE Id = {_id}")
        res = self.cursor.fetchall()

        self.assertEqual(1, res[0][0])

    def test05_admin_change_settings(self):
        # click settings
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-text.p-button-plain')[3].click()

        # click edit
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inplace-display')[0].click()

        # edit settings
        settings = self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.p-filled')[0]
        settings.clear()
        settings.send_keys('test')

        # save settings
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component')[-1].click()

        time.sleep(1)

        # verify
        self.cursor.execute("SELECT value FROM Settings")
        res = self.cursor.fetchall()
        self.assertEqual('test', res[0][0])

    def test06_admin_report_a_bug(self):
        # click settings
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-text.p-button-plain')[4].click()

        # fill in the form
        form_inputs = self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-inputtext.p-component.w-full.w-full')
        form_inputs[-2].send_keys('test_name')
        form_inputs[-1].send_keys('test_description')

        # click send
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component')[-1].click()

        # TODO: add verification

    def test07_admin_logout(self):
        # click settings
        self.driver.find_elements(by=By.CSS_SELECTOR, value='.p-button.p-component.p-button-text.p-button-plain')[5].click()
        self.assertTrue('Patient log in' in self.driver.page_source)


Config.set_up()
