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

def get_location():
    url = 'https://where.virt.ch.bbc.co.uk/api/1/users/n/location.json?auth_token=xxxxxxxxxxx'
    res = requests.get(url)
    if(res.status_code == 200):
        json_data = json.loads(res.text)
        return json_data
    return {}


def main():
    epd = epd2in13b.EPD()
    epd.init()
    epd.set_rotate(1)

    # clear the frame buffer
    frame_black = [0xFF] * (epd.width * epd.height / 8)
    frame_red = [0xFF] * (epd.width * epd.height / 8)

    epd.draw_filled_rectangle(frame_red, 0, 0, 250, 55, COLORED);

    font = ImageFont.truetype('/usr/share/fonts/AmaticSC-Bold.ttf', 38)
    epd.draw_string_at(frame_red, 25, 10, "WHERE IS FOO?", font, UNCOLORED)

    data = get_location()
    ds = "unknown"
    print(data)

    if(u'description' in data):
           print(data["description"])
           ds = data["description"]

    epd.draw_string_at(frame_black, 25, 60, ds, font, COLORED)

    epd.display_frame(frame_black, frame_red)

if __name__ == '__main__':
    main()
