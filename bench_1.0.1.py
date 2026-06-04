import os
import time
from scandir_rs import Count, Walk, Scandir, ReturnType

import statistics

import sys

target = 'D:\\'

# warm up
Count(target).collect()

results = []

# Count.collect
t1 = time.time()
s = Count(target).collect()
results.append(('Count.collect', time.time() - t1, s.dirs, s.files, s.size/1e9))

# os.walk
t1 = time.time()
dc = fc = 0
for r, d, f in os.walk(target):
    dc += len(d)
    fc += len(f)
results.append(('os.walk', time.time() - t1, dc, fc, 0))
# Walk.iter
t1 = time.time()
cnt = sum(1 for _ in Walk(target))
results.append(('Walk.iter', time.time() - t1, cnt, 0, 0))
# Walk.collect
t1 = time.time()
toc = Walk(target).collect()
results.append(('Walk.collect', time.time() - t1, len(toc.dirs), len(toc.files), 0))
# Scandir.collect
t1 = time.time()
entries = Scandir(target).collect()
results.append(('Scandir.collect', time.time() - t1, len(entries), 0, 0))
# Count(Ext)
t1 = time.time()
s = Count(target, return_type=ReturnType.Ext).collect()
results.append(('Count(Ext)', time.time() - t1, s.dirs, s.files, s.hlinks))

# Print results
oswalk_time = [r[2] for r in results if r[0] == 'os.walk'][0]
print()
print('=== jwalk-meta 1.0.1 (warm cache) ===')
print(f'| Method               | Time    | vs os.walk | Details            |')
print(f'|---------------------|---------|-----------|------------------|')
for name, dt, *args in results:
    speedup = oswalk_time / dt
    detail = ' '.join(str(a) for a in args[:3])
    print(f'| {name:<22}| {dt:.3f}s  | {speedup:.1f}x     | {detail:<16}|')
print()