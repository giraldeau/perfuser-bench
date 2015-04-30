#!/usr/bin/env python3

from linuxProfile import api, utils
import traceback
import time
import sys
import itertools
import pandas as pd
import numpy as np
from scipy import stats

def dict_product(params):
    prod = itertools.product(*params.values())
    for item in prod:
        d = {}
        for k, v in zip(params.keys(), item):
            d[k] = v
        yield d

class BenchEmpty(object):
    def before(self, param):
        pass
    def repeat(self, param):
        pass
    def after(self, param):
        pass

class BenchRunner(object):
    def __init__(self):
        self.data = {} # dict where keys are columns, and values are list of data
    def benchmark(self, repeat, bench, params):
        _id = 0
        for k in params.keys():
            self.data[k] = []
        self.data['time'] = []
        for param in dict_product(params):
            for x in range(repeat):
                bench.before(param)
                t1 = utils.clock_gettime_timespec().float()
                bench.repeat(param)
                t2 = utils.clock_gettime_timespec().float()
                bench.after(param)
                _id += 1
                if (x == 0):
                    continue
                for k in params.keys():
                    self.data[k].append(param[k])
                self.data['time'].append(t2 - t1)
                
    def get_data(self):
        return self.data

class TracebackStub(object):
    def open(self):
        pass
    def do_traceback(self):
        pass
    def close(self):
        pass
    def __repr__(self):
        return "stub"

class TracebackBuiltin(object):
    def open(self):
        self.file = open("traceback.out", "a")
    def do_traceback(self):
        traceback.print_stack(file=self.file)
    def close(self):
        self.file.close()
    def __repr__(self):
        return "builtin"

class TracebackSimple(object):
    def open(self):
        pass
    def do_traceback(self):
        api.traceback()
    def close(self):
        pass
    def __repr__(self):
        return "ust"

class TracebackUnwind(object):
    def open(self):
        pass
    def do_traceback(self):
        api.unwind()
    def close(self):
        pass
    def __repr__(self):
        return "ust"

class TracebackFull(object):
    def open(self):
        pass
    def do_traceback(self):
        api.traceback_full()
    def close(self):
        pass
    def __repr__(self):
        return "ust"

class BenchTraceback(BenchEmpty):
    def __init__(self):
        self.tb_type = {
                        'unwind': TracebackUnwind(),
                        'traceback': TracebackSimple(),
                        'full': TracebackFull(),
                        'builtin': TracebackBuiltin(),
                        'stub': TracebackStub(),
                        }
    def before(self, param):
        self.tb = self.tb_type[param['traceback']]
        self.tb.open()
    def repeat(self, param):
        self.foo(param['depth'])
    def after(self, param):
        self.tb.close()
    def foo(self, depth):
        if (depth > 0):
            depth -= 1
            self.foo(depth)
        else:
            self.tb.do_traceback()

def dump_html(df, name):
    with open(name + ".html", "w") as f:
        f.write(df.to_html())

from pandas.core.format import set_eng_float_format

def do_traceback_overhead():
    params = {
              "traceback": ["stub", "builtin", "traceback"],
               "depth": range(0, 100, 10),
             }
    set_eng_float_format()
    repeat = 1000
    runner = BenchRunner()
    runner.benchmark(repeat, BenchTraceback(), params)
    data = runner.get_data()
    df = pd.DataFrame(data)
    df = df[['traceback', 'depth', 'time']]
    grp = df.groupby(list(params.keys()))
    results = grp['time'].aggregate([np.mean, np.std])
    #dump_html(df, "data")
    #dump_html(results, "results")
    print(results.reset_index())
    results.to_csv('traceback.csv')
    df.to_csv('traceback_data.csv')
    #df[df['traceback'] == 'ust' and df['depth'] == 100]
    #for group in grp.groups:
        #x = grp.get_group(group)
        #print(group)
        #print(x.head())

    #v1 = df.loc[(df['traceback'] == 'stub') & (df['depth'] == depth), "time"].values
    #v2 = df.loc[(df['traceback'] == 'ust') & (df['depth'] == depth), "time"].values
    #v3 = df.loc[(df['traceback'] == 'builtin') & (df['depth'] == depth), "time"].values
    #print(v1)
    #print(v2)
    #print(v3)
    #ttest1 = stats.ttest_ind(v1, v2)
    #ttest2 = stats.ttest_ind(v1, v3)
    #ttest3 = stats.ttest_ind(v2, v3)
    #print("H0: stub == ust     " + repr(ttest1))
    #print("H0: stub == builtin " + repr(ttest2))
    #print("H0: ust  == builtin " + repr(ttest3))
