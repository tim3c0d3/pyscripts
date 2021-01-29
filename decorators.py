#!/usr/bin/env python

def before(func):
    """
        Decorator Function: Execute `func` before decorated function

    """
    def internal(decorated):
        def inner(*a, **kw):
            func()
            if a or kw:
                decorated(*a, **kw)
            else:
                decorated()
        
        return inner
    
    return internal

def e():
    print "e"

@before(e)
def f(*a):
    print a
    print "f"

@before(e)
def g():
    print "g"

f("1")
g()

def after(func):
    """
        Decorator Function: Execute `func` after decorated function

    """
    def internal(decorated):
        def inner(*a, **kw):
            if a or kw:
                decorated(*a, **kw)
            else:
                decorated()
            
            func()
            
        return inner
    
    return internal

def k():
    print "k"

@after(k)
def h(*a):
    print "h"

@after(k)
def j():
    print "j"

h()
j()