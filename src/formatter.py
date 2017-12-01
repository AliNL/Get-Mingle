import datetime
from bs4 import BeautifulSoup


class Formatter:
    def __init__(self, template: BeautifulSoup):
        self.template = template
        self.colors = ['#E57373', '#BA68C8', '#7986CB',
                       '#4FC3F7', '#4DB6AC', '#AED581',
                       '#FFF176', '#FFB74D', '#F06292',
                       '#9575CD', '#64B5F6', '#4DD0E1',
                       '#81C784', '#DCE775', '#FFD54F',
                       '#FF8A65']

    def format_status_toggles(self, status):
        parent_tag = self.template.find('div', class_='status-toggles')
        for status_key in status:
            insert_tag = self.template.new_tag('div')
            insert_tag['class'] = 'status-toggle'
            insert_tag['onclick'] = f'toggleStatus({status_key}, this)'
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
                        time_delta = int((this_time - last_time) / (36 * 24)) / 100
                        all_data[this_status][i] += time_delta
                last_time = this_time or last_time
            i += 1
        data_str = self._get_data_str_from_all_data(all_data)
        script_tag.insert_before('var card_numbers = ' + labels + ';')
        script_tag.insert_before('var all_data = ' + data_str + ';')
        self.template.find('canvas')['height'] = str(len(changes) * 15)

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
