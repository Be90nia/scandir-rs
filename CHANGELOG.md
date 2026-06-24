# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.7] - 2026-06-24

### Fixed

- `Walk.collect()` / `Scandir.collect()` no longer panic on `Arc::try_unwrap` when jwalk-meta iterator retains the `process_read_dir` closure (P0 regression introduced in 3.0.5). Replaced with `lock+take`.
- `Walk::has_errors()` returned inverted value (had `!` prefix) — returns correct value now.
- Non-UTF-8 root path and filenames no longer panic; return `Err` / use `to_string_lossy` fallback.
- `Count.__next__` releases GIL via `py.detach` while waiting for worker progress (was busy-waiting).
- `Drop` impl added on pyscandir side to signal worker thread stop on GC, preventing thread leak.
- `methods.rs::check_and_expand_path`: `expanduser().unwrap()` panic on Unix when HOME unset — falls back to original path (H1).
- 4× `recv_timeout` sites split `RecvTimeoutError::Disconnected` vs `::Timeout`; worker panic no longer leaves `busy()` permanently true (H2).
- 3× outer iterator `if let Ok()` silent I/O error drop — converted to explicit `match`, errors forwarded to channel/shared sink (H3).

### Changed

- Stored errors capped at 1000 to bound memory under DoS (M5).
- `walk` dual `std::sync::Mutex` merged to single `parking_lot::Mutex` (no poisoning, lower contention).
- jwalk-meta dependency updated `v1.0.6 → v1.0.7` (`rev a6bbc8fb → 2ef58fec`): fixes max-heap ordering bug + priority-queue Disconnected race window.

### Performance

- `collect()` runs in direct mode (worker thread accumulates in-process via `JoinHandle`), bypassing channel — eliminates SMB burst backpressure regression seen with bounded(4096) in 3.0.5.
- pyscandir binding gains `from_owned` constructors — eliminates deep clones at the Rust/Python boundary.
- `scandir` core: 20+ small optimizations (Vec prealloc, conditional locking, suffix-only allocation, etc.).
- Streaming channel bounded(4096) to limit backlog memory growth.


## [2.9.9] - 2026-05-26

### Fixed

- Reexport method filter_direntry (Rust interface).
- Update Python interface (export ScandirResult, Statistics).

## [2.9.8] - 2026-05-26

### Improved

- Improve workflow and build wheel for older x64 CPUs (no AVX) too.

## [2.9.7] - 2026-05-26

### Improved

- Return error for root DirEntry instead of throwing a panic, which crashes the application.
- Use parking_lot Mutex to reduce locking overhead.

### Changed

- Update dependencies.
- Refactor code. Put together what belongs together.

## [2.9.6] - 2026-02-26

### Changed

- Update dependencies.

## [2.9.5] - 2025-11-24

### Changed

- Update dependencies.

### Fixed

- Fix clippy warnings and a test.

## [2.9.4] - 2025-04-16

### Changed

- Update dependencies.

### Fixed

- Fix compilation error when features are not enabled.

## [2.9.3] - 2025-03-28

### Changed

- Update dependencies.
- Update edition to 2024.

## [2.9.2] - 2025-01-27

### Fixed

- Fix test on Windows.

## [2.9.1] - 2025-01-27

### Fixed

- Fix `follow_links` feature.

## [2.9.0] - 2025-01-27

### Improved

- Update dependencies.
- Add optional argument `follow_links`.

## [2.8.0] - 2024-10-26

### Changed

- ATTENTION: `skip_hidden` is now `false` by default!

### Improved

- Fix tests on Windows.
- Add support for macos-14 on ARM64.

## [2.7.3] - 2024-10-22

### Changed

- ATTENTION: `skip_hidden` is now `false` by default!

### Improved

- Update dependencies.
- Add support for Python 3.13.
- Fix continuous integration on github for Linux and Windows.

## [2.7.2] - 2024-07-09

### Improved

- Update dependencies.

## [2.7.1] - 2024-04-17

### Fixed

- Fixed project description.

## [2.7.0] - 2024-04-15

### Added

- Added optional serialization methods `to_json`, `to_speedy` and `to_bincode` to `Walk`.
  The corresponding features `json`, `speedy` and `bincode` need to be enabled.
- Add `statistics` getter to `Walk`.

### Improved

- Optimized code.
- Update benchmarks.

## [2.6.0] - 2024-04-10

### Added

- Added optional serialization methods `to_json`, `to_speedy` and `to_bincode`.
  The corresponding features `json`, `speedy` and `bincode` need to be enabled.
- Add `statistics` getter to `Scandir`.

### Improved

- Optimized code.
- Update benchmarks.

### Changed

- Change methods `duration`, `finished` and `busy` to getters.

## [2.5.1] - 2024-04-01

### Changed

- Update dependencies.

## [2.5.0] - 2024-03-24

### Added

- Added methods to directly access contents of DirEntry(Ext) in ScandirResult.

## [2.4.2] - 2024-03-24

### Changed

- Update dependencies.
- Fix warnings.

## [2.4.1] - 2024-02-10

### Changed

- Update dependencies.

## [2.4.0] - 2023-05-06

### Changed

- Unify API of different methods (API changes in some methods!).
- Update documentation.

## [2.3.5] - 2023-04-27

### Changed

- Update dependencies

## [2.3.4] - 2023-03-12

### Fixed

- Fix compile problems on Windows.
- Replace all shell build scripts with a single Python build script.

## [2.3.3] - 2023-03-03

### Fixed

- Fix a possible crash in scandir.

## [2.3.2] - 2023-02-13

### Changed

- Update dependencies.

## [2.3.1] - 2023-01-23

### Fixed

- Update jwalk to 0.8.1 to fix Windows issues.

## [2.3.0] - 2023-01-23

### Added

- Add support for path to file as root path.

## [2.2.0] - 2022-11-29

### Added

- Add support for Python 3.11.
- Add option `store` to optionally disable storing results locally.

### Changed

- Change path to generic type to accept different input types.

## [2.1.0] - 2022-11-16

### Added

- Add optional support for speedy serialization.

## [2.0.5] - 2022-10-17

### Changed

- Update supported Python versions.

### Fixed

Fix CVE-2007-4559 in benchmark.py

## [2.0.4] - 2022-05-05

### Changed

- Replace alive AtomicBool by is_finished method of JoinHandle.
  IMPORTANT: At least Rust 1.61 is needed!

## [2.0.3] - 2022-05-05

### Fixed

- Fix build scripts.

## [2.0.2] - 2022-05-04

### Added

- Add methods has_entries, entries_cnt and has_errors.

### Fixed

- Fix root path parsing bug.

## [2.0.1] - 2022-05-03

### Fixed

- Fixed root path problem for Unix platforms.
- Fixed metadata reading problem for some cases.
- Fixed problem with buggy filenames.

## [2.0.0] - 2022-04-24

### Changed

- Complete rewrite.
- Namespaces have changed.
- API has changed.

## [0.9.7] - 2022-02-19

### Changed

- Update dependencies.

## [0.9.6] - 2022-02-19

### Fixed

- Fix a crash when file system doesn't support file creation time.

## [0.9.5] - 2022-01-31

### Added

- Thread safe ts_busy method for each sub-module.
- Thread safe ts_count method for each sub-module.

### Changed

- Update dependencies.
- Add support for Python 3.10.
- Improve example ex_scandir for showing usage of thread safe ts_busy and ts_count methods.

## [0.9.4] - 2021-02-16

### Changed

- Update dependencies.

## [0.9.3] - 2020-07-27

### Added

- Improved pytest test cases.

### Changed

- In benchmark.py:
  - Use Linux kernel 5.5.5 as platform independent a reference.
  - Accept optional parameter for temporary directory base.
  - Benchmark directory C:\Windows on Windows and /usr on other platforms.

### Fixed

- scandir didn't execute.
- Fix performance issue with Walk.
- Correctly return Python exceptions.
- Make build_wheels.sh version independent.
- Make examples platform independent.
- Fix typo in README.md.

## [0.9.2] - 2020-07-26

### Changed

- Provide Windows wheels without debug information.

## [0.9.1] - 2020-07-26

### Changed

- Update to latest versions of Rust and dependencies.

## [0.9.0] - 2020-01-27

### Added

- Add DirEntryExt and DirEntryFull.
- Arguments for directory and file filtering.

### Changed

- Replaced arguments `metadata` and `metadata_ext` with `return_type`.
- Update documentation.

## [0.8.0] - 2020-01-19

### Added

- Add getters to DirEntry.

### Changed

- Update documentation.

### Fixed

- Correctly count hardlinks.
- Update [jwalk](https://github.com/Be90nia/jwalk/tree/jwalk-0.4.1-alpha.1) to get correct extended
  metadata (size and hardlinks).

## [0.7.2] - 2020-01-10

### Changed

- Change default return_type for Walk to RETURN_TYPE_WALK.

## [0.7.1] - 2020-01-10

### Changed

- Update documentation.

## [0.7.0] - 2020-01-09

- First release.
