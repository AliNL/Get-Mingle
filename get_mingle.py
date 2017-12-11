import codecs
from datetime import datetime, timedelta

import os
import yaml
from bs4 import BeautifulSoup

from src.card import Card
from src.formatter import Formatter
from src.iteration import Iteration
from src.requester import Requester


class GetMingle:
    def __init__(self):
        with open('config.yml', 'r') as f:
            config = yaml.load(f)
        with open('page_templates/index.html', 'r') as f:
            template = BeautifulSoup(f.read(), 'html.parser')

        self.host = config['auth_info']['host']
        self.project = config['auth_info']['project']
        user_name = config['auth_info']['user_name']
        secret_key = config['auth_info']['secret_key']
        url = self.host + '/projects/' + self.project + '/cards/'
        self.template = template
        self.status = config['query_info']['status']

        self.requester = Requester(self.host, self.project, user_name, secret_key)
        self.formatter = Formatter(self.template, self.status, url)

    def get_current_iteration(self):
        today = datetime.today()
        this_monday = (today - timedelta(today.weekday())).strftime('%Y-%m-%d')
        xml = self.requester.get_cards_by_mql(f"SELECT Number, Name where Name = '{this_monday}'")
        soup = BeautifulSoup(xml, 'xml')
        number = soup.find('number').string
        title = soup.find('name').string
        return Iteration(number, title, ['In-Progress', 'In QA'])

    def get_cards_by_iteration(self, iteration: Iteration):
        xml = self.requester.get_cards_by_mql(
            "SELECT Number,Name,'Estimated Points' " \
            + "where Status in ('Deployed to Prod','Done') and Iteration = NUMBER " + iteration.number)
        soup = BeautifulSoup(xml, 'xml')
        cards = []
        numbers = []
        for result in soup.find_all('result'):
            number = result.find('number').string
            numbers.append(number)
            title = result.find('name').string
            points = result.find('estimated_points').string
            cards.append(Card(number, title, points, self.status, 'In-Progress'))
        changes = self._get_changes_by_card_numbers(numbers)
        for card in cards:
            card.changes = changes[card.number]
            card.init()
        return cards

    def _get_changes_by_card_numbers(self, numbers):
        not_finished = numbers[:]
        changes = {number: [] for number in numbers}
        next_page = None
        while not_finished:
            xml = self.requester.get_events(next_page)
            soup = BeautifulSoup(xml, 'xml')
            next_page = soup.find('link', rel='next')['href']
            entries = soup.find_all('entry')
            for entry in entries:
                card_title = entry.title.text
                number_mark = card_title.find('#') + 1
                card_number = card_title[number_mark:card_title.find(' ', number_mark)]
                if card_number in numbers:
                    changes[card_number].append(entry)
                    if entry.find('change', type='card-creation'):
                        not_finished.remove(card_number)
                        changes[card_number].reverse()
                        if not not_finished:
                            break
        return changes

    def format_index(self, iteration, cards):
        self.formatter.format_iteration_data(iteration)
        self.formatter.format_iteration_chart(iteration)
        self.formatter.format_status_toggles()
        self.formatter.format_card_durations_chart(cards)
        self.formatter.format_card_durations_data(cards)

    def save_result(self):
        directory_name = datetime.now().strftime('result/%Y-%m-%d-%H:%M:%S-result')
        os.mkdir(directory_name)
        with codecs.open(directory_name + '/index.html', 'w', encoding='utf8') as f:
            f.write(str(self.template))


def main():
    getter = GetMingle()
    current_iteration = getter.get_current_iteration()
    cards = getter.get_cards_by_iteration(current_iteration)
    current_iteration.get_cards_data(cards)
    getter.format_index(current_iteration, cards)
    getter.save_result()


if __name__ == '__main__':
    main()
