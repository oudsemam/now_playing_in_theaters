import os
import ssl
import wifi
import socketpool
import adafruit_requests
import time
import board
import terminalio
import displayio
import json
from adafruit_datetime import datetime
from adafruit_magtag.magtag import MagTag
from adafruit_display_text import label, wrap_text_to_pixels, scrolling_label


# Getting today's date variables
aio_username = os.getenv("AIO_USERNAME")
aio_key = os.getenv("AIO_KEY")
timezone = os.getenv("TIMEZONE")
TIME_URL = "https://io.adafruit.com/api/v2/"+str(aio_username)+"/integrations/time/strftime?x-aio-key="+aio_key+"&tz="+timezone+"&fmt=%25Y-%25m-%25d+%25H%3A%25M%3A%25S.%25L+%25j+%25u+%25z+%25Z"

# headers for the call
TMBD_TOKEN = str(os.getenv("TMBD_TOKEN"))
HEADERS = dict(accept = "application/json", Authorization="Bearer "+TMBD_TOKEN)
# sets variables
PAGENUMBER = 1
# This URL is themoviedb.org.
MOVIE_URL_START = "https://api.themoviedb.org/3/movie/"
MOVIE_URL_END_POINT = "now_playing?" # shows now playing movies
# MOVIE_URL_END_POINT = "upcoming?" # shows upcoming movies in theathers
MOVIE_URL_LANGUAGE = "language=en-US"
MOVIE_URL_PAGE = "page="
MOVIE_URL_REGION ="region=US"

# Need to define and use for MagTag call early on
# Remainder of functions are down below.
def format_url_string (URL_START,
    URL_END_POINT,
    URL_LANGUAGE,
    URL_PAGE,
    PAGENUMBER,
    URL_REGION):
    JSON_MOVIE_URL = URL_START+URL_END_POINT+URL_LANGUAGE
    JSON_MOVIE_URL += "&"+URL_PAGE+str(PAGENUMBER)+"&"+URL_REGION
    return str(JSON_MOVIE_URL)

JSON_MOVIE_URL = format_url_string (MOVIE_URL_START,
    MOVIE_URL_END_POINT,
    MOVIE_URL_LANGUAGE,
    MOVIE_URL_PAGE,
    PAGENUMBER,
    MOVIE_URL_REGION)

MOVIES = []
magtag = MagTag(url=JSON_MOVIE_URL, headers=HEADERS, json_path=MOVIES)
# variables for other functions
HOW_MANY_DAYS_TO_ADD = 14
READ_TIME = 45
WAIT = 180
CONTINUE = True

# display variables
WRAP_TEXT = 48
display = board.DISPLAY
# wait until we can draw
time.sleep(display.time_to_refresh)
# main group to hold everything
main_group = displayio.Group()
# white background. Scaled to save RAM
bg_bitmap = displayio.Bitmap(display.width // 8, display.height // 8, 1)
bg_palette = displayio.Palette(1)
bg_palette[0] = 0xFFFFFF
bg_sprite = displayio.TileGrid(bg_bitmap, x=0, y=0, pixel_shader=bg_palette)
bg_group = displayio.Group(scale=8)
bg_group.append(bg_sprite)
main_group.append(bg_group)
# text area
title_text_area = label.Label(
    terminalio.FONT,
    scale=2,
    color=0x000000,
    padding_top=1,
    padding_bottom=3,
    padding_right=4,
    padding_left=4,
)
release_date_text = label.Label(
    terminalio.FONT,
    scale=1,
    color=0x000000,
    padding_top=1,
    padding_bottom=3,
    padding_right=4,
    padding_left=4,
)
details_text = label.Label(
    terminalio.FONT,
    scale=1,
    color=0x000000,
    padding_top=1,
    padding_bottom=3,
    padding_right=4,
    padding_left=4,
)

# define functions to display the movies
def string_to_date(string):
    # takes a string date and turns it into an iso formatted date
    isoformat = datetime.fromisoformat(string)
    return isoformat

def add_days(today_string, days_to_add):
    is_leap_year = False
    date_obj = today_string.split('-')
    year = int(date_obj[0])
    month = int(date_obj[1])
    day = int(date_obj[2])
    leap_year_calc = year/400
    if "." in str(leap_year_calc):
        is_leap_year = True
    else:
        is_leap_year = False
    added_days = day + days_to_add
    if added_days > 31 and (month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12):
        added_days = added_days - 31
        print("This is calc day: ", day)
        month += 1
        if month == 12:
            year += 1
    if (month == 4 or month == 6 or month == 9 or month == 11) and added_days > 30:
        day = added_days - 30
        month += 1
    if month == 2 and is_leap_year and day < 28:
        day = added_days - 28
        month +=1
    date_next_week = str(year)+"-"
    if month < 10:
        date_next_week += "0"+str(month)+"-"
    else:
        date_next_week += str(month)
    if added_days < 10:
        date_next_week += "0"+str(added_days)
    else:
        date_next_week += str(added_days)
    return date_next_week



def filter_by_date(today_string, release_date_string, HOW_MANY_DAYS_TO_ADD):
    # takes today's date based on set timezone and
    # compares it to the movie release_date
    # also added functionality to show only movies released in the
    # next 7 days
    today_date = string_to_date(today_string)
    future_date_string = add_days(today_string, HOW_MANY_DAYS_TO_ADD)
    future_date = string_to_date(future_date_string)
    movie_release_date = string_to_date(release_date_string)
    movie_released_after_today = today_date < movie_release_date
    movie_release_future_date = movie_release_date < future_date
    if movie_released_after_today and movie_release_future_date:
        add_movie = True
    else:
        add_movie = False
    return add_movie

def format_to_date_string(datetime_string):
    # takes the response from get_today and parses out the date
    # string infomration
    datetime_obj = datetime_string.split(' ')
    if len(datetime_obj) > 0:
        today_string = datetime_obj[0]
        return today_string
    else:
        today_string = "2025-04-01"
    return today_string

def get_today():
    # calls the API in order to get today's date based on the set
    # timezone and creds in secrets.py
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    print("At the tone the time will be... (getting today's date)")
    response = requests.get(TIME_URL)
    datetime_string = response.text
    today_string = format_to_date_string(datetime_string)
    return today_string

def movie_loop(today, raw_data, results_data, HOW_MANY_DAYS_TO_ADD):
    if len(raw_data['results']) > 0:
        for movie in results_data:
            add_movie = filter_by_date(today, movie['release_date'], HOW_MANY_DAYS_TO_ADD)
            if add_movie and movie['poster_path']!=None:
                movie_data = {}
                movie_data["title"] = movie['title']
                movie_data["release_date"] = movie['release_date']
                movie_data["overview"] = movie['overview']
                MOVIES.append(movie_data)
    return MOVIES

def get_movie_info(MOVIE_URL_START,
        MOVIE_URL_END_POINT,
        MOVIE_URL_LANGUAGE,
        MOVIE_URL_PAGE,
        PAGENUMBER,
        MOVIE_URL_REGION,
        MOVIES,
        CONTINUE,
        HOW_MANY_DAYS_TO_ADD):
    print("Getting all the movies...")
    JSON_MOVIE_URL = format_url_string(MOVIE_URL_START,
        MOVIE_URL_END_POINT,
        MOVIE_URL_LANGUAGE,
        MOVIE_URL_PAGE,
        PAGENUMBER,
        MOVIE_URL_REGION)
    MOVIES.clear()
    today = get_today()
    i = 0
    while CONTINUE:
        try:
            magtag.network.connect()
            raw_data = json.loads(magtag.fetch())
            results_data = raw_data['results']
            MOVIES = movie_loop(today, raw_data, results_data, HOW_MANY_DAYS_TO_ADD)
            total_pages = raw_data['total_pages']
            if PAGENUMBER <= total_pages:
                PAGENUMBER += 1
                JSON_MOVIE_URL_NEXT_PAGE = format_url_string(MOVIE_URL_START,
                    MOVIE_URL_END_POINT,
                    MOVIE_URL_LANGUAGE,
                    MOVIE_URL_PAGE,
                    PAGENUMBER,
                    MOVIE_URL_REGION)
                magtag.url = JSON_MOVIE_URL_NEXT_PAGE
            elif PAGENUMBER > raw_data['total_pages']:
                print("Got all the movies released this week.")
                CONTINUE = False
                return MOVIES
        except (ValueError, RuntimeError) as e:
            print("Failed to connect to themovieb.org. Rebooting in 3 seconds...", e)
            time.sleep(3)

# runs the program
MOVIES = get_movie_info(MOVIE_URL_START,
        MOVIE_URL_END_POINT,
        MOVIE_URL_LANGUAGE,
        MOVIE_URL_PAGE,
        PAGENUMBER,
        MOVIE_URL_REGION,
        MOVIES,
        CONTINUE,
        HOW_MANY_DAYS_TO_ADD)

def display_movies(MOVIES,
    title_text_area,
    release_date_text,
    details_text,
    main_group,
    WRAP_TEXT):
    # Display each movie information as a group
    i = 0
    print("There are ", len(MOVIES), " to go through")
    for movie in MOVIES:
        TITLE = movie['title']
        DATE = movie['release_date']
        OVERVIEW = movie['overview']
        # Title
        title_text_area.text = TITLE
        title_text_area.x = 10
        title_text_area.y = 10
        main_group.append(title_text_area)
        # Date
        release_date_text.text = DATE
        release_date_text.x = 10
        release_date_text.y = 30
        main_group.append(release_date_text)
        # Overview
        details_text.text = "\n".join(wrap_text_to_pixels(OVERVIEW, WRAP_TEXT))
        details_text.x = 10
        details_text.y = 50
        main_group.append(details_text)
        #print("Movie Details: ", OVERVIEW)
        display.root_group = main_group
        display.refresh()
        time.sleep(READ_TIME)
        while len(main_group) >1:
            main_group.pop()

while True:
    display_movies(MOVIES, title_text_area, release_date_text, details_text, main_group, WRAP_TEXT)
    time.sleep(60*60*60)
