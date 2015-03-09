import argparse
from perfuserBench.accuracy import *
import sys

def main():
    print(sys.version_info)
    cmds = ['linear', 'cprofile', 'linuxprofile', 'crunch']

    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=cmds)
    args = parser.parse_args()

    if args.command == 'linear':
        check_linear(work)

    chunk = 128
    repeat = 10000
    factors = [(f_00, 50), (f_01, 20), (f_02, 15), (f_03, 5), (f_04, 5),
               (f_05, 1), (f_06, 1), (f_07, 1), (f_08, 1), (f_09, 1), ]

    if args.command == 'cprofile':
        do_cprofile(repeat, factors, chunk)
    if args.command == 'linuxprofile':
        do_linuxprofile(repeat, factors, chunk)
    if args.command == 'crunch':
        do_stride()



