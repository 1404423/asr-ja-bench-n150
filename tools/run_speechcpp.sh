#!/bin/sh
# speech.cpp 0.9.2 (CPU build) in a container capped with --cpus. usage: run_speechcpp.sh MODEL.gguf THREADS CONDITION
# Writes one hypothesis per line (files in sorted order) and prints wall-clock seconds; RTF = (wall - ~6 s start-up) / audio seconds.
M=$1; T=$2; C=$3
s=$(date +%s.%N)
/data/spcpp/speech asr "$M" --threads "$T" /data/$C/*.wav > /data/out_$C.txt 2>/dev/null
e=$(date +%s.%N)
echo "$C $T $s $e"
