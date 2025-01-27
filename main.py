import requests
import time
import datetime
from discord_webhook import DiscordWebhook
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import json

load_dotenv()
DISCROD_URL = os.getenv('DISCROD_URL')

def get_timestamp():
    return str(round(int(datetime.datetime.timestamp(datetime.datetime.strptime(datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d'), '%Y/%m/%d')))))

def get_menu(timestamp):
    timestamp='1738320300' # usun
    r = requests.get(f'https://technischools.bistrokoziolek.pl/set-search/stolowka/4462/Technischools/{timestamp}')
    soup = BeautifulSoup(r.text, 'html.parser')


    menu_list = list(soup.find_all('div', class_='dish-text'))
    pretty_list = []
    fields = []
    inline_counter = 0

    for i in menu_list:
        title = i.span.a.text
        price = i.find('span', class_='js-dPrice').text
        desc = i.find('div', class_='desc').text if i.find('div', class_='desc') else ''
        if inline_counter % 3 == 0:
            fields.append({"name": title, "value": f"{price} \n\n {desc}", "inline": True})
            fields.append({"name": "\t", "value": "\t"})
        else:
            fields.append({"name": title, "value": f"{price} \n\n {desc}", "inline": True})
        inline_counter += 1

    return fields[:-3]

def send_message(fields):
    with open('message.json', 'r', encoding='utf-8') as file:
        message = json.load(file)

    message['embeds'][0]['fields'] = fields

    print(message)

    response = requests.post(DISCROD_URL, json=message)
    print(response)

    return response

if __name__ == "__main__":
    fields = get_menu(get_timestamp())
    send_message(fields)