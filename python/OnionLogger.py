import inspect
import logging
import pickle
import time

# max at roughly 50MB mem, that's a lot of logs
# Change to 0 for unlimited
MAX_LOGS = 49999
KEEP_UNIQUE_ONLY = False


class Msg(object):
    SORTING_KEYS = ['level', 'time', 'func_name']

    def __init__(self, message_str, level=None) -> None:
        for key in self.SORTING_KEYS:
            self.__dict__['_' + key] = None
        self.message = message_str
        self._level = level
        self._time = time.time()
        self._function = inspect.stack()[2].function

    def __repr__(self) -> str:
        return '<OnionLogger.Msg(time={}, level={}, function={}) at {:x}>' \
               ''.format(self._time, self._level, self._function, id(self))


class Logger(object):

    def __init__(self):
        self._messages = []
        self.len = 0
        self.max_limit = MAX_LOGS

    # Standard methods
    def info(self, msg):
        self.log(msg)

    def warn(self, msg):
        self.log(msg, level=logging.WARN)

    def critical(self, msg):
        self.log(msg, level=logging.CRITICAL)

    # Base method
    def log(self, msg, level=logging.INFO):

        # if discarding duplicate logs
        if KEEP_UNIQUE_ONLY:
            try:
                self._messages.remove(msg)
            except ValueError:
                pass

        message = Msg(msg, level=level)
        self._messages.append(message)
        self.len += 1

        # if limit exceeded, pop first-most item
        if self.max_limit:
            if self.len > self.max_limit:
                self._messages.pop(0)

    # sorted return methods
    def return_time_sort(self):
        return sorted(self._messages, key=lambda x: x._time)

    def return_level_sort(self):
        return sorted(self._messages, key=lambda x: x._level)

    def return_func_sort(self):
        return sorted(self._messages, key=lambda x: x._function)

    def serialize(self):
        return pickle.dumps(self)

    def save_to_disk(self, path):
        with open(path, 'rb') as w:
            w.write(self.serialize)

    # Todo: delete test functions
    def test(self):

        for i in range(0, 10):
            self.test2()
            self.log('Privet')

    def test2(self):
        self.log('Hello World')
