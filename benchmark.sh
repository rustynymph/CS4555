#! /bin/bash

if [ $# -lt 2 ]; then
	echo "Usage: benchmark.sh filename iterations"
	exit 1
fi

filename=$1
iterations=$2

counter=0

python NodeCounter.py $filename
for i in $(seq 1 $iterations); do
	sleep 1
	time python compile.py $filename;
done
