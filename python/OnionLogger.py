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

# max at roughly 25MB mem, that's a lot of logs
# Change to 0 for unlimited
MAX_LOGS = 49999
KEEP_UNIQUE_ONLY = False
VERBOSITY = logging.INFO

# set up stream handler to shell
formatter = logging.Formatter(
    '%(asctime)s | %(name)s |  %(levelname)s: %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)
_LOGGER.addHandler(stream_handler)


class SortBy(object):
    Function, Level, Time = range(3)


class Msg(object):

    def __init__(self, message_str, level=None) -> None:
        self.message = message_str
        self._level = level
        self._time = time.time()

        self._stack = '/'.join([fr.function for fr in inspect.stack()[3:]])
        self._function = self._stack.split('/')[0]

    def __eq__(self, other):
        return self.message == other.message

    def __ne__(self, other):
        return self.message != other.message

    def __repr__(self) -> str:
        return '<OnionLogger.Msg(time={}, level={}, function={}) at {:x}>' \
               ''.format(self._time, self._level, self._function, id(self))


class Logger(object):

    def __init__(self, name=__name__):
        self._messages = []
        self.name = name

    def __repr__(self) -> str:
        return '<OnionLogger.Logger(len(self._messages)={}, at {:x}>' \
               ''.format(len(self._messages), id(self))

    @property
    def len(self):
        return len(self._messages)

    @property
    def messages(self):
        return self._messages

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
        """
        Base logging method for appending logs to self at set verbosity level.

        Args:
            msg : (str)
            level : (int)
        """
        message = Msg(msg, level=level)

        # print if meets verbosity criteria
        if level >= VERBOSITY:
            _LOGGER.log(level=level, msg=msg)

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

    def sorted(self, sort_order):
        if sort_order == SortBy.Time:
            return self.return_time_sort()
        elif sort_order == SortBy.Level:
            return self.return_level_sort()
        elif sort_order == SortBy.Function:
            return self.return_func_sort()
        else:
            raise ValueError('Expecting SortBy attribute as argument')

    # other methods
    def reset(self):
        """
        Erase all logs
        """
        self._messages = []
        _LOGGER.info('OnionLogger reset, logs erased')

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


def load_from_disk(path=None):
    with open(path, 'rb') as w:
        onion = pickle.loads(w.read())
    return onion
