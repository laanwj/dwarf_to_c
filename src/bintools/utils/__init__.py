"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""


class IntegerIntervals(object):
    def __init__(self):
        """
        interval: (min, max, value)
        The intervals list is sorted by minimum, checking against overlapping.
        """
        self.__intervals = []
    
    def __bisect(self, x):
        """
        Locate the insertion point for x in the intervals to maintain sorted min
        order. If x is already present in the intervals, the insertion point 
        will be after (to the right of) an existing entry.
        """
        lo = 0
        hi = len(self.__intervals)
        while lo < hi:
            mid = (lo+hi)//2
            v = self.__intervals[mid][0]
            if v <= x:
                lo = mid+1
                if v == x: break
            else:
                hi = mid
        return lo
    
    def add_interval(self, min, max, value):
        if min > max:
            raise Exception("min > max")
        
        if not self.__intervals:
            self.__intervals.append((min, max, value))
            return
        
        i = self.__bisect(min)
        if i != 0:
            prev_min, prev_max, _ = self.__intervals[i-1]
            if prev_max >= min:
                raise Exception("[%x-%x] overlaps [%x-%x]" % (min, max, prev_min, prev_max))
        if i != len(self.__intervals):
            next_min, next_max, _ = self.__intervals[i]
            if next_min <= max:
                raise Exception("[%x-%x] overlaps [%x-%x]" % (min, max, next_min, next_max))
        
        self.__intervals.insert(i, (min, max, value))
    
    def get(self, addr):
        """
        O(log n) interval look-up
        
        return = hit ? value : None
        """
        index = self.__bisect(addr)
        if index != 0:
            (min, max, value) = self.__intervals[index - 1]
            if addr >= min and addr <= max:
                return value
    
    def __str__(self):
        return '\n'.join(['[%x-%x] %s' % (min, max, str(value)[:10])
                          for (min, max, value) in self.__intervals])


class Enum(object):
    def __init__(self, dict):
        self.dict = dict
        self.name_dict = {}
        for key, name in self.dict.items():
            self.name_dict[name] = key
    
    def __getitem__(self, key):
        return self.dict[key]
    
    def __contains__(self, key):
        return key in self.dict
    
    def __getattr__(self, name):
        return self.name_dict[name]


def benchmark(func, *args, **kargs):
    from time import time
    start = time()
    func(*args, **kargs)
    tot = time() - start
    print('\n\nTot time: (%.2f)s' % tot)
