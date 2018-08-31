#!/usr/bin/env python

##
# whereis.py
##
# This script updates a Waveshare 2.13inch three-colour e-Paper HAT
# with status information taken from BBC Whereabouts.
#
# Author: Libby Miller <libby.miller@bbc.co.uk>
# Author: Henry Cooke <henry.cooke@bbc.co.uk>
#
##

import epd2in13b
import time
import Image
import ImageDraw
import ImageFont
import json

COLORED = 1
UNCOLORED = 0

try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")


def get_location( user_number, auth_token ):
    url = 'https://where.virt.ch.bbc.co.uk/api/1/users/%s/location.json?auth_token=%s' % (
        user_number,
        auth_token
    )
    res = requests.get(url)
    if(res.status_code == 200):
        json_data = json.loads(res.text)
        return json_data
    return {}


def load_config():
    lines = []
    with open( "/home/pi/rpi-whereis-0.1/config.txt" ) as f:
        lines = f.read().splitlines()
    return {
        "caption" : lines[0],
        "user_number" : lines[1],
        "auth_token" : lines[2],
        "old_ds" : lines[3]
}


def save_config(ds):
    with open( "/home/pi/rpi-whereis-0.1/config.txt", 'r' ) as f:
        lines = f.readlines()
    lines[3] = ds+"\n"
    with open("/home/pi/rpi-whereis-0.1/config.txt", 'w') as f:
        f.writelines(lines)


def main():
    
    config = load_config()
    
    epd = epd2in13b.EPD()
    epd.init()
    epd.set_rotate(1)
    
    # clear the frame buffer
    frame_black = [0xFF] * (epd.width * epd.height / 8)
    frame_red = [0xFF] * (epd.width * epd.height / 8)
    
    epd.draw_filled_rectangle(frame_red, 0, 0, 250, 55, COLORED);
    
    font = ImageFont.truetype('/usr/share/fonts/AmaticSC-Bold.ttf', 38)
    epd.draw_string_at(frame_red, 25, 10, config["caption"], font, UNCOLORED)
    
    data = get_location( config["user_number"], config["auth_token"] )
    ds = "unknown"
    print(data)
    
    if(u'description' in data):
           print(data["description"])
           ds = data["description"]
    
    epd.draw_string_at(frame_black, 25, 60, ds, font, COLORED)
    
    if (config["old_ds"] != ds):
        epd.display_frame(frame_black, frame_red)
    
    save_config(ds)


if __name__ == '__main__':
    main()

