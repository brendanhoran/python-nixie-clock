import clock
import pytest
from mock import MagicMock
from unittest.mock import patch



date_time_test_value = '20200516133010'

# def test_get_time_date_data(mocker):
#    mocker.patch('clock.SerialWrite.write_data')
#    mocker.patch('clock.datetime.datetime')
#    # with patch('clock.datetime.datetime') as brr:
#        # brr.return_value = '232'
#    assert clock.get_time_date_data('pc') == date_time_test_value


def test_format_time():
    assert clock.format_time(date_time_test_value) == '133010'


def test_format_date():
    assert clock.format_date(date_time_test_value) == '20200516'
