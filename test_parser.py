from parser import ArgParser, Logg
from datetime import datetime
import pytest


@pytest.fixture(scope='module')
def logg():
    logg = Logg('gunicorn.log2')
    logg.open_file()
    yield logg


def test_requests(logg):
    assert logg.output['requests'] == 99999


def test_responses(logg):
    assert logg.output['responses'] == {'200': 96205, '404': 3794}


def test_2xx_size(logg):
    assert logg.output['2xx_size'] == [96205, 77519252]


def test_count_avg_2xx_size(logg):
    assert logg.output['avg_2xx_size'] == 805.7715503352217


def test_count_requests_per_seconds(logg):
    assert logg.output['requests_per_seconds'] == '1.1'


def test_display_output(logg):
    output = '''requests: 99999
requests/sec: 1.1
responses: {'200': 96205, '404': 3794}
avg size of 2xx responses: 0.00 Mb (806 bytes)'''
    assert logg.display_output() == output


def test_check_if_date_in_range(logg):
    test_line = 'Dec 01 11:06:07 app3-test-vm1 gunicorn[53253]:' \
                ' 172.16.3.14 - - [01/Dec/2019:11:06:07 +0100]' \
                ' "GET /internal/user/03144bdb-805e-4a56-836f-3324a812fe0f/agenda/2019-12-01/2019-12-02 HTTP/1.1"' \
                ' 200 720 "-" "python-requests/2.22.0" 402636'
    test_line_two = 'Dec 01 11:06:03 app3-test-vm1 gunicorn[53253]:' \
                    ' 172.16.3.14 - - [01/Dec/2020:11:06:03 +0100]' \
                    ' "GET /internal/user/9e4189b1-6d91-4bef-a80a-e9ebfb401ac6/agenda/2019-12-01/2019-12-02 HTTP/1.1"' \
                    ' 200 720 "-" "python-requests/2.22.0" 421824'
    assert logg.check_if_date_in_range(test_line) is True
    assert logg.check_if_date_in_range(test_line_two) is False


@pytest.fixture(scope='module')
def logg_with_from():
    from_arg = datetime.strptime('01 12 2019 11 06 04', '%d %m %Y %H %M %S')
    logg_from = Logg('gunicorn.log2', from_arg)
    logg_from.open_file()
    yield logg_from


def test_from_requests(logg_with_from):
    assert logg_with_from.output['requests'] == 36


def test_from_responses(logg_with_from):
    assert logg_with_from.output['responses'] == {'200': 36}


def test_from_2xx_size(logg_with_from):
    assert logg_with_from.output['2xx_size'] == [36, 25920]


def test_from_count_avg_2xx_size(logg_with_from):
    assert logg_with_from.output['avg_2xx_size'] == 720.0


def test_from_count_requests_per_seconds(logg_with_from):
    assert logg_with_from.output['requests_per_seconds'] == '12.0'


def test_from_display_output(logg_with_from):
    output = '''requests: 36
requests/sec: 12.0
responses: {'200': 36}
avg size of 2xx responses: 0.00 Mb (720 bytes)'''
    assert logg_with_from.display_output() == output


def test_from_check_if_date_in_range(logg_with_from):
    test_line_one = 'Dec 01 11:06:07 app3-test-vm1 gunicorn[53253]:' \
                    ' 172.16.3.14 - - [01/Dec/2019:11:06:07 +0100] ' \
                    '"GET /internal/user/03144bdb-805e-4a56-836f-3324a812fe0f/agenda/2019-12-01/2019-12-02 HTTP/1.1"' \
                    ' 200 720 "-" "python-requests/2.22.0" 402636'
    test_line_two = 'Dec 01 11:06:03 app3-test-vm1 gunicorn[53253]:' \
                    ' 172.16.3.14 - - [01/Dec/2019:11:06:03 +0100]' \
                    ' "GET /internal/user/9e4189b1-6d91-4bef-a80a-e9ebfb401ac6/agenda/2019-12-01/2019-12-02 HTTP/1.1"' \
                    ' 200 720 "-" "python-requests/2.22.0" 421824'
    assert logg_with_from.check_if_date_in_range(test_line_one) is True
    assert logg_with_from.check_if_date_in_range(test_line_two) is False


# requests: 47
# requests/sec: 11.8
# responses: {'404': 1, '200': 46}
# avg size of 2xx responses: 0.00 Mb (720 bytes)
# {'requests': 47, 'requests_per_sec': '', 'responses': {'404': 1, '200': 46}, '2xx_size': [46, 33120], 'avg_2xx_size': 720.0, 'requests_per_seconds': '11.8'}

@pytest.fixture(scope='module')
def logg_with_to():
    to_arg = datetime.strptime('30 11 2019 09 07 22', '%d %m %Y %H %M %S')
    from_arg = datetime.strptime('30 11 2019 09 07 18', '%d %m %Y %H %M %S') # first entry in the log file
    logg_to = Logg('gunicorn.log2', from_arg, to_arg)
    logg_to.open_file()
    yield logg_to


def test_to_requests(logg_with_to):
    assert logg_with_to.output['requests'] == 47


def test_to_responses(logg_with_to):
    assert logg_with_to.output['responses'] == {'404': 1, '200': 46}


def test_to_2xx_size(logg_with_to):
    assert logg_with_to.output['2xx_size'] == [46, 33120]


def test_to_count_avg_2xx_size(logg_with_to):
    assert logg_with_to.output['avg_2xx_size'] == 720.0


def test_to_count_requests_per_seconds(logg_with_to):
    assert logg_with_to.output['requests_per_seconds'] == '11.8'


def test_to_display_output(logg_with_to):
    output = '''requests: 47
requests/sec: 11.8
responses: {'404': 1, '200': 46}
avg size of 2xx responses: 0.00 Mb (720 bytes)'''
    assert logg_with_to.display_output() == output


def test_to_check_if_date_in_range(logg_with_to):
    test_line_one = 'Nov 30 09:07:22 actify3-test-vm1 gunicorn[53253]:' \
                    ' 172.16.3.14 - - [30/Nov/2019:09:07:22 +0100]' \
                    ' "GET /internal/user/abd25fb0-5fde-4388-a925-97b948037867/agenda/2019-11-30/2019-12-01 HTTP/1.1"' \
                    ' 200 720 "-" "python-requests/2.22.0" 60616'
    test_line_two = 'Dec 01 11:06:03 app3-test-vm1 gunicorn[53253]:' \
                    ' 172.16.3.14 - - [01/Dec/2019:11:06:03 +0100]' \
                    ' "GET /internal/user/9e4189b1-6d91-4bef-a80a-e9ebfb401ac6/agenda/2019-12-01/2019-12-02 HTTP/1.1"' \
                    ' 200 720 "-" "python-requests/2.22.0" 421824'
    assert logg_with_to.check_if_date_in_range(test_line_one) is True
    assert logg_with_to.check_if_date_in_range(test_line_two) is False

# requests: 2046
# requests/sec: 11.9
# responses: {'200': 2023, '404': 23}
# avg size of 2xx responses: 0.00 Mb (768 bytes)
# {'requests': 2046, 'requests_per_sec': '', 'responses': {'200': 2023, '404': 23}, '2xx_size': [2023, 1553556], 'avg_2xx_size': 767.9466139396935, 'requests_per_seconds': '11.9'}

@pytest.fixture(scope='module')
def logg_with_from_to():
    to_arg = datetime.strptime('30 11 2019 09 10 22', '%d %m %Y %H %M %S')
    from_arg = datetime.strptime('30 11 2019 09 07 22', '%d %m %Y %H %M %S') # first entry in the log file
    logg_from_to = Logg('gunicorn.log2', from_arg, to_arg)
    logg_from_to.open_file()
    yield logg_from_to


def test_from_to_requests(logg_with_from_to):
    assert logg_with_from_to.output['requests'] == 2046


def test_from_to_responses(logg_with_from_to):
    assert logg_with_from_to.output['responses'] == {'200': 2023, '404': 23}


def test_from_to_2xx_size(logg_with_from_to):
    assert logg_with_from_to.output['2xx_size'] == [2023, 1553556]


def test_from_to_count_avg_2xx_size(logg_with_from_to):
    assert logg_with_from_to.output['avg_2xx_size'] == 767.9466139396935


def test_from_to_count_requests_per_seconds(logg_with_from_to):
    assert logg_with_from_to.output['requests_per_seconds'] == '11.9'


def test_from_to_display_output(logg_with_from_to):
    output = '''requests: 2046
requests/sec: 11.9
responses: {'200': 2023, '404': 23}
avg size of 2xx responses: 0.00 Mb (768 bytes)'''
    assert logg_with_from_to.display_output() == output


def test_from_to_check_if_date_in_range(logg_with_from_to):
    test_line_one = 'Nov 30 09:07:22 actify3-test-vm1 gunicorn[53253]:' \
                    ' 172.16.3.14 - - [30/Nov/2019:09:07:22 +0100]' \
                    ' "GET /internal/user/abd25fb0-5fde-4388-a925-97b948037867/agenda/2019-11-30/2019-12-01 HTTP/1.1"' \
                    ' 200 720 "-" "python-requests/2.22.0" 60616'
    test_line_two = 'Dec 01 11:06:03 app3-test-vm1 gunicorn[53253]:' \
                    ' 172.16.3.14 - - [01/Dec/2019:11:06:03 +0100]' \
                    ' "GET /internal/user/9e4189b1-6d91-4bef-a80a-e9ebfb401ac6/agenda/2019-12-01/2019-12-02 HTTP/1.1"' \
                    ' 200 720 "-" "python-requests/2.22.0" 421824'
    assert logg_with_from_to.check_if_date_in_range(test_line_one) is True
    assert logg_with_from_to.check_if_date_in_range(test_line_two) is False

