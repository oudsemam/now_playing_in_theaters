import os
import time
import board
import terminalio
import displayio
import json
from adafruit_datetime import date, datetime
from adafruit_bitmap_font import bitmap_font
from adafruit_magtag.magtag import MagTag
from adafruit_display_text import label, wrap_text_to_pixels, scrolling_label


#Getting today's date variables
aio_username = os.getenv("ADAFRUIT_AIO_USERNAME")
aio_key = os.getenv("ADAFRUIT_AIO_KEY")
timezone = os.getenv("TIMEZONE")
TIME_URL = f"https://io.adafruit.com/api/v2/{aio_username}/integrations/time/strftime?x-aio-key={aio_key}&tz={timezone}"
TIME_URL += "&fmt=%25Y-%25m-%25d+%25H%3A%25M%3A%25S.%25L+%25j+%25u+%25z+%25Z"

# headers for the call
TMBD_TOKEN = str(os.getenv("TMBD_TOKEN"))
HEADERS = dict(accept = "application/json", Authorization="Bearer "+TMBD_TOKEN)
# sets variables
PAGENUMBER = 1
JSON_MOVIE_URL = "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page="+str(PAGENUMBER)+"&region=US"
MOVIES = []
magtag = MagTag(url=JSON_MOVIE_URL, headers=HEADERS, json_path=MOVIES)
# variables for other functions
READ_TIME = 5
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

# define functions
def string_to_date(string):
    isoformat = datetime.fromisoformat(string)
    return isoformat

def filter_by_date(max_date, release_date):
    near_today = string_to_date(max_date)
    movie_release_date = string_to_date(release_date)
    add_movie = near_today > movie_release_date
    return add_movie

def movie_loop(raw_data, MOVIES):
    if len(raw_data['results']) > 0:
        movies = raw_data['results']
        for movie in movies:
            add_movie = filter_by_date(raw_data['dates']['maximum'], movie['release_date'])
            if add_movie:
                movie_data = {}
                movie_data["title"] = movie['title']
                movie_data["release_date"] = movie['release_date']
                movie_data["overview"] = movie['overview']
                MOVIES.append(movie_data)
    return MOVIES

def get_movie_info(JSON_MOVIE_URL, PAGENUMBER, MOVIES, CONTINUE):
    MOVIES.clear()
    while CONTINUE:
        try:
            magtag.network.connect()
            raw_data = json.loads(magtag.fetch(auto_refresh=False))
            # print(raw_data['dates'])
            results_data = raw_data['results']
            MOVIES = movie_loop(raw_data, MOVIES)
            total_pages = raw_data['total_pages']
            if PAGENUMBER <= total_pages:
                PAGENUMBER += 1
                JSON_MOVIE_URL = "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page="+str(PAGENUMBER)+"&region=US"
                magtag.url = JSON_MOVIE_URL
            elif PAGENUMBER > raw_data['total_pages']:
                print("Got all the movies released this week.")
                CONTINUE = False
                return MOVIES
        except (ValueError, RuntimeError) as e:
            print("Failed to connect to themovieb.org. Rebooting in 3 seconds...", e)
            time.sleep(3)

# runs the program
MOVIES = get_movie_info(JSON_MOVIE_URL, PAGENUMBER, MOVIES, CONTINUE)

def display_movies(MOVIES, title_text_area, release_date_text, details_text, main_group, WRAP_TEXT):
    # Display all calendar events
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
        time.sleep(10) # 45 seconds seeems long enough
        while len(main_group) >1:
            main_group.pop()

display_movies(MOVIES, title_text_area, release_date_text, details_text, main_group, WRAP_TEXT)

#while True:
#    display_movies(MOVIES, title_text_area, release_date_text, main_group)
#    pass
# print("Sleeping for %d minutes" % WAIT)
magtag.exit_and_deep_sleep(WAIT * 60)
