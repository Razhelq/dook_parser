import argparse
import re


class Log:
    def __init__(self, file=None, fromm=None, to=None):
        self.file = file
        self.fromm = fromm
        self.to = to
        self.output = {
            'requests': 0,
            'requests_per_sec': 0,
            'responses': {},
            '2xx_size': [0, 0],
            'avg_2xx_size': 0
        }

    def open_file(self):
        with open(self.file, 'r') as log:
            self.read_file(log)

    def read_file(self, log):
        for line in log.readlines():
            if self.fromm or self.to:
                if self.validate_time(line):
                    self.look_for_responses(line)
                    self.look_for_size(line)
            else:
                self.look_for_responses(line)
                self.look_for_size(line)
        self.count_avr_2xx_size()

    def validate_time(self):
        self.parse_time()

    def parse_time(self):


    def look_for_responses(self, line: str) -> None:
        response_regex = re.compile(r'(?<=\s)\d{3}(?=\s)')
        response = re.search(response_regex, line)
        if response:
            response_value = response.group(0)
            self.output['requests'] += 1
            try:
                self.output['responses'][response_value] += 1
            except KeyError:
                self.output['responses'][response_value] = 0

    def look_for_size(self, line: str) -> None:
        size_regex = re.compile(r'(?<=[2]\d{2}\s)\d*(?=\s)')
        size = re.search(size_regex, line)
        if size:
            size_value = size.group(0)
            self.output['2xx_size'][0] += 1
            self.output['2xx_size'][1] += int(size_value)

    def count_avr_2xx_size(self):
        self.output['avg_2xx_size'] = self.output['2xx_size'][1] / self.output['2xx_size'][0]


class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--fromm', '--from', required=False)
        self.parser.add_argument('--to', required=False)
        self.parser.add_argument('file')

    def return_arguments(self):
        args = self.parser.parse_args()
        return args.fromm, args.to, args.file


if __name__ == "__main__":
    p = Parser()
    fromm, to, file = p.return_arguments()

    l = Log(file, fromm, to)
    l.open_file()

    print(l.output)
