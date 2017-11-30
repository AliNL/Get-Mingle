from bs4 import BeautifulSoup


class Formatter:
    def __init__(self, template: BeautifulSoup):
        self.template = template
        self.colors = ['#AFB226', '#F07627', '#149E49', '#EDAB85', '#E73F8F',
                       '#74AC6D', '#E51723', '#16AFC2', '#5B1256', '#8F644F',
                       '#F9DAC3', '#FFF440', '#6DC4CB']

    def format_status_toggles(self, status):
        parent_tag = self.template.find('div', class_='status-toggles')
        for status_key in status:
            insert_tag = self.template.new_tag('div')
            insert_tag['class'] = 'status-toggle'
            rect = self.template.new_tag('rect')
            rect['class'] = 'color-check-box'
            color = self.colors[status_key]
            rect['style'] = f'background-color: {color};border: solid {color} 3px;'
            span = self.template.new_tag('span')
            span['class'] = 'status-name'
            span.string = status[status_key]

            insert_tag.append(rect)
            insert_tag.append(span)
            parent_tag.append(insert_tag)
