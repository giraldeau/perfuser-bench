import argparse
from perfuserBench.accuracy import do_check_linear, do_cprofile, do_linuxprofile, do_stride, profile_simple, stride_ext, stride_py
import sys

def main():
    #
    # FIXME: add proper argument parsing
    #
    print(sys.version_info)
    cmds = ['linear', 'cprofile', 'linuxprofile', 'stride']
    stride_types = { 'ext': stride_ext, 'py': stride_py }
    
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=cmds)
    parser.add_argument('--repeat', action='store', type=int, default=1)
    parser.add_argument('--stride', action='store', type=int, default=1)
    parser.add_argument('--chunk', action='store', type=int, default=128)
    parser.add_argument('--type', action='store', choices=stride_types.keys(), default='ext')
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



