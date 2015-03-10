'''
Created on Mar 5, 2015

@author: francis
'''
from linuxProfile import api, utils
from perfuserBench import ext
import time
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import sys
import math
import cProfile, pstats

def f_00(fn, *args, **kwargs):
    fn(*args, **kwargs)

def f_01(fn, *args, **kwargs):
    fn(*args, **kwargs)

def f_02(fn, *args, **kwargs):
    fn(*args, **kwargs)

def f_03(fn, *args, **kwargs):
    fn(*args, **kwargs)

def f_04(fn, *args, **kwargs):
    fn(*args, **kwargs)

def f_05(fn, *args, **kwargs):
    fn(*args, **kwargs)

def f_06(fn, *args, **kwargs):
    fn(*args, **kwargs)

def f_07(fn, *args, **kwargs):
    fn(*args, **kwargs)

def f_08(fn, *args, **kwargs):
    fn(*args, **kwargs)

def f_09(fn, *args, **kwargs):
    fn(*args, **kwargs)

def burn(size=0):
    data = list(range(size))
    data.reverse()
    data.sort()

profile_simple = [
    (f_00, 50), (f_01, 20), (f_02, 15), (f_03, 5), (f_04, 5),
    (f_05, 1), (f_06, 1), (f_07, 1), (f_08, 1), (f_09, 1),
]


class ProgressBar(object):
    def __init__(self, total_work=1, width=40):
        self._total_work = float(total_work)
        self._width = width
        self._state = 0
    def update(self, current):
        bar = int(math.ceil((current / self._total_work) * self._width))
        if (bar == self._state):
            return
        space = self._width - bar
        sys.stdout.write("[{}{}]\r".format("#" * bar, " " * space))
        sys.stdout.flush()
        self._state = bar
    def done(self):
        sys.stdout.write("\ndone\n")
        sys.stdout.flush()

def do_check_linear(args):
    check_linear(burn)

def check_linear(func=burn, max_power=20, max_repeat=100):
    data = { 'size': [], 'time': [] }
    bar = ProgressBar(total_work=max_power * max_repeat)
    work = 0
    for _ in range(max_repeat):
        for power in range(max_power):
            size = 2 ** power
            bar.update(work)
            t1 = time.clock()
            burn(size)
            t2 = time.clock()
            delta = t2 - t1
            data['size'].append(size)
            data['time'].append(delta)
            work += 1
    bar.done()
    df = pd.DataFrame(data)
    grp = df.groupby('size')
    res = grp['time'].aggregate([np.mean, np.std]).reset_index()
    res['iter_ns'] = res['mean'] / res['size'] * 1000000000
    print(res)
    # r = res['mean'].corr(res['size'])
    # model = pd.ols(y=res['mean'], x=res['size'])
    # print(model.summary)
    # print(model.sm_ols.outlier_test())
    # print("correlation size v.s. mean: {}".format(r))
    # p = res.plot(x='size', y='mean')
    # p.set_yscale('log')
    # p.set_xscale('log')
    # plt.show()

def do_experiment(repeat, chunk, factors):
    for _ in range(repeat):
        for fn, param in factors:
            fn(burn, param * chunk)

def do_cprofile(repeat, chunk, factors):
    pr = cProfile.Profile()
    pr.enable()
    do_experiment(repeat, chunk, factors)
    pr.disable()
    s = pstats.Stats(pr).sort_stats('cumulative')
    s.print_callers()
    s.print_stats()

def do_linuxprofile(repeat, chunk, factors):
    api.enable_perf()
    do_experiment(repeat, chunk, factors)
    api.disable_perf()

# named function wrapper for the report
def stride_near(dst, src, stride):
    ext.stride(dst, src, stride)

def stride_far(dst, src, stride):
    ext.stride(dst, src, stride)

def do_stride(repeat=1, size=10, stride=1):
    print("init...")
    src = bytearray([(x % 256) for x in range(size)])
    dst = bytearray([0] * size)
    print("work...")
    bar = ProgressBar(total_work=repeat)
    api.enable_perf()
    for x in range(repeat):
        bar.update(x)
        stride_far(dst, src, stride)
        stride_near(dst, src, 1)



    api.disable_perf()
    bar.done()
