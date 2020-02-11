import argparse
import re
from datetime import datetime


class Logg:
    def __init__(self, file=None, from_arg=None, to_arg=None):
        self.file = file
        self.from_arg = from_arg
        self.to_arg = to_arg
        self.time_window = {
            'from': None,
            'to': None,
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

    def check_arguments(self):
        if self.from_arg:
            self.convert_time_frame('from')
        if self.to_arg:
            self.convert_time_frame('to')

    def convert_time_frame(self, from_to: str) -> None:
        time_frame = {
            'from': {
                'day': 1,
                'month': 1,
                'year': 1970,
                'hour': 00,
                'minute': 00,
                'second': 00
            },
            'to': {
                'day': 00,
                'month': datetime.now().month,
                'year': datetime.now().year,
                'hour': 23,
                'minute': 59,
                'second': 59,
            }
        }
        try:
            # Splits from/to argument into date and time strings
            if from_to == 'from':
                date_time = self.from_arg.split('_')
            elif from_to == 'to':
                date_time = self.to_arg.split('_')
            date = date_time[0].split('-')
            for i in range(len(date)):
                if i == 0:
                    time_frame[from_to]['day'] = date[0]
                if i == 1:
                    time_frame[from_to]['month'] = date[1]
                if i == 2:
                    time_frame[from_to]['year'] = date[2]
        except ValueError:
            # If the from/to format doesn't match correct format, the value remain None
            print(f"Please provide correct {from_to} values (eg. 23-12-1999_23-11-55)\n"
                  f"{from_to} scope won't be specified")
        try:
            # check if the time part is provided
            time = date_time[1].split('-')
            for i in range(len(time)):
                if i == 0:
                    if len(time) == 1:
                        time_frame[from_to]['minute'] = 00
                        time_frame[from_to]['second'] = 00
                    time_frame[from_to]['hour'] = time[0]
                if i == 1:
                    if len(time) == 2:
                        time_frame[from_to]['second'] = 00
                    time_frame[from_to]['minute'] = time[1]
                if i == 2:
                    time_frame[from_to]['second'] = time[2]
        except IndexError:
            print(f"\"{from_to}\" time part was not provided")
        # Parse dictionary values into datetime object
        from_to_time = f"{time_frame[from_to]['day']} " \
                       f"{time_frame[from_to]['month']} " \
                       f"{time_frame[from_to]['year']} " \
                       f"{time_frame[from_to]['hour']} " \
                       f"{time_frame[from_to]['minute']} " \
                       f"{time_frame[from_to]['second']}"
        self.time_window[from_to] = datetime.strptime(from_to_time, '%d %m %Y %H %M %S')

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
                # if 'from' value is None, unix epoch beginning time is assigned :)
                self.time_window['from'] = datetime.strptime('01 01 1970', '%d %m %Y')
            validation_status = self.time_window['from'] <= log_date_datetime <= self.time_window['to']
            # print(validation_status)
            if validation_status:
                if not self.time_window['last']:
                    # first date value which match the condition is assigned as 'first' date value for 'request_per_sec'
                    self.time_window['last'] = log_date_datetime
                # last date value which match the condition is assigned as 'last' value for 'request_per_sec'
                self.time_window['first'] = log_date_datetime
            return validation_status
        except AttributeError:
            # date not in the log entry (eg. first log row)
            return False

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
        try:
            seconds = self.time_window['last'] - self.time_window['first']
        except TypeError:
            raise TypeError('Given from/to dates are invalid')
        req_per_sec = self.output['requests'] / seconds.total_seconds()
        self.output['requests_per_seconds'] = f"{req_per_sec:.1f}"

    def display_output(self):
        requests = f"requests: {self.output['requests']}"
        req_per_sec = f"requests/sec: {self.output['requests_per_seconds']}"
        responses = f"responses: {self.output['responses']}"
        avg = f"avg size of 2xx responses:" \
              f" {self.output['avg_2xx_size']*10**(-6):.2f} Mb" \
              f" ({round(self.output['avg_2xx_size'])} bytes)"
        avg_str = "\n".join([requests, req_per_sec, responses, avg])
        return avg_str


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('--fromm', '--from', required=False)
    parser.add_argument('--to', required=False)
    args = parser.parse_args()
    file = args.file
    from_arg = args.fromm
    to_arg = args.to

    logg = Logg(file, from_arg, to_arg)
    logg.check_arguments()
    logg.open_file()
    print(logg.display_output())
