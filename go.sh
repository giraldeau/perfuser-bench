#!/bin/sh

lttng destroy -a
rm -rf trace-profile
lttng create -o trace-profile
lttng enable-event -u python:traceback
lttng start
perf record -e instructions -- python3 accuracy.py linuxprofile
lttng stop
lttng destroy -a
pyperf report trace-profile/
