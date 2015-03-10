import argparse
from perfuserBench.accuracy import *
import sys

def main():
    #
    # FIXME: add proper argument parsing
    #
    print(sys.version_info)
    cmds = ['linear', 'cprofile', 'linuxprofile', 'stride']

    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=cmds)
    parser.add_argument('--repeat', action='store', type=int, default=1)
    parser.add_argument('--stride', action='store', type=int, default=1)
    parser.add_argument('--chunk', action='store', type=int, default=128)
    args = parser.parse_args()


    if args.command == 'linear':
        do_check_linear(args)

    if args.command == 'cprofile':
        do_cprofile(args.repeat, args.chunk, profile_simple)
    if args.command == 'linuxprofile':
        do_linuxprofile(args.repeat, args.chunk, profile_simple)
    if args.command == 'stride':
        do_stride(args.repeat, args.chunk, args.stride)



