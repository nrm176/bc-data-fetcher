import sqlite3
import pathlib
import csv
import requests
import json
import os
from os.path import join, dirname
from dotenv import load_dotenv
from lib.logtaker import logger
import random
import time
import sys

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class DownloadHanlder(object):

    @classmethod
    def split_list(cls, _list, x):
        return [_list[i:i + x] for i in range(0, len(_list), x)]

    @classmethod
    def load_company_codes(cls):
        codes = []
        with open('./stocklist.csv', 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                codes.append(row[0])
        return codes

    @classmethod
    def build_year_and_quarter(cls, start_year):
        end_year = start_year - 8
        quaters = ['Q1', 'Q2', 'Q3', 'Q4']
        yqs = []
        while True:
            for quater in quaters:
                yqs.append('{}{}'.format(end_year, quater))
            end_year += 1
            if end_year > start_year:
                break

        yqs = cls.split_list(yqs, 12)
        return [(yq[0], yq[-1:][0]) for yq in yqs]

    @classmethod
    def send_request(cls, tickers, _from, _to):
        try:
            response = requests.get(
                url=os.environ['API_URL'],
                params={
                    "tickers": tickers,
                    "from": _from,
                    "to": _to,
                },
                headers={
                    "x-api-key": os.environ['API_KEY'],
                },
            )
            return response.json()
        except requests.exceptions.RequestException:
            logger.error('HTTP Request failed')

    @classmethod
    def save_json(cls, data, tickers, _from, _to):
        with open('./json/{}-{}-{}.json'.format(tickers.replace(',', '_'), _from, _to), 'w') as outfile:
            json.dump(data, outfile)
        logger.info('saved')

    @classmethod
    def count_existing_json_file(cls):
        return len(list(pathlib.Path('./json').glob('*')))

    @classmethod
    def run(cls, num_of_requests):
        codes = cls.load_company_codes()
        codes = cls.split_list(codes, 3)
        tickers = [','.join(code) for code in codes]
        values = cls.build_year_and_quarter(2019)

        request_lists = []
        for ticker in tickers:
            for value in values:
                logger.info('requesting {0} for {1}-{2}'.format(ticker, value[0], value[1]))
                request_lists.append({'tickers': ticker, '_from': value[0], '_to': value[1]})
        start = cls.count_existing_json_file()
        logger.info('start from {}th element'.format(start))

        for request in request_lists[start:start+int(num_of_requests)]:
            logger.info('sending a request for {} from {} to {}'.format(request['tickers'], request['_from'], request['_to']))
            d = cls.send_request(request['tickers'], request['_from'], request['_to'])

            if d.get("message") == "Limit Exceeded":
                logger.error('request limit exceeded')
                sys.exit()
            cls.save_json(d, request['tickers'], request['_from'], request['_to'])
            time.sleep(random.uniform(0, 1) * 5.0)
