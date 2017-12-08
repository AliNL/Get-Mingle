from src.card import Card


class Iteration:
    def __init__(self, number, title, key_status_list):
        self.number = number
        self.title = title
        self.sum_points = 0
        self.sum_days = {key_status: 0 for key_status in key_status_list}
        self.cards = []

    def add_card(self, card: Card):
        self.cards.append(card)
        self.sum_points += card.points
        for key_status in self.sum_days:
            self.sum_days[key_status] += card.durations[key_status]
