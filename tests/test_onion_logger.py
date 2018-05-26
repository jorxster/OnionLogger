#!/usr/bin/env python3

import os
import sys

THIS_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(THIS_PATH + '/python')
sys.path.append(THIS_PATH + '/python')
import OnionLogger


def main():
    logger = OnionLogger.Logger()
    logger.test()
    print(logger.return_func_sort())


if __name__ == '__main__':
    main()