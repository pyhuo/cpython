#!/bin/python
def foo(x):
    return x ** 2

def bar(x):
    y = x /2
    return y

def is_cmp(x, y):
    ret = x == y
    ret_is = x is y
    return ret, ret_is

foo(2)
is_cmp(2, 3)
