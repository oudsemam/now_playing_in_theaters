# MagTag Now Playing In Theaters v1.0 (last updated 2/25/2025)
by: Maggie Oudsema
By using the data from themoviedb.org v3 API which has multiple API points, this is just 1 of them which is their 'Now Playing' endpoint: https://api.themoviedb.org/3/movie/now_playing to get, pars/filter JSON data, and display the movie Title, Release Date, and short description (a.k.a. Overview). This uses some of the Adafruit libraries that are built as part of their other products and projects.

# Links:
- Link to project: https://github.com/oudsemam/now_playing_in_theaters.git
- Link to TMDB API documentation: https://developer.themoviedb.org/reference/intro/getting-started
- MagTag CircuitPython: https://circuitpython.org/board/adafruit_magtag_2.9_grayscale/
- Link to Adafruit CircuitPython Library Bundle: https://docs.circuitpython.org/projects/bundle/en/latest/

# Build Requirements:
- Adafruit CircuitPython 9.2.4 on 2025-01-29
- Adafruit MagTag with ESP32S2
- Board: adafruit_magtag_2.9_grayscale


# Required Libraries:
These files should be held in a file on the drive named "lib". 
- adafruit_bitmap_font
- adafruit_connection_manager.mpy
- adafruit_datetime.mpy
- adafruit_display_text
- adafruit_fakerequests.mpy
- adafruit_io
- adafruit_magtag
- adafruit_minimqtt
- adafruit_miniqr.mpy
- adafruit_pixelbuf.mpy
- adafruit_portalbase
- adafruit_requests.mpy
- adafruit_ticks.mpy
- neopixel.mpy
- simpleio.mpy


# Creating and Connecting MagTag to https://io.adafruit.com/ 
(More detailed information can be found here: https://learn.adafruit.com/adafruit-magtag/getting-the-date-time)
1) Create an Adafruit account: It's free to register and make an account if you don't have one already.
2) Sign into your account if it doesn't do so automatically.
3) Get your Adafruit IO Key: click on "My Key" in the top bar. You should get a popup with your "Username" and "Activity Key".
4) Create or open settings.toml on the drive ad add the lines for the 'AIO_USERNAME', 'ADAFRUIT_AIO_KEY' and 'TIMEZONE'.
5) Also copy these into your secrets.py file as well for 'aio_username' and 'aio_key'.


# Create a TMDB account and API key and token 
It is also free to create. Please refer to the documentation associated with the TMDB API here: https://developer.themoviedb.org/reference/intro/getting-started


# Required Files:
These files you will need to create (they are NOT included) as they will contain the secrets and tokens which will be used. Please be sure not to include these files in your own repository or share with others. Replace the items that begin with 'your'
- secrets.py
- settings.toml

1) secrets.py will hold the following information please keep the nameing the same or make sure you change variables:
secrets = {
    'ssid' : 'YOUR_WIFI_NAME',
    'password' : 'YOUR_WIFI_PASSWORD',
    'aio_username' : 'YOUR_AIO_USERNAME',
    'aio_key' : 'YOUR_ADAFRUIT_AIO_KEY',
    'tmdb_key' : 'your_tmdb_key',
    'tmdb_access_token' : 'your_tmdb_access_token',
}

2) settings.toml will hold similar information as your secrets.py but please note the structure/name changes in variables:
CIRCUITPY_WIFI_SSID = "YOUR_WIFI_NAME"
CIRCUITPY_WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
AIO_USERNAME = "YOUR_AIO_USERNAME"
AIO_KEY = "YOUR_ADAFRUIT_AIO_KEY"
TMBD_TOKEN = "your_tmdb_access_token"
TMDB_KEY = "your_tmdb_key"

# Installing
The files need to be placed on your MagTag which MUST already have CircitPython installed. Again directions can be found on Adafruit.com under their learning section. Once this is done you can drag and drop some files or use their Mu editor or VS code to create the other needed files.
1) create secrets.py and settings.toml files.
2) Install rquired libraries in a 'lib' folder
3) Drag and drop the 