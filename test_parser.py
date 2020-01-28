from parser import Logg
from datetime import datetime
import pytest


@pytest.fixture(scope='module')
def logg():
    logg = Logg('gunicorn.log2')
    logg.check_arguments()
    logg.open_file()
    yield logg


@pytest.mark.no_args
def test_convert_time_frame(logg):
    assert logg.time_window == {
            'from': datetime.strptime('01 01 1970', '%d %m %Y'),
            'to': datetime.strptime('01 12 2019 11 06 07', '%d %m %Y %H %M %S'),
            'first': datetime.strptime('30 11 2019 09 07 18', '%d %m %Y %H %M %S'),
            'last': datetime.strptime('01 12 2019 11 06 07', '%d %m %Y %H %M %S')
        }
    assert logg.time_window != {
            'from': datetime.strptime('01 03 1970', '%d %m %Y'),
            'to': datetime.strptime('01 12 2020 11 06 07', '%d %m %Y %H %M %S'),
            'first': datetime.strptime('30 10 2019 09 07 18', '%d %m %Y %H %M %S'),
            'last': datetime.strptime('01 12 2019 11 06 07', '%d %m %Y %H %M %S')
        }


@pytest.mark.no_args
def test_requests(logg):
    assert logg.output['requests'] == 99999
    assert logg.output['requests'] != 99232


@pytest.mark.no_args
def test_responses(logg):
    assert logg.output['responses'] == {'200': 96205, '404': 3794}
    assert logg.output['responses'] != {'232': 96205, '404': 3794}

@pytest.mark.no_args
def test_2xx_size(logg):
    assert logg.output['2xx_size'] == [96205, 77519252]
    assert logg.output['2xx_size'] != [9620213235, 77519252]


@pytest.mark.no_args
def test_count_avg_2xx_size(logg):
    assert logg.output['avg_2xx_size'] == 805.7715503352217
    assert logg.output['avg_2xx_size'] != 343452217


@pytest.mark.no_args
def test_count_requests_per_seconds(logg):
    assert logg.output['requests_per_seconds'] == '1.1'
    assert logg.output['requests_per_seconds'] != '12'


@pytest.mark.no_args
def test_display_output(logg):
    output = '''requests: 99999
requests/sec: 1.1
responses: {'200': 96205, '404': 3794}
avg size of 2xx responses: 0.00 Mb (806 bytes)'''
    assert logg.display_output() == output


@pytest.mark.no_args
def test_check_if_date_in_range(logg):
    test_line_one = 'Dec 01 11:06:07 app3-test-vm1 gunicorn[53253]:' \
                ' 172.16.3.14 - - [01/Dec/2019:11:06:07 +0100]' \
                ' "GET /internal/user/03144bdb-805e-4a56-836f-3324a812fe0f/agenda/2019-12-01/2019-12-02 HTTP/1.1"' \
                ' 200 720 "-" "python-requests/2.22.0" 402636'
    test_line_two = 'Dec 01 11:06:03 app3-test-vm1 gunicorn[53253]:' \
                    ' 172.16.3.14 - - [01/Dec/2020:11:06:03 +0100]' \
                    ' "GET /internal/user/9e4189b1-6d91-4bef-a80a-e9ebfb401ac6/agenda/2019-12-01/2019-12-02 HTTP/1.1"' \
                    ' 200 720 "-" "python-requests/2.22.0" 421824'
    assert logg.check_if_date_in_range(test_line_one) is True
    assert logg.check_if_date_in_range(test_line_two) is False


@pytest.fixture(scope='module')
def logg_with_from():
    logg_from = Logg('gunicorn.log2', '01-12-2019_11-06-04')
    logg_from.check_arguments()
    logg_from.open_file()
    yield logg_from


@pytest.mark.fromm
def test_from_convert_time_frame(logg_with_from):
    assert logg_with_from.time_window == {
        'from': datetime.strptime('01 12 2019 11 06 04', '%d %m %Y %H %M %S'),
        'to': datetime.strptime('01 12 2019 11 06 07', '%d %m %Y %H %M %S'),
        'first': datetime.strptime('01 12 2019 11 06 04', '%d %m %Y %H %M %S'),
        'last': datetime.strptime('01 12 2019 11 06 07', '%d %m %Y %H %M %S')
    }
    assert logg_with_from.time_window != {
        'from': datetime.strptime('01 12 2019 11 06 04', '%d %m %Y %H %M %S'),
        'to': datetime.strptime('01 12 2019 11 06 07', '%d %m %Y %H %M %S'),
        'first': datetime.strptime('01 10 2019 11 06 04', '%d %m %Y %H %M %S'),
        'last': datetime.strptime('01 12 2019 11 06 07', '%d %m %Y %H %M %S')
    }


@pytest.mark.fromm
def test_from_requests(logg_with_from):
    assert logg_with_from.output['requests'] == 36
    assert logg_with_from.output['requests'] != 232


@pytest.mark.fromm
def test_from_responses(logg_with_from):
    assert logg_with_from.output['responses'] == {'200': 36}
    assert logg_with_from.output['responses'] != {'200': 323236}


@pytest.mark.fromm
def test_from_2xx_size(logg_with_from):
    assert logg_with_from.output['2xx_size'] == [36, 25920]
    assert logg_with_from.output['2xx_size'] != [36, 2534920]


@pytest.mark.fromm
def test_from_count_avg_2xx_size(logg_with_from):
    assert logg_with_from.output['avg_2xx_size'] == 720.0
    assert logg_with_from.output['avg_2xx_size'] != 7340.0


@pytest.mark.fromm
def test_from_count_requests_per_seconds(logg_with_from):
    assert logg_with_from.output['requests_per_seconds'] == '12.0'
    assert logg_with_from.output['requests_per_seconds'] != '1'


@pytest.mark.fromm
def test_from_display_output(logg_with_from):
    output = '''requests: 36
requests/sec: 12.0
responses: {'200': 36}
avg size of 2xx responses: 0.00 Mb (720 bytes)'''
    assert logg_with_from.display_output() == output


@pytest.mark.fromm
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


@pytest.fixture(scope='module')
def logg_with_to():
    logg_to = Logg('gunicorn.log2', None, '30-11-2019_09-07-22')
    logg_to.check_arguments()
    logg_to.open_file()
    yield logg_to


@pytest.mark.to
def test_to_convert_time_frame(logg_with_to):
    assert logg_with_to.time_window == {
            'from': datetime.strptime('01 01 1970', '%d %m %Y'),
            'to': datetime.strptime('30 11 2019 09 07 22', '%d %m %Y %H %M %S'),
            'first': datetime.strptime('30 11 2019 09 07 18', '%d %m %Y %H %M %S'),
            'last': datetime.strptime('30 11 2019 09 07 22', '%d %m %Y %H %M %S')
    }
    assert logg_with_to.time_window != {
        'from': datetime.strptime('01 01 1970', '%d %m %Y'),
        'to': datetime.strptime('30 12 2019 09 07 22', '%d %m %Y %H %M %S'),
        'first': datetime.strptime('30 11 2019 09 07 18', '%d %m %Y %H %M %S'),
        'last': datetime.strptime('30 11 2019 09 07 22', '%d %m %Y %H %M %S')
    }


@pytest.mark.to
def test_to_requests(logg_with_to):
    assert logg_with_to.output['requests'] == 47
    assert logg_with_to.output['requests'] != 472


@pytest.mark.to
def test_to_responses(logg_with_to):
    assert logg_with_to.output['responses'] == {'404': 1, '200': 46}
    assert logg_with_to.output['responses'] != {'40422': 1, '200': 46}


@pytest.mark.to
def test_to_2xx_size(logg_with_to):
    assert logg_with_to.output['2xx_size'] == [46, 33120]
    assert logg_with_to.output['2xx_size'] != [436, 33122320]


@pytest.mark.to
def test_to_count_avg_2xx_size(logg_with_to):
    assert logg_with_to.output['avg_2xx_size'] == 720.0
    assert logg_with_to.output['avg_2xx_size'] != 2323


@pytest.mark.to
def test_to_count_requests_per_seconds(logg_with_to):
    assert logg_with_to.output['requests_per_seconds'] == '11.8'
    assert logg_with_to.output['requests_per_seconds'] != '11.54'


@pytest.mark.to
def test_to_display_output(logg_with_to):
    output = '''requests: 47
requests/sec: 11.8
responses: {'404': 1, '200': 46}
avg size of 2xx responses: 0.00 Mb (720 bytes)'''
    assert logg_with_to.display_output() == output


@pytest.mark.to
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


@pytest.fixture(scope='module')
def logg_with_from_to():
    logg_from_to = Logg('gunicorn.log2', '30-11-2019_09-07-22', '30-11-2019_09-10-22')
    logg_from_to.check_arguments()
    logg_from_to.open_file()
    yield logg_from_to


@pytest.mark.from_to
def test_from_to_convert_time_frame(logg_with_from_to):
    assert logg_with_from_to.time_window == {
            'from': datetime.strptime('30 11 2019 09 07 22', '%d %m %Y %H %M %S'),
            'to': datetime.strptime('30 11 2019 09 10 22', '%d %m %Y %H %M %S'),
            'first': datetime.strptime('30 11 2019 09 07 22', '%d %m %Y %H %M %S'),
            'last': datetime.strptime('30 11 2019 09 10 14', '%d %m %Y %H %M %S')
    }
    assert logg_with_from_to.time_window != {
        'from': datetime.strptime('30 11 2020 09 07 22', '%d %m %Y %H %M %S'),
        'to': datetime.strptime('30 11 2019 09 10 22', '%d %m %Y %H %M %S'),
        'first': datetime.strptime('30 11 2019 09 07 22', '%d %m %Y %H %M %S'),
        'last': datetime.strptime('30 11 2019 09 10 14', '%d %m %Y %H %M %S')
    }


@pytest.mark.from_to
def test_from_to_requests(logg_with_from_to):
    assert logg_with_from_to.output['requests'] == 2046
    assert logg_with_from_to.output['requests'] != 2046322


@pytest.mark.from_to
def test_from_to_responses(logg_with_from_to):
    assert logg_with_from_to.output['responses'] == {'200': 2023, '404': 23}
    assert logg_with_from_to.output['responses'] != {'2220': 2023, '404': 23}


@pytest.mark.from_to
def test_from_to_2xx_size(logg_with_from_to):
    assert logg_with_from_to.output['2xx_size'] == [2023, 1553556]
    assert logg_with_from_to.output['2xx_size'] != [2023, 15343453556]


@pytest.mark.from_to
def test_from_to_count_avg_2xx_size(logg_with_from_to):
    assert logg_with_from_to.output['avg_2xx_size'] == 767.9466139396935
    assert logg_with_from_to.output['avg_2xx_size'] != 767.94661393934346935


@pytest.mark.from_to
def test_from_to_count_requests_per_seconds(logg_with_from_to):
    assert logg_with_from_to.output['requests_per_seconds'] == '11.9'
    assert logg_with_from_to.output['requests_per_seconds'] != '114.9'


@pytest.mark.from_to
def test_from_to_display_output(logg_with_from_to):
    output = '''requests: 2046
requests/sec: 11.9
responses: {'200': 2023, '404': 23}
avg size of 2xx responses: 0.00 Mb (768 bytes)'''
    assert logg_with_from_to.display_output() == output


@pytest.mark.from_to
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
