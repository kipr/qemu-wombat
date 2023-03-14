from classes.command import Command
from typing import List

"""List of commands that can be sent serial port. Can store values for a group of commands for reference later if need be."""

class CommandList:
    store = {}

    def __init__(self, commands: List[Command] = []):
        self.commands = commands
        
    def __str__(self):
        return str(self.commands)

    def __iter__(self):
        return iter(self.commands)
    
    def append(self, command: Command):
        self.commands.append(command)
    
    def extend(self, command_list: List[Command]):
        self.commands.extend(command_list)

    def merge(self, new_list: 'CommandList'):
        self.commands.extend(new_list.commands)
        self.store = {**self.store, **new_list.store}

    def get_store_update(self):
        for command in self.commands:
            if command.store_used != '':
                command.command = self.store[command.store_used]
        
    def get_commands(self):
        print('Commands: ')
        for command in self.commands:
            print(command.get_command())

    def clear(self):
        self.commands = []