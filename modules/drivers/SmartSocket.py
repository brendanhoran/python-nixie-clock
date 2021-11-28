from util import SerialUart

# class B7Settings:
    # def __init__(self):
        # Not done, maybe won't do
        # idea here is to wrap the tube counting function
        # work out max length for all helper settings

        # do we want all sockets to behave the same
        # if so then set __init__ to work out max length


def b7_effect(serial_device, message):
    ''' Set the transition effect type '''
    _command_prefix = '$B7E'
    set_b7_effect = SerialUart.SerialWrite(serial_device)

    set_b7_effect.write_data(_command_prefix+message)


def b7_effect_speed(serial_device, message):
    ''' Set the transition effect speed '''
    _command_prefix = '$B7S'
    set_b7_effect_speed = SerialUart.SerialWrite(serial_device)

    set_b7_effect_speed.write_data(_command_prefix+message)


def b7_font(serial_device, message):
    ''' Set the font to use  on a tube '''
    _command_prefix = '$B7F'
    set_b7_font = SerialUart.SerialWrite(serial_device)

    set_b7_font.write_data(_command_prefix+message)


def b7_message(serial_device, message):
    ''' Write a character to a tube '''
    _command_prefix = '$B7M'
    write_b7_message = SerialUart.SerialWrite(serial_device)

    def _reverse_helper(string):
        """ Ugly helper function since micropython can't split on steps under 1 """
        # https://github.com/micropython/micropython/blob/b9ec6037edf5e6ff6f8f400d70f7351d1b0af67d/py/objstrunicode.c#L189
        reverse = ""
        for character in string:
            reverse = character+reverse
        return reverse

    if serial_device == 'micropython':
        # Use helper to flip the string for MicroPython
        message = _reverse_helper(message)
        write_b7_message.write_data(_command_prefix+message.upper())
    else:
        # Flip the message, socket order is reversed
        message = message[::-1]
        write_b7_message.write_data(_command_prefix+message.upper())


def b7_blank_tube(serial_device, message):
    ''' Blank the tube display, all segments off '''

    # This is not working, only blanks first tube
    # no way to select a tube location

    _command_prefix = '$B7M'
    blank_tube = SerialUart.SerialWrite(serial_device)

    # Space char(ASCII 32) will blank a tube
    blank_tube.write_data(_command_prefix+' ')


def b7_underscore(serial_device, message):
    ''' Set the underscore on or off at a given location '''
    _command_prefix = '$B7U'
    set_b7_underscore = SerialUart.SerialWrite(serial_device)

    set_b7_underscore.write_data(_command_prefix+message)


def clear_state(socket_count, serial_device):
    ''' Clear all states in the PIC ensure a known state to start in '''
    # This sets up each smart socket to be in a decent state
    # Sometimes unexpected shutdown causes the PIC to spit crap data
    # A decent state to us is as follows :
    #     1 second transition speed
    #     No active transition pattern
    #     Each socket blanked
    socket_count = int(socket_count)
    b7_effect_speed(serial_device, ('1' * socket_count))
    b7_effect(serial_device, ('0' * socket_count))
    b7_underscore(serial_device, ('0' * socket_count))

    # Space char(ASCII 32) sent to all tubes to blank the display
    b7_message(serial_device, (' ' * socket_count))
    print('clear state')