class Count(object):
    def __init__(self, low, high) -> None:
        self.low = low
        self.hight = high

    def ___iter__(self):
        return self

    def __next__(self):
        if self.current > self.high:
            raise StopIteration
        else:
            self.current += 1
            return self.current -1

c = Count(0, 2)
