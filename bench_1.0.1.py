"""
scandir-rs benchmark — 三种 API 对比
=====================================

API 区别：
  Count   → 只计数，返回 Statistics（dirs/files/slinks/size 等统计数字）  类比: du -s
  Walk    → 返回 (root, dirs, files) 元组，类似 os.walk                    类比: os.walk
  Scandir → 返回 DirEntry 列表（路径、大小、时间戳、权限等完整元信息）       类比: os.scandir + stat

返回类型：
  Base (默认)  → 基础元数据（路径、大小、时间戳、文件类型）
  Ext          → 扩展元数据（额外包含硬链接数、设备号、inode 等），需要额外系统调用

使用方式：
  Count(dir).collect()                           → Statistics
  Count(dir, return_type=ReturnType.Ext).collect() → Statistics (含 hlinks)

  Walk(dir)                                      → 迭代 (root, dirs, files)
  Walk(dir, return_type=ReturnType.Ext)          → 迭代 (root, dirs, files, symlinks, other, errors)
  Walk(dir).collect()                            → Toc (dirs + files 列表)

  Scandir(dir)                                   → 迭代 DirEntry
  Scandir(dir, return_type=ReturnType.Ext)       → 迭代 DirEntryExt (含 st_mode/atime/ctime/mtime)
  Scandir(dir).collect()                         → List[DirEntry]
  Scandir(dir, return_type=ReturnType.Ext).collect() → List[DirEntryExt]

参考：examples/count.py, examples/walk.py, examples/scandir.py
"""
import os
import time
from scandir_rs import Count, Walk, Scandir, ReturnType

target = 'Z:\\品质部\\内部文件\\MSDS模板\\2022'

# warm up — 预热文件系统缓存
Count(target).collect()

results = []

# ========== Count — 只计数，不存储每条 entry，内存占用最低 ==========
# Count(dir).collect() → Statistics { dirs, files, slinks, size, ... }
t1 = time.time()
s = Count(target).collect()
results.append(('Count.collect', time.time() - t1, s.dirs, s.files, s.size / 1e9))

# Count(dir, return_type=ReturnType.Ext).collect() → Statistics { dirs, files, hlinks, ... }
t1 = time.time()
s = Count(target, return_type=ReturnType.Ext).collect()
results.append(('Count(Ext).collect', time.time() - t1, s.dirs, s.files, s.hlinks))

# ========== Python stdlib 对照组 ==========

# os.walk — Python 内置递归遍历（不获取 stat）
t1 = time.time()
dc = fc = 0
for r, d, f in os.walk(target):
    dc += len(d)
    fc += len(f)
oswalk_time = time.time() - t1
results.append(('os.walk', oswalk_time, dc, fc, 0))

# os.walk + os.stat — Python 内置遍历 + 逐条 stat（模拟 Ext 模式）
t1 = time.time()
dc = fc = 0
for r, d, f in os.walk(target):
    for dn in d:
        try:
            os.stat(os.path.join(r, dn))
            dc += 1
        except OSError:
            pass
    for fn in f:
        try:
            os.stat(os.path.join(r, fn))
            fc += 1
        except OSError:
            pass
results.append(('os.walk(Ext)', time.time() - t1, dc, fc, 0))

# os.scandir 递归 — 生成器 + stat（最佳 Python 原生方案）
t1 = time.time()
dc = fc = 0


def scantree(path):
    try:
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                yield entry
                yield from scantree(entry.path)
            else:
                yield entry
    except (PermissionError, OSError):
        return


for entry in scantree(target):
    try:
        entry.stat()
        if entry.is_dir():
            dc += 1
        else:
            fc += 1
    except OSError:
        pass
results.append(('scantree(os.scandir)', time.time() - t1, dc, fc, 0))

# ========== Walk — 类似 os.walk，返回 (root, dirs, files) 元组 ==========

# Walk(dir) → 迭代 (root, dirs, files)
t1 = time.time()
dc = fc = 0
for root, dirs, files in Walk(target):
    dc += len(dirs)
    fc += len(files)
results.append(('Walk.iter', time.time() - t1, dc, fc, 0))

# Walk(dir, return_type=ReturnType.Ext) → 迭代 (root, dirs, files, symlinks, other, errors)
t1 = time.time()
dc = fc = 0
for root, dirs, files, symlinks, other, errors in Walk(target, return_type=ReturnType.Ext):
    dc += len(dirs)
    fc += len(files)
results.append(('Walk(Ext).iter', time.time() - t1, dc, fc, len(symlinks)))

# Walk(dir).collect() → Toc { dirs: [...], files: [...] }
t1 = time.time()
toc = Walk(target).collect()
results.append(('Walk.collect', time.time() - t1, len(toc.dirs), len(toc.files), 0))

# Walk(dir, return_type=ReturnType.Ext).collect() → Toc (含扩展信息)
t1 = time.time()
toc = Walk(target, return_type=ReturnType.Ext).collect()
results.append(('Walk(Ext).collect', time.time() - t1, len(toc.dirs), len(toc.files), 0))

# ========== Scandir — 返回每条 entry 的完整元信息（DirEntry/DirEntryExt）==========

# Scandir(dir) → 迭代 DirEntry（路径、大小、时间戳、文件类型）
t1 = time.time()
cnt = 0
for entry in Scandir(target):
    cnt += 1
results.append(('Scandir.iter', time.time() - t1, cnt, 0, 0))

# Scandir(dir, return_type=ReturnType.Ext) → 迭代 DirEntryExt（额外含 st_mode/atime/ctime/mtime）
t1 = time.time()
cnt = 0
for entry in Scandir(target, return_type=ReturnType.Ext):
    cnt += 1
results.append(('Scandir(Ext).iter', time.time() - t1, cnt, 0, 0))

# Scandir(dir).collect() → List[DirEntry]（全量收集到内存）
t1 = time.time()
entries = Scandir(target).collect()
results.append(('Scandir.collect', time.time() - t1, len(entries), 0, 0))

# Scandir(dir, return_type=ReturnType.Ext).collect() → List[DirEntryExt]
t1 = time.time()
entries = Scandir(target, return_type=ReturnType.Ext).collect()
results.append(('Scandir(Ext).collect', time.time() - t1, len(entries), 0, 0))

# ========== Print results ==========
print()
print(f'=== scandir-rs benchmark (warm cache) ===')
print(f'| {"Method":<24}| {"Time":<8}| {"vs os.walk":<10}| {"Details":<20}|')
print(f'|{"-" * 24}|{"-" * 9}|{"-" * 11}|{"-" * 21}|')
for name, dt, *args in results:
    speedup = oswalk_time / dt
    detail = ' '.join(str(a) for a in args[:3])
    print(f'| {name:<23}| {dt:.3f}s  | {speedup:.1f}x       | {detail:<19}|')
print()
