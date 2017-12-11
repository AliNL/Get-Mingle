from src.card import Card


class Iteration:
    def __init__(self, number, title, key_status_list):
        self.number = number
        self.title = title
        self.sum_points = 0
        self.sum_days = {key_status: 0 for key_status in key_status_list}
        self.cards = []

    def get_cards_data(self, cards):
        self.cards = cards
        for card in self.cards:
            if card.points:
                self.sum_points += int(card.points)
            for key_status in self.sum_days:
                self.sum_days[key_status] += card.durations[key_status]
