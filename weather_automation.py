import re
# For using sleep function to load pages
import time
# For interactions with webpage
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options

from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# For locating user
import reverse_geocode
# For sending emails
import smtplib
# For getting date
from datetime import date


# For chrome browser to run in background
# options = Options()
# options.headless = True

# weather_info stores all the information necessary to report back the the user
class weather_info:
    def __init__(self, max, min, current, rain, uv):
        self.max = max
        self.min = min
        self.current = current
        self.rain = rain
        self.uv = uv

# get_latitude_longitude() opens up google maps and obtains the user's longitude and latitude
# requires: user's location is accessible
# effects: opens chrome browser
#          reads from url (location)
def get_latitude_longitude():
    # set up webdriver
    driver_gmaps = webdriver.Chrome()
    # go to google maps
    driver_gmaps.get("https://www.google.com/maps")
    # wait for page to load, until coordinates are visible
    wait = WebDriverWait(driver_gmaps, 10)
    wait.until(EC.url_matches(r'@(-?\d+\.\d+),(-?\d+\.\d+)'))
    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', driver_gmaps.current_url)
    # attempts to obtain longitude and lattitude
    if match:
        latitude, longitude = map(float, match.groups())
        return (latitude, longitude)
    else:
        print("Error getting location: Unable to get your coordinates")
        return None
    
    driver_gmaps.quit()


# get_city() translates lattitude or longitude coordinates into city, country
#            if coordinates are not provided, it prompts users to type in their location
# effects: may write and read to the console
def get_city():
    # get coordinates from get_latitude_longitude()
    coordinates = get_latitude_longitude()
    if coordinates is not None:
        # uses reverse_geocode to search for information on provided longitude and lattitude
        address = reverse_geocode.search(((coordinates),))
        city_country = address[0]['city'] + ', ' + address[0]['country']
        return city_country
    else:
        # if coordinates not provided, prompts user for city and country
        city_country = input("Please enter your city and country: ")
        return city_country


# get_data() obtains relevant data from accweather website, returning weather information
# requires: user has internet access
# effects: inputs to webside, reads from website
def get_data():
    # obtains location from get_city()
    city = get_city()
    # initialize webdriver
    driver_weather = webdriver.Chrome()
    # open accuweather (weather reporting website)
    driver_weather.get("https://www.accuweather.com/")
    # find search bar and enter location
    input_field = WebDriverWait(driver_weather, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-input')))
    input_field.clear()
    input_field.send_keys(city)
    # navigate to first autocomplete option from the dropdown menu
    time.sleep(3)
    current_block = WebDriverWait(driver_weather, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'search-results'))
    )
    input_field.send_keys(Keys.ARROW_DOWN)
    input_field.send_keys(Keys.ENTER)
    # click on the weather card to navigate to current information
    current_block = WebDriverWait(driver_weather, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'cur-con-weather-card__body'))
    )
    current_block.click()

    # find current temperature
    try:
        current_temp_elem = WebDriverWait(driver_weather, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'display-temp'))
        )
        current_temp = current_temp_elem.text[:-2]
    except NoSuchElementException:
        print("Current temperature not found.")
        current_temp = None
    # find max temperature
    try:
        max_temp_elem = WebDriverWait(driver_weather, 5).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='temperature' and span[@class='hi-lo-label' and text()='Hi']]"))
        )
        max_temp = max_temp_elem.text[:-3]
    except NoSuchElementException:
        print("Maximum temperature not found.")
        max_temp = None
    # find min temperature
    try:
        min_temp_elem = WebDriverWait(driver_weather, 5).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='temperature' and span[@class='hi-lo-label' and text()='Lo']]"))
        )
        min_temp = min_temp_elem.text[:-3]
    except NoSuchElementException:
        print("Minumum temperature not found.")
        min_temp = None

    # find chance of rain
    try:
        precip_prob_elem = WebDriverWait(driver_weather, 5).until(
        EC.presence_of_element_located((By.XPATH, "(//p[@class='panel-item' and contains(text(), 'Probability of Precipitation')])[1]"))
        )
        precip_prob = precip_prob_elem.find_element(By.CLASS_NAME, "value").text[:-1]
    except NoSuchElementException:
        print("Probability of Precipitation not found.")
        precip_prob = None

    # find uv index
    try:
        uv_elem = WebDriverWait(driver_weather, 5).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='half-day-card-content']//p[@class='panel-item' and contains(text(), 'Max UV Index')]"))
        )
        uv_text = uv_elem.find_element(By.CLASS_NAME, "value").text
        uv_match = re.search(r'\d+', uv_text)
        uv_int = uv_match.group()
    except NoSuchElementException:
        print("UV index not found.")
        uv_int = None

    # return data
    weather_data = weather_info(int(max_temp), int(min_temp), int(current_temp), int(precip_prob), int(uv_int))
    return weather_data

# send_email() formats and sends the relevant information to the user's email
# effects: accesses weatherinfoautomation@gmail.com's account
#          sends information to user's email
def send_email():
    # obtain today's weather info
    weather = get_data()
    # set up account info
    sender_email = "weatherinfoautomation@gmail.com"
    sender_password = "nrrr ontg sgpp omsl"                 # used "app password" option, as gmail doesn't trust other methods
    receiver_email = "weatherinfoautomation@gmail.com"
    # prepare default email content
    today = str(date.today())
    subject = "Weather on " + today
    body = f"Good morning! Here's the weather summary for {today}:\n"
    body += f"It's currently {weather.current} degrees outside.\n"
    body += f"The temperature will range from {weather.max} to {weather.min} degrees today.\n"
    # provide personalized suggestions based on weather information
    if weather.rain > 10:
        body += f"There's a {weather.rain}% chance of rain! Consider bringing an umbrella!\n"
    if weather.uv > 7:
        body += f"There's a lot of sun today! Consider wearing a hat or sunglasses!\n"
    if weather.max > 25:
        body += "It's hot! Wear light clothes.\n"
    elif weather.min < 5:
        body += "It's cold! Bring a warm coat.\n"
    elif weather.min < 15:
        body += "It's moderate. A light jacket might be needed.\n"
    # setting up the message
    message = f'Subject: {subject}\n\n{body}'
    # connecting to server
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    # login to email account
    server.login(sender_email, sender_password)
    # send the email!
    server.sendmail(sender_email, receiver_email, message)
    server.quit()


# can choose to customize this to a daily process
send_email()


