import codecs
import shutil
from datetime import datetime

import os
import yaml
from bs4 import BeautifulSoup

from src.formatter import Formatter
from src.requester import Requester


class GetMingle:
    def __init__(self):
        with open('config.yml', 'r') as f:
            config = yaml.load(f)
        self.host = config['auth_info']['host']
        self.project = config['auth_info']['project']
        user_name = config['auth_info']['user_name']
        secret_key = config['auth_info']['secret_key']
        self.requester = Requester(self.host, self.project, user_name, secret_key)

        with open('page_templates/index.html', 'r') as f:
            template = BeautifulSoup(f.read(), 'html.parser')
        self.template = template
        self.formatter = Formatter(self.template)

        self.status = config['query_info']['status']

    @staticmethod
    def _get_number_name_map_from_xml(xml: str):
        soup = BeautifulSoup(xml, 'xml')
        the_map = {}
        for result in soup.find_all('result'):
            the_map[result.number.text] = result.find('name').text
        return the_map

    @staticmethod
    def _list_to_str(ths_list):
        string = '('
        for s in ths_list:
            string += s + ','
        string = string[:-1] + ')'
        return string

    def get_iterations_map(self):
        xml = self.requester.get_cards_by_mql('SELECT Number, Name where Type = Iteration')
        return self._get_number_name_map_from_xml(xml)

    def get_cards_list_by_iteration(self, iteration_number):
        iteration_str = self._list_to_str(iteration_number)
        xml = self.requester.get_cards_by_mql(
            "SELECT Number,Name where Status in ('Deployed to Prod','Done') and Iteration NUMBER in" + iteration_str)
        # cards = self._get_number_name_map_from_xml(xml)
        return self._get_number_name_map_from_xml(xml)

    def get_changes_by_card_numbers(self, numbers):
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

    def format_card_status_durations(self, cards, changes):
        self.formatter.format_status_toggles(self.status)
        all_data = self.formatter.format_card_status_durations(changes, self.status)
        self.formatter.format_card_status_data(all_data, self.status, cards,
                                               self.host + '/projects/' + self.project + '/cards')

    def save_result(self):
        directory_name = datetime.now().strftime('result/%Y-%m-%d-%H:%M:%S-result')
        os.mkdir(directory_name)
        with codecs.open(directory_name + '/index.html', 'w', encoding='utf8') as f:
            f.write(str(self.template))
        shutil.copyfile('page_templates/logo.png', directory_name + '/logo.png')


def main():
    getter = GetMingle()
    iterations = getter.get_iterations_map()
    cards = getter.get_cards_list_by_iteration(list(iterations.keys())[:2])
    changes = getter.get_changes_by_card_numbers(list(cards.keys()))
    getter.format_card_status_durations(cards, changes)
    getter.save_result()


if __name__ == '__main__':
    main()
