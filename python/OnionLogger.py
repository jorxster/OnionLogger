#!/usr/bin/env python3
"""
OnionLogger for easy inheritance and hiearchical logging with dynamic sorting.
"""
__author__ = 'jorxster@gmail.com'
__date__ = '27 May 2018'
__version__ = "0.1.0"

import inspect
import logging
import os
import pickle
import tempfile
import time

# max at roughly 50MB mem, that's a lot of logs
# Change to 0 for unlimited
MAX_LOGS = 49999
KEEP_UNIQUE_ONLY = False
VERBOSITY = logging.INFO


class Msg(object):
    SORTING_KEYS = ['level', 'time']

    def __init__(self, message_str, level=None) -> None:
        for key in self.SORTING_KEYS:
            self.__dict__['_' + key] = None
        self.message = message_str
        self._level = level
        self._time = time.time()
        self._function = inspect.stack()[3].function

    def __eq__(self, other):
        return self.message == other.message

    def __ne__(self, other):
        return self.message != other.message

    def __repr__(self) -> str:
        return '<OnionLogger.Msg(time={}, level={}, function={}) at {:x}>' \
               ''.format(self._time, self._level, self._function, id(self))


class Logger(object):

    def __init__(self):
        self._messages = []
        self._len = 0

    @property
    def len(self):
        return len(self._messages)

    # Standard methods
    def debug(self, msg):
        self.log(msg, level=logging.DEBUG)

    def info(self, msg):
        self.log(msg)

    def warn(self, msg):
        self.log(msg, level=logging.WARN)

    def critical(self, msg):
        self.log(msg, level=logging.CRITICAL)

    # Base method
    def log(self, msg, level=logging.INFO):

        message = Msg(msg, level=level)

        # print if meets verbosity criteria
        if level >= VERBOSITY:
            # TODO : replace this with logging
            print(msg)

        # if discarding duplicate logs
        if KEEP_UNIQUE_ONLY:
            try:
                self._messages.remove(message)
            except ValueError:
                pass
        self._messages.append(message)

        # if limit exceeded, pop first-most item
        if MAX_LOGS:
            if self.len > MAX_LOGS:
                self._messages.pop(0)

    # sorted return methods
    def return_time_sort(self):
        return sorted(self._messages, key=lambda x: x._time)

    def return_level_sort(self):
        return sorted(self._messages, key=lambda x: x._level)

    def return_func_sort(self):
        return sorted(self._messages, key=lambda x: x._function)

    # other methods
    def reset(self):
        """
        Erase all logs
        """
        self._messages = []
        self.info('OnionLogger reset, logs erased')

    def serialize(self):
        return pickle.dumps(self)

    def save_to_disk(self, path=None):

        if not path:
            # construct temp / time filepath
            path = os.path.join(
                tempfile.gettempdir(),
                time.strftime('%Y%m%d_%H%M%S.olog')
            )

        with open(path, 'wb') as w:
            self.log('OnionLogger.Logger: serializing and '
                     'writing to path -- \n\t{}'.format(path))
            w.write(self.serialize())
