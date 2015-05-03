import argparse
from perfuserBench.accuracy import do_check_linear, do_cprofile, do_linuxprofile, do_stride, profile_simple, stride_ext, stride_py, \
    do_experiment
from perfuserBench.microbench import do_traceback_overhead
from linuxProfile.launch import ProfileRunnerPerfSampling, ProfileRunner
from linuxProfile.api import sampling
import sys
import time
import statistics

def main():
    #
    # FIXME: add proper argument parsing
    #
    print(sys.version_info)
    cmds = ['linear', 'cprofile', 'linuxprofile', 'stride', 'traceback']
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
    args = parser.parse_args()


    if args.command == 'linear':
        do_check_linear(args)
    if args.command == 'cprofile':
        do_cprofile(args.repeat, args.chunk, profile_simple)
    if args.command == 'linuxprofile':
        prof = None
        if not args.baseline:
            prof = ProfileRunnerPerfSampling(args.event, args.period)
        if prof:
            prof.enable()
        items = [0.0] * args.repeat
        do_experiment(args.repeat, args.chunk, profile_simple)
        h1 = sampling.hits()
        for i in range(args.repeat):
            t1 = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
            do_experiment(1, args.chunk, profile_simple)
            t2 = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
            items[i] = (t2 - t1) * 1000000
        if prof:
            prof.disable()
        h2 = sampling.hits()
        samples = h2 - h1
        xsum = sum(items)
        xbar = statistics.mean(items)
        sd = 0.0
        if len(items) > 1:
            sd = statistics.stdev(items, xbar)
        print("us samples=%d n=%d sum=%0.f mean=%.0f sd=%.0f" % (samples, len(items), xsum, xbar, sd))
        with open("linuxprofile.csv", "a") as f:
            f.write("%s;%d;%d;%0.f;%0.f;\n" % (args.baseline, args.period, samples, xbar, sd))
    if args.command == 'stride':
        t = stride_types.get(args.type)
        do_stride(args.repeat, args.chunk, args.stride, t)
    if args.command == 'traceback':
        do_traceback_overhead()



