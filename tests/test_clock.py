import clock
import pytest
import datetime
from mock import patch, Mock


class Test_Clock:
    @pytest.fixture
    def fixture_test_date_time_value_24H(self):
        date_time_test_value = '20200516133010'
        return date_time_test_value

    @pytest.fixture
    def fixture_test_date_time_value_12H(self):
        date_time_test_value = '20200516013010'
        return date_time_test_value

    @pytest.fixture
    def fixture_seriaL_device(self, mocker):
        ''' Mock serial device '''
        self.mock_serial_write = mocker.patch('clock.SerialWrite.write_data')

    @pytest.fixture
    def fixture_mock_date_time_value(self, mocker):
        ''' This mock's out pythons datetime object so we have a consistent date '''
        _test_timedate_value = '20200516133010'

        self.mock_datatime_object = mocker.patch('clock.datetime.datetime')
        self.mock_datatime_object.now.return_value = datetime.datetime(_test_timedate_value)

    def test_b7_effect(self, fixture_seriaL_device, mocker):
        ''' test the format of the effect command '''
        message = '88'
        clock.b7_effect(fixture_seriaL_device, message)

        self.mock_serial_write.assert_called_with('$B7E88')

    def test_b7_effect_speed(self, fixture_seriaL_device):
        '''  test the format of the effect speed command '''
        message = '11'

        clock.b7_effect_speed(fixture_seriaL_device, message)

        self.mock_serial_write.assert_called_with('$B7S11')

    def test_b7_message(self, fixture_seriaL_device):
        ''' test the format of the message command '''
        message = 'hello'

        clock.b7_message(fixture_seriaL_device, message)

        # Message command reverses the order of the items
        # message should be backwards as this is how the smart socket work
        self.mock_serial_write.assert_called_with('$B7MOLLEH')

    def test_b7_underscore(self, fixture_seriaL_device):
        ''' test the format of the underscore command '''
        message = '11'

        clock.b7_underscore(fixture_seriaL_device, message)

        self.mock_serial_write.assert_called_with('$B7U11')

    def test_b7_font(self, fixture_seriaL_device):
        ''' test the format of the font command '''
        message = '11'

        clock.b7_font(fixture_seriaL_device, message)

        self.mock_serial_write.assert_called_with('$B7F11')

    def test_format_time(self, fixture_test_date_time_value_24H):
        ''' test we format the time value correctly from the full date_time object '''
        assert clock.format_time(fixture_test_date_time_value_24H) == '133010'

    def test_format_date(self, fixture_test_date_time_value_24H):
        ''' test we format date value correct from the full date_time object '''
        assert clock.format_date(fixture_test_date_time_value_24H) == '20200516'

    @patch.object(clock, 'datetime', Mock(wraps=datetime))
    def test_getting_date_time_object_pc_format_24h(self, fixture_test_date_time_value_24H):
        ''' Test getting PC time date in 24H format '''

        _time_date_value = '2020-05-16 13:30:10.253043'
        _datetime_now = datetime.datetime.strptime(_time_date_value, '%Y-%m-%d %H:%M:%S.%f')

        clock.datetime.datetime.now.return_value = _datetime_now

        assert clock.get_time_date_data('pc', '24h') == fixture_test_date_time_value_24H

    @patch.object(clock, 'datetime', Mock(wraps=datetime))
    def test_getting_date_time_object_pc_format_12h(self, fixture_test_date_time_value_12H):
        ''' Test getting PC time date in 12H format '''

        _time_date_value = '2020-05-16 01:30:10.253043'
        _datetime_now = datetime.datetime.strptime(_time_date_value, '%Y-%m-%d %H:%M:%S.%f')

        clock.datetime.datetime.now.return_value = _datetime_now

        assert clock.get_time_date_data('pc', '12h') == fixture_test_date_time_value_12H
