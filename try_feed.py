import html
import feedparser
import mongoengine
import telethon
import time
import os



# constants

MONGODB_NAME = "upwork"
MONGODB_HOST = os.environ.get("MONGODB_HOST")

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

USERNAME = os.environ.get("USERNAME")
CHANNEL_URL = os.environ.get("CHANNEL_URL")


mongoengine.connect(MONGODB_NAME, host=MONGODB_HOST)


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
    t_client = telethon.TelegramClient('session', API_ID, API_HASH )
    t_client.start()

    channel = t_client.get_entity(CHANNEL_URL)

    for url in Url.objects:
        print("processing " + url.title)
        resp = feedparser.parse(url.url)
        resp.entries.reverse()



        # loop through items
        try:
            for item in resp.entries:
                found = Item.objects(guid=item.guid)


                if found.count() == 0:
                    to_save = Item(title=item.title,
                                   guid=item.guid,
                                   description=item.summary
                                   )
                    to_save.save()

                    message = "###################\n\n\n"
                    message += "<b>" + to_save.title + "</b>\n\n\n"
                    message += to_save.description.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n").replace("<br >", "\n")
                    message += "##################"

                    t_client.send_message(channel, html.unescape(message), parse_mode="html", link_preview=False)
                    t_client.send_message(channel, "#---> " + url.title)
                    time.sleep(5)
        except KeyError:
            t_client.send_message(USERNAME, "ada error di url " + url.url)
            t_client.send_message(USERNAME, "please check")
            t_client.send_message(USERNAME, "```" + resp.content + "```")
        except Exception as e:
            t_client.send_message(USERNAME, "another error, please check the script")
            t_client.send_message(USERNAME, "```" + str(e) + "```")

    time.sleep(10 * 60)
