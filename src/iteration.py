from datetime import datetime

from src.card import Card


class Iteration:
    def __init__(self, title, start_date, end_date, key_status_list, steps_status):
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.sum_points = 0
        self.sum_steps = 0
        self.steps_status = dict(zip(steps_status.values(), steps_status.keys()))
        self.sum_days = {key_status: 0 for key_status in key_status_list}
        self.cards = []
        self.changes = []
        self.steps = {}

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
                    self.sum_steps += self.steps_status[new_status] - self.steps_status[old_status]
                    self.steps[update_time] = self.sum_steps

    def init(self):
        self.get_cards_data()
        self.get_steps_data()
