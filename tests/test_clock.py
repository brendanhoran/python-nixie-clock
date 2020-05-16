import clock
import serial
from mock import MagicMock
from unittest.mock import patch



date_time_test_value = '20200516133010'

def test_get_time_date_data(mocker):
	mocker.patch('clock.write_data')
	with patch('clock.datetime.datetime.now') as brr:
	    brr.return_value = '232'
	    assert clock.get_time_date_data('pc') == date_time_test_value



def test_format_time():
	assert clock.format_time(date_time_test_value) == '133010'

def test_format_date():
	assert clock.format_date(date_time_test_value) == '20200516'