#coding: utf-8
# Author:zk   2018.7.19
import collections
import time
import sys
import threading
from threading import Thread
import logging
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.WARN)


class pb2:
    __od = collections.OrderedDict()
    __lock = threading.RLock()
    __dirty = False
    __instance = None
    __currentIconIdx = 0
    __istty=sys.stdout.isatty()
    if not __istty:
        logger.warning("WARNNING:pb2 not in tty! only support one line. multi line not supported")

    def up(self):
        if self.__istty:
            sys.stdout.write('\x1b[1A')
            sys.stdout.flush()


    def down(self):
        if self.__istty:
            sys.stdout.write('\n')
            sys.stdout.flush()

    @classmethod
    def getSingleton(cls):
        if not cls.__instance:
            with cls.__lock:
                if not cls.__instance:
                    cls.__instance = cls()
        return cls.__instance

    def __init__(self) -> None:
        super().__init__()
        self.___demon()

    def ___demon(self):
        t = Thread(target=self.paint)
        t.daemon = True
        t.start()

    def update(self, tag, nowValue, fullValue,extrainfo=None, customVisualbar=None):
        with self.__lock:
            self.__od[tag] = self.customVisualbar(tag, nowValue, fullValue,extrainfo) if customVisualbar is None else customVisualbar(tag, nowValue, fullValue,extrainfo)

            self.__dirty = True

    def customVisualbar(self, tag, nowValue, fullValue,extrainfo=""):
        bar_length = 100
        percent = float(nowValue) / fullValue
        arrow = '-' * int(round(percent * bar_length) - 1) + '>'
        spaces = ' ' * (bar_length - len(arrow))
        return "{2} [{0}] {1}%  {3}".format(arrow + spaces, int(round(percent * 100)), tag,extrainfo)

    # print after bar
    def print(self, str):
        with self.__lock:
            self.__od[time.time()] = str
            self.__dirty = True

    #   print before bar
    # def insert_print(self, str):
    #     with self.__lock:
    #         time_time = time.time()
    #         columns, rows = shutil.get_terminal_size()
    #         self.__od[time_time] = str+' '*(columns-len(str)    )
    #         self.__od.move_to_end(time_time, last=False)
    #         self.__dirty = True
    def start(self):

        with self.__lock:
            self.__paint()
            for i in range(len(self.__od)):
                self.down()
            self.__od.clear()

    def stop(self):
        self.start()

    def paint(self):
        while True:
            if not self.__dirty:
                time.sleep(0.1)
                continue
            self.__lock.acquire()
            self.__paint()
            self.__lock.release()

    def __paint(self):
        text = ""
        for _, v in self.__od.items():
            if self.__istty:
                print(v)
            else:
                print("\r"+v,end='')
        for i in range(len(self.__od)):
            self.up()
        self.__dirty = False
