from datetime import datetime, timedelta


class Iteration:
    def __init__(self, title, start_date, end_date, key_status_list, steps_status):
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.sum_points = 0
        self.sum_steps = 0
        self.steps_status = steps_status
        self.sum_days = {key_status: 0 for key_status in key_status_list}
        self.cards = []
        self.changes = []
        self.steps = {}
        self.movements = []

    def get_cards_data(self):
        for card in self.cards:
            if card.points:
                self.sum_points += int(card.points)
            for key_status in self.sum_days:
                self.sum_days[key_status] += card.durations[key_status]

    def get_steps_data(self):
        for entry in self.changes:
            found_status = entry.find('name', text='Status')
            if found_status:
                update_time = entry.updated.string[:-1]
                old_status = found_status.find_next('old_value').string
                new_status = found_status.find_next('new_value').string
                if old_status in self.steps_status and new_status in self.steps_status:
                    self.sum_steps += self.steps_status.index(new_status) - self.steps_status.index(old_status)
                    if update_time in self.steps.keys():
                        dt = datetime.strptime(update_time, '%Y-%m-%dT%H:%M:%S') + timedelta(seconds=1)
                        update_time = dt.strftime('%Y-%m-%dT%H:%M:%S')
                    self.steps[update_time] = self.sum_steps
                    self.movements.append([entry.title.string, old_status + ' -> ' + new_status])

    def init(self):
        self.get_cards_data()
        self.get_steps_data()
