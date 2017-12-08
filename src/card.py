from datetime import datetime, time, timedelta


class Card:
    def __init__(self, number, title, points, interested_status, key_status):
        self.number = number
        self.title = title
        self.points = points
        self.changes = []
        self.key_status = key_status
        self.history = {}
        self.movement = []
        self.durations = {status: 0 for status in interested_status}
        self.moved_back = False
        self.description_changed = False

    def init(self):
        self.get_history_from_changes()
        self.get_durations_from_history()
        self.get_movement_from_history()
        self.get_extra_info_from_history()

    def get_history_from_changes(self):
        for entry in self.changes:
            this_time, this_change = get_change_from_entry(entry)
            if this_time:
                self.history[this_time] = this_change

    def get_movement_from_history(self):
        for change in self.history.values():
            if change != 'description-change':
                self.movement.append(change)

    def get_extra_info_from_history(self):
        get_to_the_key_status = False
        for change in self.history.values():
            if get_to_the_key_status:
                if change == 'description-change':
                    self.description_changed = True
                elif change == self.key_status:
                    self.moved_back = True
            if change == self.key_status:
                get_to_the_key_status = True

    def get_durations_from_history(self):
        last_time = None
        for this_time in self.history:
            this_status = self.history[this_time]
            if this_status in self.durations:
                this_time = datetime.fromtimestamp(this_time)
                time_delta = calculate_days_from_time(last_time, this_time)
                self.durations[this_status] += time_delta
            last_time = this_time or last_time


def get_change_from_entry(entry):
    this_time = entry.find('updated').string
    this_time = int(datetime.strptime(this_time, '%Y-%m-%dT%H:%M:%SZ').strftime("%s"))
    found_status = entry.find('name', text='Status')
    if found_status:
        return this_time, found_status.find_next('old_value').string
    elif entry.find('change', type='description-change'):
        return this_time, 'description-change'
    return None, None


def calculate_days_from_time(last_time, this_time):
    timed_delta = 0
    timed_delta += get_work_time(last_time, True)
    timed_delta += get_work_time(this_time, False)

    time_pointer = last_time.date()
    while time_pointer < this_time.date():
        time_pointer += timedelta(1)
        if time_pointer.weekday() < 5:
            timed_delta += timedelta(0, 32400)
    return timed_delta.total_seconds() / (3600 * 9)


def get_work_time(this_time, is_start):
    if this_time.weekday() > 4:
        return 0
    day_start = datetime.combine(this_time.date(), time(9, 0))
    day_end = datetime.combine(this_time.date(), time(18, 0))

    if this_time < day_start:
        this_time = day_start
    elif this_time > day_end:
        this_time = day_end

    if is_start:
        return day_end - this_time
    else:
        return this_time - day_start
