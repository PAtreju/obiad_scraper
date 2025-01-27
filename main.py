import requests
import time
import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import json
import schedule

load_dotenv()
DISCROD_URL = os.getenv('DISCROD_URL')

def get_timestamp():
    return str(round(int(datetime.datetime.timestamp(datetime.datetime.strptime(datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d'), '%Y/%m/%d')))))

def get_menu(timestamp):
    r = requests.get(f'https://technischools.bistrokoziolek.pl/set-search/stolowka/4462/Technischools/{timestamp}')
    soup = BeautifulSoup(r.text, 'html.parser')

    menu_list = list(soup.find_all('div', class_='dish-text'))[:-3]
    fields = []
    inline_counter = 0

    for i in menu_list:
        title = i.span.a.text
        link = i.span.a['href']
        price = i.find('span', class_='js-dPrice').text
        desc = i.find('div', class_='desc').text if i.find('div', class_='desc') else ''
        if inline_counter % 2 == 0:
            fields.append({"name": "\t", "value": "\t"})
            fields.append({"name": "════════════════════════", "value": "\t", "inline": True})
            fields.append({"name": "════════════════════════", "value": "\t", "inline": True})
            fields.append({"name": "\t", "value": "\t"})
            fields.append({"name": title, "value": f" {desc} \n {price} ● [ORDER]({link})", "inline": True})
        else:
            fields.append({"name": title, "value": f"{desc} \n {price} ● [ORDER]({link})", "inline": True})
        inline_counter += 1

    if len(fields) % 2 != 0:
        fields.append({"name": "\t", "value": "\t", "inline": True})

    return fields

def dsc_post(DISCORD_URL, message_content):
    response = requests.post(DISCORD_URL, json=message_content)
    return response

def send_message():
    fields = get_menu(get_timestamp())
    check_for_last = False

    with open('message.json', 'r', encoding='utf-8') as file:
        message = json.load(file)

    if len(fields) > 25:
        message['embeds'][0]['fields'] = fields[:25]
        dsc_post(DISCROD_URL, message)

        message['embeds'][0]['fields'] = fields[25:50 if len(fields) > 50 else len(fields)]
        message['content'] = ''
        message['embeds'][0]['title'] = ''

        if message['embeds'][0]['fields'][-1] == {"name": "════════════════════════", "value": "\t", "inline": True} and message['embeds'][0]['fields'][-2] != {"name": "════════════════════════", "value": "\t", "inline": True}:
            del (message['embeds'][0]['fields'][-1])
            check_for_last = True

        dsc_post(DISCROD_URL, message)

        if len(fields) > 50:
            if check_for_last:
                message['embeds'][0]['fields'] = [{"name": "════════════════════════", "value": "\t", "inline": True}] + fields[50:]
            else:
                message['embeds'][0]['fields'] = fields[50:]
            message['content'] = ''
            message['embeds'][0]['title'] = ''
            dsc_post(DISCROD_URL, message)
    else:
        message['embeds'][0]['fields'] = fields
        dsc_post(DISCROD_URL, message)

    message['embeds'][0]['fields'] = [{"name": '\t', "value": f"[technischools.bistrokoziolek.pl](https://technischools.bistrokoziolek.pl/set-search/stolowka/4462/Technischools/{get_timestamp()})"}]
    message['content'] = ''
    message['embeds'][0]['title'] = ''

    dsc_post(DISCORD_URL=DISCROD_URL, message_content=message)

    return 0

# Schedule the send_message function to run every day at 8 AM
schedule.every().day.at("08:00").do(send_message)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)