import configparser
import os

import requests as r
import json
from bs4 import BeautifulSoup
import logging
import sys
from datetime import datetime
from typing import List

from notifier.emailer import Emailer

log = logging.getLogger()
log.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', '%m-%d-%Y %H:%M:%S')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('movie_notifier.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

log.addHandler(file_handler)
log.addHandler(stdout_handler)

url = "https://www.amctheatres.com/movies?availability=COMING_SOON"

# Create config file
if not os.path.exists('conf.ini'):
    log.error('conf.ini file does not exist')
    with open('conf.ini', 'x') as f:
        f.write('''[email]
sender=
password=
emails=
''')
    exit(0)

config = configparser.ConfigParser()
config.read('conf.ini')

email_sender = config['email']['sender']
email_password = config['email']['password']
email_to = config['email']['emails'].split(',')


def get_save_data():
    data = {}
    try:
        f = open('save.json', 'r')
        data = json.load(f)
    except FileNotFoundError as fnfe:
        log.warning(fnfe)
    except json.decoder.JSONDecodeError as jde:
        log.warning(jde)

    return data


def does_element_exist(b_soup, selector):
    try:
        result = b_soup.select_one(selector)
        if result is None:
            raise
    except Exception as e:
        return False
    return True


def get_web_data():
    data = {}
    try:
        page = r.get(url=url)
        soup = BeautifulSoup(page.content, "html.parser")
        movies = soup.select('.poster-grid > div .Slide')
        for m in movies:
            m_data = {}
            id = m.select_one('a').get('href').split('-')[-1]
            m_data['title'] = m.select_one('.PosterContent h3').contents.pop()
            m_data['status'] = None if does_element_exist(m, '.PosterContent button span') else m.select_one(
                '.PosterContent div .Btn').contents.pop()
            m_data['last_update'] = str(datetime.now())
            m_data['id'] = id
            data[id] = m_data

    except AttributeError as ae:
        log.error(ae)

    return data


def get_updated_data(save_data: dict, web_data: dict):
    data = save_data
    new_movies: List[str] = []

    for wb in web_data:
        if wb not in save_data:
            data[wb] = web_data[wb]
            if web_data[wb]['status'] is not None:
                new_movies.append(web_data[wb])
        elif save_data[wb]['status'] is None and save_data[wb]['status'] != web_data[wb]['status']:
            data[wb]['status'] = web_data[wb]['status']
            data[wb]['last_update'] = str(datetime.now())
            data[wb]['id'] = web_data[wb]['id']
            new_movies.append(web_data[wb])
            log.info(f'{web_data[wb]["title"]} tickets are now available for purchase')

    if len(new_movies) > 0:
        movies = ''
        for m in new_movies:
            title = m['title']
            id = m['id']
            movies += f'<a href=\'https://www.amctheatres.com/movies/{id}\'>{title}</a><br><br>'
        email = f'''<!DOCTYPE html>
            <html lang="en">
                <b>The following movies now have tickets available:<b><br><br>
                
                {movies}
            </html>
            '''

        e: Emailer = Emailer(email_sender, email_password)
        e.send_email(email_to, 'New Movies Available', email)

    return data


def write_data(data: dict):
    with open('save.json', 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    log.info('Starting Movie Notifier')
    wd = get_web_data()
    sd = get_save_data()
    updated_data = get_updated_data(sd, wd)
    write_data(updated_data)
    log.info('Completed Movie Notifier')

