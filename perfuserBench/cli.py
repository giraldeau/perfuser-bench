import argparse
from perfuserBench.accuracy import do_check_linear, do_cprofile, do_linuxprofile, do_stride, profile_simple, stride_ext, stride_py, \
    do_experiment
from perfuserBench.microbench import do_traceback_overhead
from linuxProfile.launch import ProfileRunnerPerfSampling, ProfileRunner
from linuxProfile.api import sampling
import sys
import time
import statistics
import itertools

def mkstats(items):
    xsum = sum(items)
    xbar = statistics.mean(items)
    sd = 0.0
    if len(items) > 1:
        sd = statistics.stdev(items, xbar)
    return {"elapsed": xsum, "mean": xbar, "stdev": sd }

def do_workload(items, repeat, chunk):
    for i in range(repeat):
        t1 = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
        do_experiment(1, chunk, profile_simple)
        t2 = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
        items[i] = (t2 - t1) * 1000000000

def make_results(event, period, repeat, chunk, monitor, output, items, baseline):
    print("experiment {}".format({"event": event, "period": period, "monitor": monitor}))

    prof = ProfileRunnerPerfSampling(event, period, monitor)
    prof.enable()
    do_workload(items, repeat, chunk)
    h1 = sampling.hits()
    do_workload(items, repeat, chunk)
    prof.disable()
    s = mkstats(items)

    h2 = sampling.hits()
    n = h2 - h1

    overhead_abs = s["elapsed"] - baseline["elapsed"]
    overhead_perc = overhead_abs / baseline["elapsed"] * 100
    ev_cost = overhead_abs
    if (n > 0):
        ev_cost = overhead_abs / n

    with open(output, "a") as f:
        f.write("%s;%d;%s;%d;%.0f;%.0f;%.0f;%.0f;%.3f;%.3f\n" %
                (event, period, monitor, n, s["elapsed"], s["mean"], s["stdev"], overhead_abs, overhead_perc, ev_cost))

def do_paper3_results(repeat, chunk, output):
        items = [0.0] * repeat

        # header
        cols = [ "event", "period", "monitor", "samples", "elapsed", "mean", "stdev", "overhead_abs", "overhead_perc", "evcost" ]
        with open(output, "w+") as f:
            f.write(";".join(cols) + "\n")

        # warm-up
        do_workload(items, repeat, chunk)

        # baseline measure
        do_workload(items, repeat, chunk)
        baseline = mkstats(items)

        print("baseline: {}".format(baseline))

        r = []
        for p in [10000, 100000, 1000000, 10000000]:
            r = r + [(x + 1) * p for x in range(10)]

        for period in [10000, 100000, 1000000, 10000000]:
            for monitor in [ "unwind", "traceback", "full" ]:
                # for event in [ "instructions", "cycles" ]:
                for event in [ "cycles" ]:
                    make_results(event, period, repeat, chunk, monitor, output, items, baseline)

# copied from cpython ccprofile.py
def task_pidigits():
    """Pi calculation (Python)"""
    _map = map
    _count = itertools.count
    _islice = itertools.islice

    def calc_ndigits(n):
        # From http://shootout.alioth.debian.org/
        def gen_x():
            return _map(lambda k: (k, 4 * k + 2, 0, 2 * k + 1), _count(1))

        def compose(a, b):
            aq, ar, as_, at = a
            bq, br, bs, bt = b
            return (aq * bq,
                    aq * br + ar * bt,
                    as_ * bq + at * bs,
                    as_ * br + at * bt)

        def extract(z, j):
            q, r, s, t = z
            return (q * j + r) // (s * j + t)

        def pi_digits():
            z = (1, 0, 0, 1)
            x = gen_x()
            while 1:
                y = extract(z, 3)
                while y != extract(z, 4):
                    z = compose(z, next(x))
                    y = extract(z, 3)
                z = compose((10, -10 * y, 0, 1), z)
                yield y

        return list(_islice(pi_digits(), n))

    return calc_ndigits, (50,)

tasks = [task_pidigits]

def setprofile_load(task, args, items, repeat):
    for i in range(repeat):
        t1 = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
        for _ in range(repeat):
            task(*args)
        t2 = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
        items[i] = (t2 - t1) * 1000000000 / repeat

def do_setprofile(repeat, chunk):
    items = [0.0] * repeat
    with open("setprofile.csv", "w") as f:
        f.write("test;x1;s1;x2,s2\n")
        for t in tasks:
            print(t.__doc__)
            # warm-up
            fn, args = t()
            setprofile_load(fn, args, items, repeat)

            # baseline
            setprofile_load(fn, args, items, repeat)
            baseline = mkstats(items)

            # setprofile
            enable_perf()
            setprofile_load(fn, args, items, repeat)
            disable_perf()
            inst = mkstats(items)

            print("baseline {}".format(baseline))
            print("instrum. {}".format(inst))
            f.write("%s;%.0f;%.0f;%.0f;%.0f;\n" % (t.__doc__,
                                        baseline['mean'], baseline['stdev'],
                                        inst['mean'], inst['stdev']))


def main():
    #
    # FIXME: add proper argument parsing
    #
    print(sys.version_info)
    cmds = ['linear', 'cprofile', 'linuxprofile', 'stride', 'traceback', 'results',
            'setprofile', 'setprofile_perf']
    stride_types = { 'ext': stride_ext, 'py': stride_py }

    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=cmds)
    parser.add_argument('--repeat', action='store', type=int, default=1)
    parser.add_argument('--stride', action='store', type=int, default=1)
    parser.add_argument('--chunk', action='store', type=int, default=128)
    parser.add_argument('--event', '-e', action='store', type=str, default='cycles', choices=ProfileRunnerPerfSampling.evdefs.keys())
    parser.add_argument('--period', '-p', action='store', type=int, default=10000)
    parser.add_argument('--baseline', action='store_true', default=False)
    parser.add_argument('--type', action='store', choices=stride_types.keys(), default='ext')
    parser.add_argument('--output', action='store', default='linuxprofile.csv')
    args = parser.parse_args()

    if args.command == 'linear':
        do_check_linear(args)
    if args.command == 'cprofile':
        do_cprofile(args.repeat, args.chunk, profile_simple)
    if args.command == 'linuxprofile':
        do_linuxprofile(args.repeat, args.chunk, profile_simple)
    if args.command == 'stride':
        t = stride_types.get(args.type)
        do_stride(args.repeat, args.chunk, args.stride, t)
    if args.command == 'traceback':
        do_traceback_overhead()
    if args.command == 'results':
        do_paper3_results(args.repeat, args.chunk, args.output)
    if args.command == 'setprofile':
        do_setprofile(args.repeat, args.chunk)
    if args.command == 'setprofile_perf':
        items = [0.0] * args.repeat
        fn, opts = task_pidigits()
        if not args.baseline:
            enable_perf()
        setprofile_load(fn, opts, items, args.repeat)
        if not args.baseline:
            disable_perf()



