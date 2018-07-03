import operator
from datetime import datetime, time, timedelta


class Card:
    def __init__(self, number, title, points, interested_status, key_status, requester, time_zone):
        self.number = number
        self.title = title
        self.points = points
        self.changes = []
        self.key_status = key_status
        self.requester = requester
        self.time_zone = time_zone
        self.history = {}
        self.movement = []
        self.movements = {}
        self.interested_status = interested_status
        self.durations = {status: 0 for status in interested_status}
        self.moved_back = False
        self.description_changed = False

    def init(self):
        self.get_history_from_changes()
        self.get_durations_from_history()
        self.get_movements_from_history()
        self.get_extra_info_from_history()

    def get_history_from_changes(self):
        for entry in self.changes:
            this_time, this_change = get_change_from_entry(entry)
            if this_time:
                self.history[this_time] = this_change
        self.get_murmurs()

    def get_movements_from_history(self):
        last_status = -1
        last_change = None
        for i in range(1, len(self.history)):
            this_time = list(self.history.keys())[i]
            this_change = self.history[this_time]
            if this_change[0] == 'status' and this_change[1] in self.interested_status:
                this_status = self.interested_status.index(this_change[1])
                if last_status != -1:
                    if this_status > last_status:
                        self.movements[this_time] = ('forward', last_change[1] + '　⇨　' + this_change[1])
                    else:
                        if this_change[1] == self.key_status:
                            self.moved_back = True
                        self.movements[this_time] = ('backward', this_change[1] + '　⇦　' + last_change[1])
                last_status = this_status
                last_change = this_change
            elif this_change[0] == 'murmur':
                self.movements[this_time] = this_change

    def get_extra_info_from_history(self):
        get_to_the_key_status = False
        for this_time in self.history:
            this_change = self.history[this_time]
            if get_to_the_key_status and this_change[0] == 'description':
                self.movements[this_time] = this_change
                self.description_changed = True
            if this_change[1] == self.key_status:
                get_to_the_key_status = True

    def get_durations_from_history(self):
        last_time = None
        for this_time in self.history:
            this_status = self.history[this_time]
            if this_status[0] != 'status':
                continue
            this_time = datetime.fromtimestamp(this_time)
            if this_status[1] in self.durations:
                time_delta = calculate_days_from_time(last_time, this_time)
                self.durations[this_status[1]] += time_delta
            last_time = this_time

    def get_murmurs(self):
        from bs4 import BeautifulSoup
        xml = self.requester.get_murmurs(self.number)
        murmurs = BeautifulSoup(xml, 'xml')
        for murmur in murmurs.find_all('murmur'):
            this_time = datetime.strptime(murmur.created_at.string, '%Y-%m-%dT%H:%M:%SZ') + timedelta(
                hours=int(self.time_zone))
            this_time = int(this_time.strftime("%s"))
            author = murmur.author.find('name').string
            body = murmur.body.string
            self.movements[this_time] = ('murmur', author + ':', body)


def get_change_from_entry(entry):
    this_time = entry.find('updated').string
    this_time = int(datetime.strptime(this_time, '%Y-%m-%dT%H:%M:%SZ').strftime("%s"))
    author = entry.author.find('name').string
    found_status = entry.find('name', text='Status')
    if found_status:
        return this_time, ('status', found_status.find_next('old_value').string)
    elif entry.find('change', type='description-change'):
        return this_time, ('description', author + ':', 'description change')
    return None, None


holidays = [datetime(2018, 1, 1).date()]


def calculate_days_from_time(last_time, this_time):
    timed_delta = timedelta(0)
    timed_delta += get_work_time(last_time, True)
    timed_delta += get_work_time(this_time, False)

    time_pointer = last_time.date() + timedelta(1)
    while time_pointer < this_time.date():
        if operator.xor(time_pointer.weekday() < 5, time_pointer in holidays):
            timed_delta += timedelta(0, 32400)
        time_pointer += timedelta(1)
    if last_time.date() == this_time.date():
        timed_delta -= timedelta(0, 32400)
    return round(timed_delta.total_seconds() / (3600 * 9), 2)


def get_work_time(this_time, is_start):
    if not operator.xor(this_time.weekday() < 5, this_time.date() in holidays):
        return timedelta(0)
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
