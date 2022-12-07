"""Command that can be sent serial port and with options for:
    - Alternate wait strings from command prompt 
    - Names in case it needs to be referenced
    - Buffer parser functions for outputs
    - Referencing known stored values in a command list or other list
"""

class Command:
    buffer: str = None

    def __init__(self, command: str, validator: str = '', alt_wait_string: str = '',name: str = '', buf_func = None, store_used: str = ''):
        self.command = command
        self.validator = validator
        self.alt_wait_string = alt_wait_string
        self.name = name
        self.buf_func = buf_func
        self.store_used = store_used

    def __str__(self):
        return self.command + " " + " ".join(self.validator)

    def validate(self, buffer):
        if self.validator == '':
            return True
        else:
            return self.validator in buffer

    def buffer_parser(self, buffer):
        self.buffer = buffer
        if self.buf_func != None:
            self.buf_func(self.buffer)
    
