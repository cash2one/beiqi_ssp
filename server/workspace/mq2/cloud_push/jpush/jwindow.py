#coding:utf-8


class JPushRecvWindow(object):
    def __init__(self):
        #先设置一个较大的值
        self.__max_win = 0
        self.__recv_win = 0xffff
        self.__reset = 60

    def update_win(self, d):
        self.__max_win = d.get('X-Rate-Limit-Limit')
        self.__recv_win = d.get('X-Rate-Limit-Remaining')
        self.__reset = d.get('X-Rate-Limit-Reset')

    