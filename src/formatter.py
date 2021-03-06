from datetime import datetime

from bs4 import BeautifulSoup


class Formatter:
    def __init__(self, template: BeautifulSoup, status, key_status, url):
        self.template = template
        self.status = status
        self.key_status = key_status
        self.url = url
        self.all_data = {}
        self.average_data = []
        self.script_tag = self.template.find('script', type='text/javascript').string

    @staticmethod
    def colors(i, opacity=1):
        col = [(229, 115, 115), (186, 104, 200), (121, 134, 203), (79, 195, 247),
               (77, 182, 172), (174, 213, 129), (255, 241, 118), (255, 183, 77),
               (240, 98, 146), (149, 117, 205), (100, 181, 246), (77, 208, 225),
               (129, 199, 132), (220, 231, 117), (255, 213, 79), (255, 138, 101),
               (244, 67, 54), (156, 39, 176), (63, 81, 181), (3, 169, 244),
               (0, 150, 136), (139, 195, 74), (255, 235, 59), (255, 152, 0),
               (233, 30, 99), (103, 58, 183), (33, 150, 243), (0, 188, 212),
               (76, 175, 80), (205, 220, 57), (255, 193, 7), (255, 87, 34)]
        r, g, b = col[i]
        return 'rgba' + str((r, g, b, opacity))

    def format_iteration_chart(self, iteration):
        data_str = '['
        for step in iteration.steps:
            data_str += f"{{x: '{step}', y: {str(iteration.steps[step])}}},"
        data_str = data_str[:-1] + ']'
        self.script_tag.insert_before('\nvar steps_data = ' + data_str + ';')
        self.script_tag.insert_before('\nvar movements = ' + str(iteration.movements) + ';')

    def format_iteration_data(self, iteration):
        section = self.template.find('div', id='iteration-summary-section')
        section.h2.string.insert_after(iteration.title)
        data_part = self.template.find('div', class_='iteration-summary-data')

        data_part.append(self._new_tag('h3', 'Total Points: ' + str(iteration.sum_points)))
        data_part.append(self._new_tag('h3', 'Total Movements: ' + str(iteration.sum_steps)))
        for status in iteration.sum_days:
            data_part.append(
                self._new_tag('h3', 'Total Days for "' + status + '": ' + '%.2f' % iteration.sum_days[status]))

    def remove_iteration_summary_section(self):
        self.template.find('div', id='iteration-summary-section').decompose()

    def format_unusual_cards(self, cards):
        section = self.template.find('div', class_='unusual-cards-section')
        moved_back_section = section.find('div', class_='unusual-cards-sub-section left')
        changed_section = section.find('div', class_='unusual-cards-sub-section right')
        moved_back_section.h3['title'] = moved_back_section.h3.string + f' after moved to "{self.key_status}"'
        changed_section.h3['title'] = changed_section.h3.string + f' after moved to "{self.key_status}"'
        for card in cards:
            if card.moved_back:
                if moved_back_section.find('span', class_='no-card'):
                    moved_back_section.find('span', class_='no-card').decompose()
                moved_back_section.append(
                    self._new_tag('button', '#' + card.number + ' ' + card.title, {'name': card.number}))
                moved_back_section.append(
                    self._new_popup(card.number, card.title, card.movements))
            if card.description_changed:
                if changed_section.find('span', class_='no-card'):
                    changed_section.find('span', class_='no-card').decompose()
                changed_section.append(
                    self._new_tag('button', '#' + card.number + ' ' + card.title, {'name': card.number}))
                changed_section.append(
                    self._new_popup(card.number, card.title, card.movements))

    def format_status_toggles(self):
        parent_tag = self.template.find('div', class_='status-toggles')
        for i in range(len(self.status)):
            insert_tag = self._new_tag('div', dic={'class': 'status-toggle', 'name': str(i)})

            insert_tag.append(self._new_tag(
                'span', dic={'class': 'color-check-box',
                             'style': f'background-color: {self.colors(i)};border: solid {self.colors(i)} 3px;'}))
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
        table_tag.append(self._get_tr_th_from_data(['Card', 'Points', 'Total'], self.status))
        total_points = 0
        for card in cards:
            if card.points:
                total_points += int(card.points)
            else:
                total_points += 1
        self.average_data = ['%.2f' % (sum([float(data) for data in self.all_data[status]]) / total_points) for status
                             in
                             self.status]
        table_tag.append(self._get_tr_th_from_data(['Average', '/', '0'], self.average_data))

        for card in cards:
            table_tag.append(self._get_tr_td_from_card(card))

    def _get_tr_th_from_data(self, titles, data):
        tr_tag = self._new_tag('tr', dic={'class': 'duration'})

        for i in range(len(titles)):
            tr_tag.append(
                self._new_tag('th', titles[i],
                              {'style': f'background-color: {self.colors(i - len(titles))};', 'class': 'duration'}))

        for i in range(len(data)):
            tr_tag.append(self._new_tag('th', str(data[i]),
                                        {'style': f"background-color: {self.colors(i)};", 'class': 'duration'}))
            i += 1
        return tr_tag

    def _get_tr_td_from_card(self, card):
        tr_tag = self._new_tag('tr', dic={'class': 'duration'})

        card_td_tag = self._new_tag('td',
                                    dic={'style': f'background-color: {self.colors(-3,0.3)};', 'class': 'duration'})
        card_a_tag = self._new_tag('a', '#' + card.number, {'title': card.title, 'href': self.url + card.number})
        card_td_tag.append(card_a_tag)

        points_td_tag = self._new_tag('td', card.points,
                                      {'style': f'background-color: {self.colors(-2,0.3)};', 'class': 'duration'})
        sum_td_tag = self._new_tag('td', '0',
                                   {'style': f'background-color: {self.colors(-1,0.3)};', 'class': 'duration'})

        tr_tag.append(card_td_tag)
        tr_tag.append(points_td_tag)
        tr_tag.append(sum_td_tag)

        i = 0
        for status in card.durations:
            dic = {'style': f'background-color: {self.colors(i,0.3)};', 'class': 'duration'}
            this_durations = card.durations[status]
            if card.points:
                this_durations = this_durations / int(card.points)
            if this_durations > float(self.average_data[i]) * 1.3:
                dic['style'] += 'border: solid red 2px'
            td_tag = self._new_tag('td', '%.2f' % card.durations[status], dic)
            tr_tag.append(td_tag)
            i += 1
        return tr_tag

    def _get_data_str_from_all_data(self):
        data_str = "["
        i = 0
        for data in self.all_data:
            data_str += f"{{label: '{data}', data: {str(self.all_data[data])}, backgroundColor: '{self.colors(i)}'}},"
            i += 1
        data_str = data_str[:-1] + "]"
        return data_str

    def _new_tag(self, tag_type, string='', dic=None):
        new_tag = self.template.new_tag(tag_type)
        if string:
            new_tag.string = string
        if dic:
            for key in dic:
                new_tag[key] = dic[key]
        return new_tag

    def _new_popup(self, number, title, movements):
        new_tag = self._new_tag('div', dic={'class': 'popup-cover', 'id': number})
        popup = self._new_tag('div', dic={'class': 'popup'})
        new_tag.append(popup)
        header = self._new_tag('div', dic={'class': 'header-area'})
        popup.append(header)
        header.append(self._new_tag('span', '×', {'class': 'close', 'name': number}))
        header.append(self._new_tag('span', '#' + number, {'class': 'number'}))
        header.append(self._new_tag('span', title, {'class': 'title'}))
        history_area = self._new_tag('div', dic={'class': 'history-area'})
        popup.append(history_area)
        table = self._new_tag('table')
        history_area.append(table)

        time_list = list(movements.keys())
        time_list.sort()
        for i in range(1, len(time_list)):
            this_time = time_list[i]
            tr_tag = self._new_tag('tr')
            table.append(tr_tag)
            if movements[this_time][0] in ('murmur', 'description'):
                tr_tag.append(self._new_tag('td'))
            td_tag = self._new_tag('td')
            tr_tag.append(td_tag)
            td_tag.append(self._new_tag('span', datetime.utcfromtimestamp(this_time).strftime('%Y-%m-%d %H:%M')))
            h5 = self._new_tag('h5', dic={'class': movements[this_time][0]})
            td_tag.append(h5)
            for string in movements[this_time][1:]:
                h5.append(self._new_tag('p', string))

        return new_tag
