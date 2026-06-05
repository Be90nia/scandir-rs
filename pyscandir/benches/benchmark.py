# -*- coding: utf-8 -*-
"""
scandir-rs 专业 benchmark — 三种 API 性能对比
==============================================

API 区别：
  Count   → 只计数，返回 Statistics（dirs/files/slinks/size 等统计数字）  类比: du -s
  Walk    → 返回 (root, dirs, files) 元组，类似 os.walk                    类比: os.walk
  Scandir → 返回 DirEntry 列表（路径、大小、时间戳、权限等完整元信息）       类比: os.scandir + stat

返回类型：
  Base (默认)  → 基础元数据（路径、大小、时间戳、文件类型）
  Ext          → 扩展元数据（额外包含硬链接数、设备号、inode 等），需要额外系统调用

使用方式：
  Count(dir).collect()                               → Statistics
  Count(dir, return_type=ReturnType.Ext).collect()   → Statistics (含 hlinks)

  Walk(dir)                                          → 迭代 (root, dirs, files)
  Walk(dir, return_type=ReturnType.Ext)              → 迭代 (root, dirs, files, symlinks, other, errors)
  Walk(dir).collect()                                → Toc (dirs + files 列表)

  Scandir(dir)                                       → 迭代 DirEntry
  Scandir(dir, return_type=ReturnType.Ext)           → 迭代 DirEntryExt (含 st_mode/atime/ctime/mtime)
  Scandir(dir).collect()                             → List[DirEntry]
  Scandir(dir, return_type=ReturnType.Ext).collect() → List[DirEntryExt]

用法：
  python benchmark.py                 # 运行所有测试
  python benchmark.py --count --walk  # 只运行 Count 和 Walk 测试

参考：examples/count.py, examples/walk.py, examples/scandir.py
"""

import os
import sys
import json
import timeit
import platform
from typing import Dict

import psutil
from tabulate import tabulate

import scandir_rs as scandir

GB = 1024 * 1024 * 1024
if os.name == "nt":
    LINUX_DIR = "C:/Workspace/benches/linux-5.9"
    LINUX_KERNEL_ARCHIVE = "C:/Workspace/benches/linux-5.9.tar.gz"
else:
    LINUX_DIR = os.path.expanduser("~/Rust/_Data/benches/linux-5.9")
    LINUX_KERNEL_ARCHIVE = os.path.expanduser("~/Rust/_Data/benches/linux-5.9.tar.gz")


def GetDiskInfo():
    from diskinfo import DiskInfo
    partition = [
        p for p in psutil.disk_partitions(all=False) if p.mountpoint in ("/", "C:\\")
    ][0]
    disks = DiskInfo().get_disk_list()
    for disk in disks:
        if partition.device.startswith(disk.get_path()):
            return (
                disk.get_model(),
                ("SSD" if disk.is_ssd() else "NVME" if disk.is_nvme() else "HDD"),
                partition.fstype,
            )


def CreateTestData():
    tempDir = os.path.dirname(LINUX_DIR)
    if not os.path.exists(tempDir):
        os.makedirs(tempDir)
    if not os.path.exists(LINUX_KERNEL_ARCHIVE):
        import requests
        proxies = None
        userDnsDomain = os.environ.get("USERDNSDOMAIN")
        if userDnsDomain and userDnsDomain.endswith("SCH.COM"):
            proxies = {
                "http": "http://127.0.0.1:3129",
                "https": "http://127.0.0.1:3129",
            }
        r = requests.get(
            "https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.9.tar.gz",
            stream=True,
            proxies=proxies,
        )
        print("Downloading linux-5.9.tar.gz...")
        with open(LINUX_KERNEL_ARCHIVE, "wb") as F:
            for chunk in r.iter_content(chunk_size=4096):
                F.write(chunk)
    if not os.path.exists(LINUX_DIR):
        print("Extracting linux-5.9.tar.gz...")
        os.makedirs(LINUX_DIR)
        # cmdLine = f"tar xzf {LINUX_KERNEL_ARCHIVE} -C {LINUX_DIR}"
        cmdLine = f"7z x {LINUX_KERNEL_ARCHIVE} -so | 7z x -aoa -si -ttar -o{LINUX_DIR}"
        print(f"Running: {cmdLine}")
        os.system(cmdLine)
    return tempDir


def RunCountBenchmarks(dirName: str) -> Dict[str, float]:
    """Count API — 只计数不存储 entry，内存占用最低，返回 Statistics"""
    print(f"Running Count benchmarks in directory: {dirName}")
    # Count(dir).collect() → Statistics { dirs, files, slinks, size, ... }
    print(scandir.Count(dirName).collect())
    # Count(dir, return_type=ReturnType.Ext).collect() → Statistics { ..., hlinks, devices, pipes }
    stats = json.loads(scandir.Count(dirName, return_type=scandir.ReturnType.Ext).collect().to_json())
    print(stats)

    # Count.collect (Base) — 基础统计
    dtScandirCountCollect = timeit.timeit(
        f"""
scandir.Count('{dirName}').collect()
    """,
        setup="import scandir_rs as scandir",
        number=3,
    ) / 3
    print(f"scandir.Count (collect): {dtScandirCountCollect}")

    # Count.collect (Ext) — 扩展统计（含硬链接数等）
    dtScandirCountCollectExt = timeit.timeit(
        f"""
scandir.Count('{dirName}', return_type=scandir.ReturnType.Ext).collect()
    """,
        setup="import scandir_rs as scandir",
        number=3,
    ) / 3
    print(f"scandir.Count(Ext) (collect): {dtScandirCountCollectExt}")
    return {
        "stats": stats,
        "dtScandirCountCollect": dtScandirCountCollect / 3,
        "Count.collect(Ext)": dtScandirCountCollectExt / 3}


def RunWalkBenchmarks(dirName: str) -> Dict[str, float]:
    """Walk API — 类似 os.walk，返回 (root, dirs, files) 元组"""
    print(f"Running Walk benchmarks in directory: {dirName}")

    # Python 对照组：os.walk（不获取 stat）
    dtOsWalk = timeit.timeit(
        f"""
for root, dirs, files in os.walk('{dirName}'):
    pass
    """,
        setup="import os",
        number=3,
    ) / 3
    print(f"os.walk {dtOsWalk}")

    # Python 对照组：os.walk + os.stat（模拟 Ext 模式）
    dtOsWalkExt = timeit.timeit(
        f"""
dirStats = dict()
fileStats = dict()
for root, dirs, files in os.walk('{dirName}'):
    for dirName in dirs:
        pathName = root + '/' + dirName
        try:
            dirStats[pathName] = os.stat(pathName)
        except:
            pass
    for fileName in files:
        pathName = root + '/' + fileName
        try:
            fileStats[pathName] = os.stat(pathName)
        except:
            pass
    """,
        setup="import os",
        number=3,
    ) / 3
    print(f"os.walk(Ext) {dtOsWalkExt}")

    # Walk.iter (Base) — Walk(dir) → 迭代 (root, dirs, files)
    dtScandirWalkIter = timeit.timeit(
        f"""
for result in scandir.Walk('{dirName}'):
    pass
    """,
        setup="import scandir_rs as scandir",
        number=3,
    ) / 3
    print(f"scandir.Walk (iter): {dtScandirWalkIter}")

    # Walk.iter (Ext) — Walk(dir, return_type=ReturnType.Ext) → 迭代 (root, dirs, files, symlinks, other, errors)
    dtScandirWalkIterExt = timeit.timeit(
        f"""
for result in scandir.Walk('{dirName}', return_type=scandir.ReturnType.Ext):
    pass
    """,
        setup="import scandir_rs as scandir",
        number=3,
    ) / 3
    print(f"scandir.Walk(Ext) (iter): {dtScandirWalkIterExt}")

    # Walk.collect (Base) — Walk(dir).collect() → Toc { dirs: [...], files: [...] }
    dtScandirWalkCollect = timeit.timeit(
        f"""
toc = scandir.Walk('{dirName}').collect()
    """,
        setup="import scandir_rs as scandir",
        number=3,
    ) / 3
    print(f"scandir.Walk (collect): {dtScandirWalkCollect}")

    # Walk.collect (Ext) — Walk(dir, return_type=ReturnType.Ext).collect() → Toc (含扩展信息)
    dtScandirWalkCollectExt = timeit.timeit(
        f"""
toc = scandir.Walk('{dirName}', return_type=scandir.ReturnType.Ext).collect()
    """,
        setup="import scandir_rs as scandir",
        number=3,
    ) / 3
    print(f"scandir.Walk(Ext) (collect): {dtScandirWalkCollectExt}")
    return {
        "os.walk": dtOsWalk,
        "os.walk(Ext)": dtOsWalkExt,
        "Walk.iter": dtScandirWalkIter,
        "Walk.iter(Ext)": dtScandirWalkIterExt,
        "Walk.collect": dtScandirWalkCollect,
        "Walk.collect(Ext)": dtScandirWalkCollectExt}


def RunScandirBenchmarks(dirName: str) -> Dict[str, float]:
    """Scandir API — 返回每条 entry 的完整元信息（DirEntry/DirEntryExt）"""
    print(f"Running Scandir benchmarks in directory: {dirName}")

    # Python 对照组：os.scandir 递归 + stat（最佳 Python 原生方案）
    dtOsScandir = timeit.timeit(
        f"""
def scantree(path):
    try:
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                yield entry
                yield from scantree(entry.path)
            else:
                yield entry
    except:
        return

dirs = 0
files = 0
symlinks = 0
size = 0
for entry in scantree(os.path.expanduser('{dirName}')):
    try:
        st = entry.stat()
    except:
        continue
    if entry.is_dir():
        dirs += 1
    elif entry.is_file():
        files += 1
    elif entry.is_symlink():
        symlinks += 1
    size += st.st_size
    """,
        setup="import os",
        number=3,
    ) / 3
    print(f"scantree (os.scandir): {dtOsScandir}")

    # Scandir.iter (Base) — Scandir(dir) → 迭代 DirEntry（路径、大小、时间戳、文件类型）
    dtScandirScandirIter = timeit.timeit(
        f"""
for result in scandir.Scandir('{dirName}'):
    pass
    """,
        setup="import scandir_rs as scandir",
        number=3,
    ) / 3
    print(f"scandir.Scandir (iter): {dtScandirScandirIter}")

    # Scandir.iter (Ext) — Scandir(dir, return_type=ReturnType.Ext) → 迭代 DirEntryExt
    dtScandirScandirIterExt = timeit.timeit(
        f"""
for result in scandir.Scandir('{dirName}', return_type=scandir.ReturnType.Ext):
    pass
    """,
        setup="import scandir_rs as scandir",
        number=3,
    ) / 3
    print(f"scandir.Scandir(Ext) (iter): {dtScandirScandirIterExt}")

    # Scandir.collect (Base) — Scandir(dir).collect() → List[DirEntry]（全量收集到内存）
    dtScandirScandirCollect = timeit.timeit(
        f"""
entries = scandir.Scandir('{dirName}').collect()
    """,
        setup="import scandir_rs as scandir",
        number=3,
    ) / 3
    print(f"scandir.Scandir (collect): {dtScandirScandirCollect}")

    # Scandir.collect (Ext) — Scandir(dir, return_type=ReturnType.Ext).collect() → List[DirEntryExt]
    dtScandirScandirCollectExt = timeit.timeit(
        f"""
entries = scandir.Scandir('{dirName}', return_type=scandir.ReturnType.Ext).collect()
    """,
        setup="import scandir_rs as scandir",
        number=3,
    ) / 3
    print(f"scandir.Scandir(Ext) (collect): {dtScandirScandirCollectExt}")
    return {
        "scantree (os.scandir)": dtOsScandir,
        "Scandir.iter": dtScandirScandirIter,
        "Scandir.iter(Ext)": dtScandirScandirIterExt,
        "Scandir.collect": dtScandirScandirCollect,
        "Scandir.collect(Ext)": dtScandirScandirCollectExt}


def BenchmarkDir(path: str, bCount: bool, bWalk: bool, bScandir: bool):
    print()
    pyVersion = sys.version.split(" ")[0]
    stats = {}
    tableCount = []
    tableWalk = []
    tableScandir = []
    if bCount:
        stats.update(RunCountBenchmarks(path))
        tableCount = [
            [stats["dtScandirCountCollect"], "Count.collect"],
            [stats["Count.collect(Ext)"], "Count(Ext).collect"]]
    if bWalk:
        stats.update(RunWalkBenchmarks(path))
        tableWalk = [
            [stats["os.walk"], f"os.walk (Python {pyVersion})"],
            [stats["Walk.iter"], "Walk.iter"],
            [stats["Walk.collect"], "Walk.collect"],
            [stats["os.walk(Ext)"], f"os.walk(Ext) (Python {pyVersion})"],
            [stats["Walk.iter(Ext)"], "Walk(Ext).iter"],
            [stats["Walk.collect(Ext)"], "Walk(Ext).collect"]]
    if bScandir:
        stats.update(RunScandirBenchmarks(path))
        tableScandir = [
            [stats["scantree (os.scandir)"], f"scantree (os.scandir, Python {pyVersion})"],
            [stats["Scandir.iter"], "Scandir.iter"],
            [stats["Scandir.collect"], "Scandir.collect"],
            [stats["Scandir.iter(Ext)"], "Scandir(Ext).iter"],
            [stats["Scandir.collect(Ext)"], "Scandir(Ext).collect"]]
    uname = platform.uname()
    print(f"\n{uname.system} {uname.machine} (kernel={uname.release})")
    print("Physical cores:", psutil.cpu_count(logical=False))
    print("Total cores:", psutil.cpu_count(logical=True))
    cpufreq = psutil.cpu_freq()
    print(f"Max Frequency: {cpufreq.max:.2f}Mhz")
    if os.name == 'posix:':
        disk = GetDiskInfo()
        print(f"Disk: {disk[0]} ({disk[1]}, {disk[2]})")
    print()
    s = stats["stats"]
    print(f"Directory {path} with:")
    print(f"  {s['dirs']} directories")
    print(f"  {s['files']} files")
    print(f"  {s['slinks']} symlinks")
    print(f"  {s['hlinks']} hardlinks")
    print(f"  {s['devices']} devices")
    print(f"  {s['pipes']} pipes")
    print(f"  {s['size'] / GB:.2f}GB size and {s['usage'] / GB:.2f}GB usage on disk")
    print()
    if tableCount:
        print(tabulate(tableCount, headers=["Time [s]", "Method"], tablefmt="github"))
        print()
    if tableWalk:
        print(tabulate(tableWalk, headers=["Time [s]", "Method"], tablefmt="github"))
        print()
        print(f"Walk.iter **~{stats["os.walk"] / stats["Walk.iter"]:.1f} times faster** than os.walk.")
        print(f"Walk(Ext).iter **~{stats["os.walk(Ext)"] / stats["Walk.iter(Ext)"]:.1f} times faster** than os.walk(Ext).")
        print()
    if tableScandir:
        print(tabulate(tableScandir, headers=["Time [s]", "Method"], tablefmt="github"))
        print()
        print(
            f"Scandir.iter **~{stats["scantree (os.scandir)"] / stats["Scandir.iter"]:.1f} times faster** than scantree(os.scandir)."
        )
        print(
            f"Scandir(Ext).iter **~{stats["scantree (os.scandir)"] / stats["Scandir.iter(Ext)"]:.1f} times faster** than scantree(os.scandir)."
        )
    with open(f"benchmark_results_{os.name}_{os.path.basename(path)}.json", "w") as F:
        F.write(json.dumps(stats))


if __name__ == "__main__":
    tempDir = CreateTestData()
    dirName = "C:/Windows" if os.name == "nt" else "/usr"
    if " --" in str(sys.argv):
        bCount = "--count" in sys.argv
        bWalk = "--walk" in sys.argv
        bScandir = "--scandir" in sys.argv
    else:
        bCount = True
        bWalk = True
        bScandir = True
    BenchmarkDir(tempDir, bCount, bWalk, bScandir)
    BenchmarkDir(dirName, bCount, bWalk, bScandir)
