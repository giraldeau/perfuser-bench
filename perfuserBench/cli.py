import argparse
from perfuserBench.accuracy import do_check_linear, do_cprofile, do_linuxprofile, do_stride, profile_simple, stride_ext, stride_py, \
    do_experiment
from perfuserBench.microbench import do_traceback_overhead
from linuxProfile.launch import ProfileRunnerPerfSampling, ProfileRunner
from linuxProfile.api import sampling, enable_perf, disable_perf
import sys
import time
import statistics


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
        items[i] = (t2 - t1) * 1000000

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

    overhead_abs = s["mean"] - baseline["mean"]
    overhead_perc = overhead_abs / baseline["mean"] * 100
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
        noinst = mkstats(items)

        enable_perf()
        do_workload(items, repeat, chunk)
        disable_perf()
        baseline = mkstats(items)

        oh = (baseline['mean'] - noinst['mean']) / noinst['mean'] * 100
        print('noinst = %.3f baseline = %.3f overhead = %.3f\n' % (noinst['mean'], baseline['mean'], oh))

        for period in [10000, 100000, 1000000, 10000000]:
            for monitor in [ "unwind", "traceback", "full" ]:
                for event in [ "instructions", "cycles" ]:
                    make_results(event, period, repeat, chunk, monitor, output, items, baseline)

def main():
    #
    # FIXME: add proper argument parsing
    #
    print(sys.version_info)
    cmds = ['linear', 'cprofile', 'linuxprofile', 'stride', 'traceback', 'results']
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



