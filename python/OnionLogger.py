import inspect
import logging
import time

SORTING_KEYS = ['level', 'time', 'func_name']


class Msg(object):
    def __init__(self, message_str, level=None) -> None:
        for key in SORTING_KEYS:
            self.__dict__['_' + key] = None
        self.message = message_str
        self._level = level
        self._time = time.time()
        self._function = inspect.stack()[2].function
        print('FUNC {}'.format(self._function))

    def __repr__(self) -> str:
        return '<OnionLogger.Msg(time={}, level={}, function={}) at {:x}>' \
               ''.format(self._time, self._level, self._function, id(self))


class Logger(object):

    def __init__(self):
        self._messages = []

    def log(self, msg, level=logging.INFO):

        message = Msg(msg, level=level)
        self._messages.append(message)

    def return_time_sort(self):
        return sorted(self._messages, key=lambda x: x._time)

    def return_level_sort(self):
        return sorted(self._messages, key=lambda x: x._level)

    def return_func_sort(self):
        return sorted(self._messages, key=lambda x: x._function)

    def test(self):

        for i in range(0, 10):
            self.test2()
            self.log('Privet')

    def test2(self):
        self.log('Hello World')
