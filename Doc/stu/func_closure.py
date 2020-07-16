
def foo(x):
    def bar(y):
        ret = x + y
        return ret
    return bar


b1 = foo(1)
b10 = foo(10)