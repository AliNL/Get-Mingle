import yaml
from src.requester import Requester
from bs4 import BeautifulSoup


class GetMingle:
    def __init__(self):
        with open('config.yml', 'r') as f:
            config = yaml.load(f)

        host = config['auth_info']['host']
        project = config['auth_info']['project']
        user_name = config['auth_info']['user_name']
        secret_key = config['auth_info']['secret_key']

        self.requester = Requester(host, project, user_name, secret_key)
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

    def get_cards_map_by_iteration(self, iteration_number):
        iteration_str = self._list_to_str(iteration_number)
        xml = self.requester.get_cards_by_mql(
            "SELECT Number, Name where Status in ('Deployed to Prod','Done') and Iteration NUMBER in" + iteration_str)
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
                # print(card_title)
                number_mark = card_title.find('#') + 1
                card_number = card_title[number_mark:card_title.find(' ', number_mark)]
                if card_number in numbers:
                    # changes[card_number].append(entry)
                    print(card_number)
                    changes[card_number].append(entry.title.text)
                    if entry.find('change', type='card-creation'):
                        print(card_number, entry.find('change', type='card-creation'))
                        not_finished.remove(card_number)
                        if not not_finished:
                            break
                        changes[card_number].reverse()
        return changes


def main():
    getter = GetMingle()
    iterations = getter.get_iterations_map()
    cards = getter.get_cards_map_by_iteration(list(iterations.keys())[:2])
    print(cards)
    changes = getter.get_changes_by_card_numbers(list(cards.keys()))
    print(changes)


if __name__ == '__main__':
    main()
