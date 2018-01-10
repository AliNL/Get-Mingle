from bs4 import BeautifulSoup


class Formatter:
    def __init__(self, template: BeautifulSoup, status, key_status, url):
        self.template = template
        self.status = status
        self.key_status = key_status
        self.url = url
        self.all_data = {}
        self.colors = ['rgba(229,115,115,1)', 'rgba(186,104,200,1)', 'rgba(121,134,203,1)',
                       'rgba(79,195,247,1)', 'rgba(77,182,172,1)', 'rgba(174,213,129,1)',
                       'rgba(255,241,118,1)', 'rgba(255,183,77,1)', 'rgba(240,98,146,1)',
                       'rgba(149,117,205,1)', 'rgba(100,181,246,1)', 'rgba(77,208,225,1)',
                       'rgba(129,199,132,1)', 'rgba(220,231,117,1)', 'rgba(255,213,79,1)',
                       'rgba(255,138,101,1)']
        self.script_tag = self.template.find('script', type='text/javascript').string

    def format_iteration_chart(self, iteration):
        data_str = '['
        for step in iteration.steps:
            data_str += "{"
            data_str += f"x: '{step}',"
            data_str += "y: " + str(iteration.steps[step])
            data_str += "},"
        data_str = data_str[:-1] + ']'
        self.script_tag.insert_before('\nvar steps_data = ' + data_str + ';')

    def format_iteration_data(self, iteration):
        section = self.template.find('div', id='iteration-summary-section')
        section.h2.string.insert_after(iteration.title)
        data_part = self.template.find('div', class_='iteration-summary-data')

        data_part.append(self._new_tag('h3', 'Total Points: ' + str(iteration.sum_points)))
        data_part.append(self._new_tag('h3', 'Total Movements: ' + str(iteration.sum_steps)))
        for status in iteration.sum_days:
            data_part.append(
                self._new_tag('h3', 'Total Days for "' + status + '": ' + '%.2f' % iteration.sum_days[status]))

    def format_unusual_cards(self, cards):
        section = self.template.find('div', class_='unusual-cards-section')
        moved_back_section = section.find('div', class_='unusual-cards-sub-section left')
        changed_section = section.find('div', class_='unusual-cards-sub-section right')
        moved_back_section.h3['title'] = moved_back_section.h3.string + f' after moved to "{self.key_status}"'
        changed_section.h3['title'] = changed_section.h3.string + f' after moved to "{self.key_status}"'
        for card in cards:
            if card.moved_back:
                if moved_back_section.find('span'):
                    moved_back_section.find('span').decompose()
                moved_back_section.append(
                    self._new_tag('a', '#' + card.number + ' ' + card.title, {'href': self.url + card.number}))
            if card.description_changed:
                if changed_section.find('span'):
                    changed_section.find('span').decompose()
                changed_section.append(self._new_tag('a', self.url + card.number, {'href': self.url + card.number}))

    def format_status_toggles(self):
        parent_tag = self.template.find('div', class_='status-toggles')
        for i in range(len(self.status)):
            insert_tag = self._new_tag('div', parameters={'class': 'status-toggle', 'name': str(i)})

            color = self.colors[i]
            insert_tag.append(self._new_tag(
                'span', parameters={'class': 'color-check-box',
                                    'style': f'background-color: {color};border: solid {color} 3px;'}))
            insert_tag.append(self._new_tag('span', self.status[i], {'class': 'status-name'}))

            parent_tag.append(insert_tag)

    def format_card_durations_chart(self, cards):
        self.all_data = {status: [] for status in self.status}
        labels = str(['#' + card.number for card in cards])
        for card in cards:
            for status in self.all_data:
                self.all_data[status].append('%.2f' % card.durations[status])
        data_str = self._get_data_str_from_all_data()
        self.script_tag.insert_before('\nvar card_numbers = ' + labels + ';')
        self.script_tag.insert_before('\nvar cards_data = ' + data_str + ';')
        self.template.find('canvas', id='statusDurationsChart')['height'] = str(len(cards) * 15)

    def format_card_durations_data(self, cards):
        table_tag = self.template.find('table', id='statusDurationsData')
        table_tag.append(self._get_tr_th_from_data('Card', 'Sum', self.status))
        average_data = ['%.2f' % (sum([float(data) for data in self.all_data[status]]) / len(cards)) for status in
                        self.status]
        table_tag.append(self._get_tr_th_from_data('Average', '0', average_data))

        for card in cards:
            table_tag.append(self._get_tr_td_from_card(card))

    def _get_tr_th_from_data(self, title, summary, data):
        tr_tag = self._new_tag('tr')

        tr_tag.append(self._new_tag('th', title, {'style': 'background-color: rgba(109,196,203,1);'}))
        tr_tag.append(self._new_tag('th', summary, {'style': 'background-color: rgba(15,180,216,1);'}))

        for i in range(len(data)):
            tr_tag.append(self._new_tag('th', str(data[i]), {'style': f"background-color: {self.colors[i]};"}))
            i += 1
        return tr_tag

    def _get_tr_td_from_card(self, card):
        tr_tag = self._new_tag('tr')

        card_td_tag = self._new_tag('td', parameters={'style': 'background-color: rgba(109,196,203,0.3);'})
        card_a_tag = self._new_tag('a', '#' + card.number, {'title': card.title, 'href': self.url + card.number})
        card_td_tag.append(card_a_tag)

        points_td_tag = self._new_tag('td', card.points, {'style': 'background-color: rgba(15,180,216,0.3);'})
        sum_td_tag = self._new_tag('td', '0', {'style': 'background-color: rgba(15,180,216,0.3);'})

        tr_tag.append(card_td_tag)
        tr_tag.append(points_td_tag)
        tr_tag.append(sum_td_tag)

        i = 0
        for status in card.durations:
            td_tag = self._new_tag('td', '%.2f' % card.durations[status],
                                   {'style': f"background-color: {self.colors[i].replace('1)', '0.3)')};"})
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

    def _new_tag(self, tag_type, string='', parameters=None):
        new_tag = self.template.new_tag(tag_type)
        if string:
            new_tag.string = string
        if parameters:
            for key in parameters:
                new_tag[key] = parameters[key]
        return new_tag
