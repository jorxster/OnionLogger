#!/usr/bin/env python3
import logging, os, sys, unittest

THIS_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(THIS_PATH + '/python')
import OnionLogger


class TestOnionLogger(unittest.TestCase):

    def setUp(self):
        self.instance = OnionLogger.Logger('TestModuleName')

    def generic_function1(self, message):
        self.instance.warn(message)

    def generic_function2(self, message):
        self.instance.warn(message)

    def test_serializing(self):
        self.generic_function1('Quoth the raven, \'Nevermore\'')
        self.generic_function2('Quoth the raven once more, \'Nevermore\'')
        for i in range(32):
            self.instance.warn('Testing integer {}'.format(i))
        self.instance.save_to_disk()
        self.instance.reset()

    def nested(self):
        self.instance.warn('\'Tis the wind and nothing more!')

    def test_inspection(self):
        self.nested()
        self.assertEqual(
            self.instance._messages[-1]._function,
            'nested')
        self.instance.reset()

    def test_max_limit(self):
        """
        Test the MAX_LOGS constant. This pops items from
        the beginning of the list of logs keeping the total
        under the maximum allowed.
        """
        OnionLogger.MAX_LOGS = 3
        for x in range(5):
            self.instance.log(x)

        self.assertEqual(self.instance.len, 3)
        self.instance._messages = []

        OnionLogger.MAX_LOGS = 0
        for x in range(5):
            self.instance.debug(x)
        self.assertEqual(self.instance.len, 5)
        self.instance.reset()

    def test_keep_unique_only(self):
        """
        Test the KEEP_UNIQUE_ONLY constant. This ensures
        that duplicates logs are removed keeping only the
        latest.
        """
        self.instance.max_limit = 0
        OnionLogger.KEEP_UNIQUE_ONLY = True
        for x in range(10):
            self.instance.debug('Ominous bird of yore.')
        self.assertEqual(len(self.instance._messages), 1)
        self.assertEqual(self.instance.len, 1)
        self.instance.reset()
        OnionLogger.KEEP_UNIQUE_ONLY = False


if __name__ == '__main__':
    logger = OnionLogger.Logger()
    print(logger.return_func_sort())
