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
        # pass

    def format_iteration_data(self, iteration):
        section = self.template.find('div', id='iteration-summary-section')
        section.h2.string.insert_after(iteration.title)
        data_part = self.template.find('div', class_='iteration-summary-data')

        h3_tag = self.template.new_tag('h3')
        h3_tag.string = 'Total Points: ' + str(iteration.sum_points)
        data_part.append(h3_tag)

        h3_tag = self.template.new_tag('h3')
        h3_tag.string = 'Total Movements: ' + str(iteration.sum_steps)
        data_part.append(h3_tag)

        for status in iteration.sum_days:
            h3_tag = self.template.new_tag('h3')
            h3_tag.string = 'Total Days for "' + status + '": ' + '%.2f' % iteration.sum_days[status]
            data_part.append(h3_tag)

    def format_status_toggles(self):
        parent_tag = self.template.find('div', class_='status-toggles')
        for i in range(len(self.status)):
            insert_tag = self.template.new_tag('div')
            insert_tag['class'] = 'status-toggle'
            insert_tag['name'] = str(i)
            check_box = self.template.new_tag('span')
            check_box['class'] = 'color-check-box'
            color = self.colors[i]
            check_box['style'] = f'background-color: {color};border: solid {color} 3px;'
            status_name = self.template.new_tag('span')
            status_name['class'] = 'status-name'
            status_name.string = self.status[i]

            insert_tag.append(check_box)
            insert_tag.append(status_name)
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
        table_tag.append(self._get_tr_th_from_data('Card', self.status))
        average_data = ['%.2f' % (sum([float(data) for data in self.all_data[status]]) / len(cards)) for status in
                        self.status]
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
