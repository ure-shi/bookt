###########################################################
######################## Init Vars ########################

##- Chrome Driver Settings -##
#executable_path="/usr/bin/chromedriver"
executable_path="chromedriver.exe"
headless_execution = False

##- QLD Booking Settings -##
drivers_license_number = '131673618'
contact_name = 'Oliver Stewart'
contact_phone_number = '0413162065'

product_type_number = "1"
region_number = "12"
centre_number = "0"

##- DiscordPY Settings -##
token = [private_token]

######################## Init Vars ########################
###########################################################
######################### Imports #########################

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import asyncio

import discord
from discord.ext import commands, tasks

######################### Imports #########################
###########################################################
######################### Globals #########################

service = Service(executable_path=executable_path)

options = Options()
options.headless = headless_execution

driver = webdriver.Chrome(service=service, options=options)

######################### Globals #########################
###########################################################
##################### Useful Functions ####################

def click_ByID(ID):
    while True:
        try:
            region = driver.find_element(By.ID, ID)
            #region = WebDriverWait(driver, 30).until\
            #    (EC.presence_of_element_located((By.ID, ID)))
            region = WebDriverWait(driver, 30, ignored_exceptions=(ElementNotInteractableException)).until\
                (EC.element_to_be_clickable(region))
            time.sleep(0.25)
            region.click()
            time.sleep(0.25)
            break
        except StaleElementReferenceException:
            time.sleep(0.25)
            continue
        except NoSuchElementException:
            time.sleep(0.25)
            continue

##################### Useful Functions ####################
###########################################################
######################## Main Code ########################

intents = discord.Intents.default()
client = commands.Bot(command_prefix = '>', intents=intents)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game("with ur mum"))
    await main()
    background_task.start()
    print('Bot is ready')

async def main():
    #initialize ChromeDriver + cookie
    print("initialize ChromeDriver + cookie")
    driver.get('https://www.service.transport.qld.gov.au/SBSExternal/public/WelcomeDrivingTest.xhtml')

    click_ByID('j_id_5r:aboutThisServiceForm:continueButton')
    click_ByID('termsAndConditions:TermsAndConditionsForm:acceptButton')

    click_ByID('CleanBookingDEForm:productType')
    click_ByID('CleanBookingDEForm:productType_' + str(product_type_number))

    dlNumber_in = driver.find_element(By.ID,'CleanBookingDEForm:dlNumber')
    contactName_in = driver.find_element(By.ID,'CleanBookingDEForm:contactName')
    contactPhone_in = driver.find_element(By.ID,'CleanBookingDEForm:contactPhone')
    dlNumber_in.send_keys(drivers_license_number)
    contactName_in.send_keys(contact_name)
    contactPhone_in.send_keys(contact_phone_number)

    click_ByID('CleanBookingDEForm:actionFieldList:confirmButtonField:confirmButton')
    click_ByID('BookingConfirmationForm:actionFieldList:confirmButtonField:confirmButton')

    click_ByID('BookingSearchForm:region')
    click_ByID('BookingSearchForm:region_' + str(region_number))

    click_ByID('BookingSearchForm:centre')
    click_ByID('BookingSearchForm:centre_' + str(centre_number))

    click_ByID('BookingSearchForm:actionFieldList:confirmButtonField:confirmButton')

    #initialize channels
    print("initialize channels")
    global seq_brisbane_northside
    seq_brisbane_northside = client.get_channel(1028460622914015325)

@tasks.loop(seconds=10)
async def background_task():
    if not hasattr(background_task, "old"):
        background_task.old = []
    background_task.new = []

    msg = ''

    for i in range(0, 10):
        _time = WebDriverWait(driver, 30, ignored_exceptions=(NoSuchElementException,ElementNotInteractableException)).until\
                    (EC.presence_of_element_located((By.XPATH, "//tr[@data-ri='" + str(i) + "']//label[@for='slotSelectionForm:slotTable:" + str(i) + ":startTime']")))
        location = WebDriverWait(driver, 30, ignored_exceptions=(NoSuchElementException,ElementNotInteractableException)).until\
                    (EC.presence_of_element_located((By.XPATH, "//tr[@data-ri='" + str(i) + "']//td[@role='gridcell'][3]")))
        background_task.new.append((_time.text, location.text))

    count = 0

    for booking in background_task.new:
        if not booking in background_task.old:
            msg = msg + booking[0] + ', ' + booking[1] + '\n'
            count = count + 1
    
    background_task.old = background_task.new

    if count > 0:
        if count == 1:
            await seq_brisbane_northside.send("A new booking has opened:\n\n" + msg + "\nTo reschedule your test, log into QLD's reschedule service: https://bit.ly/3SLytlv\nTo find your Booking Reference Number search the email subject: 'Driving Test Booking Confirmation' in your emails")
            print("\nNEW MESSAGE TEXT:\nA new booking has opened:\n\n" + msg + "\nTo reschedule your test, log into QLD's reschedule service: https://bit.ly/3SLytlv\nEND OF MESSAGE TEXT\n")
        else:
            await seq_brisbane_northside.send("New bookings have opened:\n\n" + msg + "\nTo reschedule your test, log into QLD's reschedule service: https://bit.ly/3SLytlv\nTo find your Booking Reference Number search the email subject: 'Driving Test Booking Confirmation' in your emails")
            print("\nNEW MESSAGE TEXT:\nNew bookings have opened:\n\n" + msg + "\nTo reschedule your test, log into QLD's reschedule service: https://bit.ly/3SLytlv\nEND OF MESSAGE TEXT\n")
    else:
        print("No new bookings, no new messages")

    driver.refresh()

client.run(token)
