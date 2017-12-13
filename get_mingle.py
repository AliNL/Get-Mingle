import codecs
from datetime import datetime, timedelta, date

import os
import json
from bs4 import BeautifulSoup

from src.card import Card
from src.formatter import Formatter
from src.iteration import Iteration
from src.requester import Requester


class GetMingle:
    def __init__(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
        with open('page_templates/index.html', 'r') as f:
            template = BeautifulSoup(f.read(), 'html.parser')

        self.host = config['auth_info']['host']
        self.project = config['auth_info']['project']
        user_name = config['auth_info']['user_name']
        secret_key = config['auth_info']['secret_key']
        url = self.host + '/projects/' + self.project + '/cards/'
        self.template = template
        self.key_status = config['query_info']['key_status']
        self.status = config['query_info']['status']
        self.query_cards_in = config['query_info']['query_cards_in']
        self.calculate_days_for = config['query_info']['calculate_days_for']
        self.calculate_steps_for = config['query_info']['calculate_steps_for']
        self.time_zone = config['query_info']['time_zone']

        self.requester = Requester(self.host, self.project, user_name, secret_key)
        self.formatter = Formatter(self.template, self.status, url)

    def get_iteration(self, name, start_date, end_date):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        return Iteration(name, start_date, end_date, self.calculate_days_for, self.calculate_steps_for)

    def get_cards_by_iteration(self, iteration: Iteration):
        query_status = '(' + str(self.query_cards_in)[1:-1] + ')'
        xml = self.requester.get_cards_by_mql(
            "SELECT Number,Name,'Estimated Points' " \
            + "where Status in " + query_status + " and Iteration = '" + iteration.title + "'")
        soup = BeautifulSoup(xml, 'xml')
        cards = []
        for result in soup.find_all('result'):
            number = result.find('number').string
            title = result.find('name').string
            points = result.find('estimated_points').string
            cards.append(Card(number, title, points, self.status, self.key_status))
        return cards

    def get_info_of_iteration_and_cards(self, iteration, cards):
        not_finished_cards = {card.number: card for card in cards}
        not_finished_iteration = True
        next_page = None
        while not_finished_cards or not_finished_iteration:
            xml = self.requester.get_events(next_page)
            soup = BeautifulSoup(xml, 'xml')
            next_page = soup.find('link', rel='next')['href']
            entries = soup.find_all('entry')

            for entry in entries:
                if not (not_finished_cards or not_finished_iteration):
                    break

                update_time = datetime.strptime(entry.updated.string, '%Y-%m-%dT%H:%M:%SZ') + timedelta(
                    hours=int(self.time_zone))
                entry.updated.string = update_time.strftime('%Y-%m-%dT%H:%M:%SZ')
                if not_finished_iteration:
                    not_finished_iteration = self.modify_iteration_from_entry(entry, update_time, iteration)

                if not_finished_cards:
                    self.modify_cards_from_entry(entry, not_finished_cards)

        iteration.cards = cards
        iteration.init()

    @staticmethod
    def modify_iteration_from_entry(entry, update_time, iteration):
        if iteration.start_date < update_time <= iteration.end_date:
            iteration.changes.append(entry)
        elif update_time < iteration.start_date:
            iteration.changes.reverse()
            return False
        return True

    @staticmethod
    def modify_cards_from_entry(entry, not_finished_cards):
        card_title = entry.title.string
        number_mark = card_title.find('#') + 1
        card_number = card_title[number_mark:card_title.find(' ', number_mark)]
        if card_number in not_finished_cards:
            card = not_finished_cards[card_number]
            card.changes.append(entry)
            if entry.find('change', type='card-creation'):
                card.changes.reverse()
                card.init()
                not_finished_cards.pop(card_number)

    def format_index(self, iteration, cards):
        self.formatter.format_iteration_data(iteration)
        self.formatter.format_iteration_chart(iteration)
        self.formatter.format_status_toggles()
        self.formatter.format_card_durations_chart(cards)
        self.formatter.format_card_durations_data(cards)

    def save_result(self):
        directory_name = datetime.now().strftime('result/%Y%m%d-%H%M%S')
        os.mkdir(directory_name)
        with codecs.open(directory_name + '/index.html', 'w', encoding='utf8') as f:
            f.write(str(self.template))


def main():
    getter = GetMingle()
    iteration = getter.get_iteration(name='2017-12-04', start_date='2017-12-05', end_date='2017-12-12')
    cards = getter.get_cards_by_iteration(iteration)
    getter.get_info_of_iteration_and_cards(iteration, cards)
    getter.format_index(iteration, cards)
    getter.save_result()


if __name__ == '__main__':
    main()
