#!/usr/bin/env python3
"""Synthesize original light transition effects, not a music track. Standard library only."""
import argparse
import math
import random
import struct
import wave
from pathlib import Path

RATE=48000


def write_wav(path, samples):
    with wave.open(str(path),'wb') as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(RATE)
        out.writeframes(b''.join(struct.pack('<h',int(max(-1,min(1,x))*32767)) for x in samples))


def make(out_dir):
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    rng=random.Random(187)
    whoosh=[];prev=0.0;duration=.24
    for i in range(int(RATE*duration)):
        t=i/RATE;u=t/duration
        noise=rng.uniform(-1,1)
        coefficient=.025+.22*math.sin(math.pi*u)**2
        prev += coefficient*(noise-prev)
        whoosh.append(prev*math.sin(math.pi*u)**2*.42)
    pop=[];duration=.075
    for i in range(int(RATE*duration)):
        t=i/RATE
        phase=2*math.pi*(320*t+210*.018*(1-math.exp(-t/.018)))
        envelope=min(t/.002,1)*math.exp(-t/.014)*min((duration-t)/.01,1)
        pop.append(.22*envelope*math.sin(phase))
    write_wav(out/'whoosh.wav',whoosh)
    write_wav(out/'pop.wav',pop)
    print('Created whoosh.wav and pop.wav; mix below speech, not on every caption.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out-dir',required=True)
    make(p.parse_args().out_dir)
