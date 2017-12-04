import datetime
from bs4 import BeautifulSoup


class Formatter:
    def __init__(self, template: BeautifulSoup):
        self.template = template
        self.colors = ['rgba(229,115,115,1)', 'rgba(186,104,200,1)', 'rgba(121,134,203,1)',
                       'rgba(79,195,247,1)', 'rgba(77,182,172,1)', 'rgba(174,213,129,1)',
                       'rgba(255,241,118,1)', 'rgba(255,183,77,1)', 'rgba(240,98,146,1)',
                       'rgba(149,117,205,1)', 'rgba(100,181,246,1)', 'rgba(77,208,225,1)',
                       'rgba(129,199,132,1)', 'rgba(220,231,117,1)', 'rgba(255,213,79,1)',
                       'rgba(255,138,101,1)']

    def format_status_toggles(self, status):
        parent_tag = self.template.find('div', class_='status-toggles')
        for status_key in status:
            insert_tag = self.template.new_tag('div')
            insert_tag['class'] = 'status-toggle'
            insert_tag['name'] = str(status_key)
            rect = self.template.new_tag('span')
            rect['class'] = 'color-check-box'
            color = self.colors[status_key]
            rect['style'] = f'background-color: {color};border: solid {color} 3px;'
            span = self.template.new_tag('span')
            span['class'] = 'status-name'
            span.string = status[status_key]

            insert_tag.append(rect)
            insert_tag.append(span)
            parent_tag.append(insert_tag)

    def format_card_status_durations(self, changes, status):
        script_tag = self.template.find_all('script')[-1].string
        all_status = list(status.values())
        all_data = {status: [0] * len(changes) for status in all_status}
        labels = str(['#' + card for card in list(changes.keys())])
        i = 0
        for card in changes:
            last_time = None
            for entry in changes[card]:
                this_status, this_time = self._get_status_and_time_from_entry(entry)
                if this_status:
                    if this_status in status.values():
                        time_delta = round((this_time - last_time) / (3600 * 24), 2)
                        all_data[this_status][i] += time_delta
                last_time = this_time or last_time
            i += 1
        data_str = self._get_data_str_from_all_data(all_data)
        script_tag.insert_before('\nvar card_numbers = ' + labels + ';')
        script_tag.insert_before('\nvar all_data = ' + data_str + ';')
        self.template.find('canvas')['height'] = str(len(changes) * 15)
        return all_data

    def format_card_status_data(self, all_data, status, cards, url):
        table_tag = self.template.find('table', id='statusDurationsData')
        tr_tag = self.template.new_tag('tr')
        th_tag = self.template.new_tag('th')
        th_tag.string = 'Card'
        th_tag['style'] = 'background-color: rgba(109,196,203,1);'
        tr_tag.append(th_tag)
        for status_key in status:
            th_tag = self.template.new_tag('th')
            th_tag.string = status[status_key]
            th_tag['style'] = f'background-color: {self.colors[status_key]};'
            tr_tag.append(th_tag)
        table_tag.append(tr_tag)

        avg_tr_tag = self.template.new_tag('tr')
        avg_th_tag = self.template.new_tag('th')
        avg_th_tag['style'] = 'background-color: rgba(109,196,203,1);'
        avg_th_tag.string = 'Average'
        avg_tr_tag.append(avg_th_tag)

        table_tag.append(avg_tr_tag)

        tr_list = []
        for card in cards:
            tr_tag = self.template.new_tag('tr')
            td_tag = self.template.new_tag('td')
            td_tag['style'] = 'background-color: rgba(109,196,203,0.3);'
            a_tag = self.template.new_tag('a')
            a_tag.string = '#' + card
            a_tag['title'] = cards[card]
            a_tag['href'] = url + '/' + card
            td_tag.append(a_tag)
            tr_tag.append(td_tag)
            tr_list.append(tr_tag)

        j = 0
        for data in all_data:
            i = 0
            for duration in all_data[data]:
                td_tag = self.template.new_tag('td')
                td_tag.string = '%.2f' % duration
                td_tag['style'] = f"background-color: {self.colors[j].replace('1)', '0.3)')};"
                tr_list[i].append(td_tag)
                i += 1
            avg_th_tag = self.template.new_tag('th')
            avg_th_tag.string = '%.2f' % (sum(all_data[data]) / len(all_data[data]))
            avg_th_tag['style'] = f'background-color: {self.colors[j]};'
            avg_tr_tag.append(avg_th_tag)
            j += 1

        for tr_tag in tr_list:
            table_tag.append(tr_tag)

    @staticmethod
    def _get_status_and_time_from_entry(entry):
        this_time = entry.find('updated').string
        this_time = int(datetime.datetime.strptime(this_time, '%Y-%m-%dT%H:%M:%SZ').strftime("%s"))
        found_status = entry.find('name', text='Status')
        if not found_status:
            return None, None
        this_status = found_status.find_next('old_value').string
        return this_status, this_time

    def _get_data_str_from_all_data(self, all_data):
        data_str = "["
        i = 0
        for data in all_data:
            data_str += "{"
            data_str += f"label: '{data}',"
            data_str += "data: " + str(all_data[data]) + ","
            data_str += "backgroundColor: '" + self.colors[i] + "'"
            data_str += "},"
            i += 1
        data_str = data_str[:-1] + "]"
        return data_str
