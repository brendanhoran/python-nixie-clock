import clock
import pytest
from mock import MagicMock
from unittest.mock import patch
from unittest import mock


class Test_Clock:
    @pytest.fixture
    def fixture_test_date_time_value(self):
        date_time_test_value = '20200516133010'
        return date_time_test_value

    @pytest.fixture
    def fixture_seriaL_device(self, mocker):
        ''' Mock serial device '''
        self.mock_serial_write = mocker.patch('clock.SerialWrite.write_data')

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

    def test_format_time(self, fixture_test_date_time_value):
        ''' test we format the time value correctly from the full date_time object '''
        assert clock.format_time(fixture_test_date_time_value) == '133010'

    def test_format_date(self, fixture_test_date_time_value):
        ''' test we format date value correct from the full date_time object '''
        assert clock.format_date(fixture_test_date_time_value) == '20200516'

    #def test_getting_date_time_object_pc_format_24h(self, fixture_test_date_time_value):
    #    assert clock.get_time_date_data('pc', '24h') == '20200516133010'

