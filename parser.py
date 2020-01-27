import argparse
import re
from datetime import datetime


class ArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--fromm', '--from', required=False)
        self.parser.add_argument('--to', required=False)
        self.parser.add_argument('file')
        self.from_arg = None
        self.to_arg = None
        self.file = None
        self.time_window = {'from': None, 'to': None}

    def check_arguments(self):
        args = self.parser.parse_args()
        self.from_arg = args.fromm
        self.to_arg = args.to
        self.file = args.file
        if self.from_arg:
            self.parse_time_frame('from')
        if self.to_arg:
            self.parse_time_frame('to')

    def parse_time_frame(self, from_to: str) -> None:
        time_frame = {
            'from': {
                'day': 00,
                'month': 00,
                'year': 0000,
                'hour': 00,
                'minute': 00,
                'second': 00
            },
            'to': {
                'day': 00,
                'month': 00,
                'year': 0000,
                'hour': 00,
                'minute': 00,
                'second': 00,
            }
        }
        try:
            # Splits from/to argument into date and time strings
            if from_to == 'from':
                date = self.from_arg.split('_')
            elif from_to == 'to':
                date = self.to_arg.split('_')
            day, month, year = date[0].split('-')
            time_frame[from_to]['day'] = day
            time_frame[from_to]['month'] = month
            time_frame[from_to]['year'] = year
            try:
                # check if the time part is provided
                time = date[1].split('-')
                for i in range(len(time)):
                    if i == 0:
                        time_frame[from_to]['hour'] = time[0]
                    if i == 1:
                        time_frame[from_to]['minute'] = time[1]
                    if i == 2:
                        time_frame[from_to]['second'] = time[2]
            except IndexError:
                # no time part argument provided
                pass
            # Parse dictionary values into datetime object
            from_to_time = f"{time_frame[from_to]['day']} " \
                           f"{time_frame[from_to]['month']} " \
                           f"{time_frame[from_to]['year']} " \
                           f"{time_frame[from_to]['hour']} " \
                           f"{time_frame[from_to]['minute']} " \
                           f"{time_frame[from_to]['second']}"
            self.time_window[from_to] = datetime.strptime(from_to_time, '%d %m %Y %H %M %S')
        except ValueError as e:
            # If the from/to format doesn't match correct format, the value remain None
            print('Please provide correct from/to values (eg. 23-12-1999_23-11-55)')

    def return_arguments(self):
        return self.time_window['from'], self.time_window['to'], self.file


class Logg:
    def __init__(self, file=None, from_arg=None, to_arg=None):
        self.file = file
        self.time_window = {
            'from': from_arg,
            'to': to_arg,
            'first': None,  # first date value required to count the requests_per_sec
            'last': None    # last date value required to count the requests_per_sec
        }
        self.output = {
            'requests': 0,
            'requests_per_sec': '',
            'responses': {},
            '2xx_size': [0, 0],  # [how many values, overall size]
            'avg_2xx_size': 0
        }

    def open_file(self):
        with open(self.file, 'r') as logg:
            self.read_file(logg)

    def read_file(self, logg) -> None:
        for line in logg.readlines():
            if self.check_if_date_in_range(line):
                self.look_for_responses(line)
                self.look_for_size(line)
        self.count_avg_2xx_size()
        self.count_requests_per_second()

    def check_if_date_in_range(self, line: str) -> bool:
        date_regex = re.compile(r'(?<=\[).{20}(?=\s[-+]\d)')
        log_date = re.search(date_regex, line)
        try:
            log_date_datetime = datetime.strptime(log_date.group(0), '%d/%b/%Y:%H:%M:%S')
            if not self.time_window['to']:
                # if 'to' value is None, first log entry is assigned (first is the most recent)
                self.time_window['to'] = log_date_datetime
            if not self.time_window['from']:
                # if 'from' value is assigned, unix epoch beginning time is assigned
                self.time_window['from'] = datetime.strptime('01 01 1970', '%d %m %Y')
            validation_status = self.time_window['from'] <= log_date_datetime <= self.time_window['to']
            if validation_status:
                if not self.time_window['last']:
                    # first date value which match the condition is assigned as a 'first' date value for 'request_per_sec'
                    self.time_window['last'] = log_date_datetime
                # last date value which match the condition is assigned as a 'last' value for 'request_per_sec'
                self.time_window['first'] = log_date_datetime
                return validation_status
        except AttributeError:
            # date not in the log entry (eg. first log row)
            pass

    def look_for_responses(self, line: str) -> None:
        response_regex = re.compile(r'(?<=\s)\d{3}(?=\s)')
        response = re.search(response_regex, line)
        if response:
            response_value = response.group(0)
            self.output['requests'] += 1
            try:
                self.output['responses'][response_value] += 1
            except KeyError:
                # first time occurrence of response code
                self.output['responses'][response_value] = 1

    def look_for_size(self, line: str) -> None:
        size_regex = re.compile(r'(?<=[2]\d{2}\s)\d*(?=\s)')
        size = re.search(size_regex, line)
        if size:
            size_value = size.group(0)
            self.output['2xx_size'][0] += 1
            self.output['2xx_size'][1] += int(size_value)

    def count_avg_2xx_size(self):
        # number of 2xx codes by overall 2xx responses size division
        try:
            self.output['avg_2xx_size'] = self.output['2xx_size'][1] / self.output['2xx_size'][0]
        except ZeroDivisionError:
            self.output['avg_2xx_size'] = 0

    def count_requests_per_second(self):
        seconds = self.time_window['last'] - self.time_window['first']
        req_per_sec = self.output['requests'] / seconds.total_seconds()
        self.output['requests_per_seconds'] = f"{req_per_sec:.1f}"

    def display_output(self):
        requests = f"requests: {self.output['requests']}"
        req_per_sec = f"requests/sec: {self.output['requests_per_seconds']}"
        responses = f"responses: {self.output['responses']}"
        avg = f"avg size of 2xx responses:" \
              f" {self.output['avg_2xx_size']*10**(-6):.2f} Mb" \
              f" ({round(self.output['avg_2xx_size'])} bytes)"
        print("\n".join([requests, req_per_sec, responses, avg]))


if __name__ == "__main__":
    argument_parser = ArgumentParser()
    argument_parser.check_arguments()
    from_arg, to_arg, file = argument_parser.return_arguments()

    logg = Logg(file, from_arg, to_arg)
    logg.open_file()

    logg.display_output()
