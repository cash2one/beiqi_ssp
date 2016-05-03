# coding=utf-8
"""
Created on 2015-4-22

@author: Jay
"""


class Singleton(type):   
    def __init__(cls, name, bases, dict_value):
        super(Singleton, cls).__init__(name, bases, dict_value)
        cls._instance = None   

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:   
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance  


if __name__ == "__main__":
    class Test():
        __metaclass__ = Singleton

        def __init__(self):
            pass
        
    one = Test()
    two = Test()
    
    one.a = 1
    two.a = 2
    
    print one.a, two.a

    class Test1():
        __metaclass__ = Singleton

        def __init__(self, a, b):
            self.a = a
            self.b = b

    thrid = Test1("test1", "test2")
    print thrid.__dict__
    print Test1().__dict__
    print Test1("test11", "test22").__dict__
    print Test1().__dict__
    assert thrid.a == "test1"