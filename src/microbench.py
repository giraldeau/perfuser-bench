#!/usr/bin/env python3

#from linuxProfile import api
import traceback
import time

out = open("traceback.out", "w")

def foo(n):
    if (n > 0):
        foo(n - 1)
    else:
        traceback.print_stack(file=out)

if __name__=="__main__":
    x = 0
    samples = []
    t1 = time.clock()
    while(x < 100):
        foo(10)
        t2 = time.clock()
        samples.append(t2 - t1)
        x += 1
    