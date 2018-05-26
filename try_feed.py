import requests
import mongoengine
import telethon
import time
import os
import sys

# constants
HOST = os.environ.get('MONGODB_HOST')
DATABASE = os.environ.get('MONGODB_DB', 'upwork')
CHANNEL = os.environ.get('TG_CHANNEL')
MYUSERNAME = os.environ.get('MYUSERNAME', 'IbnAmin')

API_ID = os.environ.get('API_ID') 
API_HASH = os.environ.get('API_HASH')

if not HOST:
    print('please provide the MONGODB_HOST environment variable as mongodb host string')
    sys.exit()

if not CHANNEL:
    print('please provide the TG_CHANNEL environment variable ')
    sys.exit()

if not API_ID:
    print('please provide the API_ID environment variable ')
    sys.exit()

if not API_HASH:
    print('please provide the API_HASH environment variable ')
    sys.exit()

RSS2JSONBASE = "https://api.rss2json.com/v1/api.json?rss_url="



mongoengine.connect(DATABASE, host=HOST)

t_client = telethon.TelegramClient('upwork-rss', API_ID, API_HASH )
t_client.start()

channel = t_client.get_entity(CHANNEL)

class Url(mongoengine.Document):
    title = mongoengine.StringField()
    url = mongoengine.StringField()

class Item(mongoengine.Document):
    guid = mongoengine.StringField()
    title = mongoengine.StringField()
    description = mongoengine.StringField()

    def __str__(self):
        return self.title

while True:
    for url in Url.objects:
        print("processing " + url.title)
        t_client.send_message(MYUSERNAME, "ini sedang memulai proses untuk " + url.title)
        to_get = RSS2JSONBASE + url.url
        resp = requests.get(to_get)

        # loop through items
        try:
            for item in resp.json()['items']:
                found = Item.objects(guid=item['guid']).first()

                if not found:
                    to_save = Item(title=item['title'], guid=item['guid'], description=item['description'])
                    to_save.save()
                    message = "<b>" + to_save.title + "</b>\n\n\n"
                    message += to_save.description.replace("<br>", "\n").replace("<br/>", "\n")

                    t_client.send_message(channel, message, parse_mode="html", link_preview=False)
                    time.sleep(5)
        except KeyError:
            t_client.send_message(MYUSERNAME, "ada error di url " + url.url)
            t_client.send_message(MYUSERNAME, "please check")
            t_client.send_message(MYUSERNAME, "```" + resp.content + "```")
        except Exception as e:
            t_client.send_message(MYUSERNAME, "another error, please check the script")
            t_client.send_message(MYUSERNAME, "```" + str(e) + "```")

    time.sleep(10 * 60)

