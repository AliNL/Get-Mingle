import datetime
from bs4 import BeautifulSoup


class Formatter:
    def __init__(self, template: BeautifulSoup, status, url):
        self.template = template
        self.status = status
        self.url = url
        self.all_data = {}
        self.colors = ['rgba(229,115,115,1)', 'rgba(186,104,200,1)', 'rgba(121,134,203,1)',
                       'rgba(79,195,247,1)', 'rgba(77,182,172,1)', 'rgba(174,213,129,1)',
                       'rgba(255,241,118,1)', 'rgba(255,183,77,1)', 'rgba(240,98,146,1)',
                       'rgba(149,117,205,1)', 'rgba(100,181,246,1)', 'rgba(77,208,225,1)',
                       'rgba(129,199,132,1)', 'rgba(220,231,117,1)', 'rgba(255,213,79,1)',
                       'rgba(255,138,101,1)']

    def format_status_toggles(self):
        parent_tag = self.template.find('div', class_='status-toggles')
        for status_key in self.status:
            insert_tag = self.template.new_tag('div')
            insert_tag['class'] = 'status-toggle'
            insert_tag['name'] = str(status_key)
            check_box = self.template.new_tag('span')
            check_box['class'] = 'color-check-box'
            color = self.colors[status_key]
            check_box['style'] = f'background-color: {color};border: solid {color} 3px;'
            status_name = self.template.new_tag('span')
            status_name['class'] = 'status-name'
            status_name.string = self.status[status_key]

            insert_tag.append(check_box)
            insert_tag.append(status_name)
            parent_tag.append(insert_tag)

    def format_card_durations_chart(self, cards):
        script_tag = self.template.find_all('script')[-1].string
        all_status = self.status.values()
        self.all_data = {status: [] for status in all_status}
        labels = str(['#' + card.number for card in cards])
        for card in cards:
            for status in self.all_data:
                self.all_data[status].append(card.durations[status])
        data_str = self._get_data_str_from_all_data()
        script_tag.insert_before('\nvar card_numbers = ' + labels + ';')
        script_tag.insert_before('\nvar all_data = ' + data_str + ';')

    def format_card_durations_data(self, cards):
        table_tag = self.template.find('table', id='statusDurationsData')
        table_tag.append(self._get_tr_th_from_data('Card', list(self.status.values())))
        average_data = ['%.2f' % (sum(self.all_data[status]) / len(cards)) for status in self.status.values()]
        table_tag.append(self._get_tr_th_from_data('Average', average_data))

        for card in cards:
            table_tag.append(self._get_tr_td_from_card(card))

    def _get_tr_th_from_data(self, title, data):
        tr_tag = self.template.new_tag('tr')
        th_tag = self.template.new_tag('th')
        th_tag['style'] = 'background-color: rgba(109,196,203,1);'
        th_tag.string = title
        tr_tag.append(th_tag)

        for i in range(len(data)):
            td_tag = self.template.new_tag('th')
            td_tag['style'] = f"background-color: {self.colors[i]};"
            td_tag.string = str(data[i])
            tr_tag.append(td_tag)
            i += 1
        return tr_tag

    def _get_tr_td_from_card(self, card):
        tr_tag = self.template.new_tag('tr')
        card_td_tag = self.template.new_tag('td')
        card_td_tag['style'] = 'background-color: rgba(109,196,203,0.3);'
        card_a_tag = self.template.new_tag('a')
        card_a_tag.string = '#' + card.number
        card_a_tag['title'] = card.title
        card_a_tag['href'] = self.url + card.number

        card_td_tag.append(card_a_tag)
        tr_tag.append(card_td_tag)

        i = 0
        for status in card.durations:
            td_tag = self.template.new_tag('td')
            td_tag['style'] = f"background-color: {self.colors[i].replace('1)', '0.3)')};"
            td_tag.string = str(card.durations[status])
            tr_tag.append(td_tag)
            i += 1
        return tr_tag

    def _get_data_str_from_all_data(self):
        data_str = "["
        i = 0
        for data in self.all_data:
            data_str += "{"
            data_str += f"label: '{data}',"
            data_str += "data: " + str(self.all_data[data]) + ","
            data_str += "backgroundColor: '" + self.colors[i] + "'"
            data_str += "},"
            i += 1
        data_str = data_str[:-1] + "]"
        return data_str
