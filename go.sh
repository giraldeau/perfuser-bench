#!/bin/sh -x



run_stride() {
	chunk=$1
	repeat=$2
	stride_type=$3
	lttng destroy -a
	rm -rf trace-profile
	lttng create -o trace-profile
	lttng enable-event -u python:traceback
	lttng start
	#perf record -e instructions -- perfuserBench linuxperf
	perf record -e cache-misses -- perfuserBench stride --chunk $chunk --repeat $repeat --stride 1000 --type=$stride_type
	lttng stop
	lttng destroy -a
	pyperf report trace-profile/
}

#run_stride 10000000 1000
#run_stride 1000000000 1

# chunk size too small, fits into L1-cache
#run_stride 10000 10000

run_stride 10000000 10 py
run_stride 10000000 10 ext

