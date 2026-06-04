# Graph Report - .  (2026-06-02)

## Corpus Check
- Corpus is ~47,394 words - fits in a single context window. You may not need a graph.

## Summary
- 432 nodes · 569 edges · 47 communities (40 shown, 7 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 51 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Scandir Worker|Scandir Worker]]
- [[_COMMUNITY_Walk Worker|Walk Worker]]
- [[_COMMUNITY_Count Worker|Count Worker]]
- [[_COMMUNITY_API Docs & Benchmarks|API Docs & Benchmarks]]
- [[_COMMUNITY_Scandir Data Types|Scandir Data Types]]
- [[_COMMUNITY_DirEntryExt|DirEntryExt]]
- [[_COMMUNITY_Statistics Type|Statistics Type]]
- [[_COMMUNITY_Python Tests|Python Tests]]
- [[_COMMUNITY_Toc Type|Toc Type]]
- [[_COMMUNITY_Rust Tests|Rust Tests]]
- [[_COMMUNITY_DirEntry|DirEntry]]
- [[_COMMUNITY_FastProperties GUI|FastProperties GUI]]
- [[_COMMUNITY_Rust Benchmarks & Docs|Rust Benchmarks & Docs]]
- [[_COMMUNITY_Python Benchmark Runner|Python Benchmark Runner]]
- [[_COMMUNITY_Common Filter Methods|Common Filter Methods]]
- [[_COMMUNITY_Scandir Bench|Scandir Bench]]
- [[_COMMUNITY_Walk Bench|Walk Bench]]
- [[_COMMUNITY_Build Wheels|Build Wheels]]
- [[_COMMUNITY_Common Definitions|Common Definitions]]
- [[_COMMUNITY_Count Bench|Count Bench]]
- [[_COMMUNITY_Walk Data Types|Walk Data Types]]
- [[_COMMUNITY_Options|Options]]

## God Nodes (most connected - your core abstractions)
1. `Scandir` - 45 edges
2. `Walk` - 42 edges
3. `Count` - 37 edges
4. `DirEntryExt` - 30 edges
5. `Statistics` - 23 edges
6. `DirEntry` - 21 edges
7. `Toc` - 19 edges
8. `ScandirResult` - 17 edges
9. `create_temp_file_tree()` - 15 edges
10. `cleanup()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Create Charts Tool` --references--> `Rust Count Benchmarks`  [INFERRED]
  tools/create_charts.py → scandir/doc/benchmarks.md
- `Create Charts Tool` --references--> `Rust Walk Benchmarks`  [INFERRED]
  tools/create_charts.py → scandir/doc/benchmarks.md
- `Create Charts Tool` --references--> `Rust Scandir Benchmarks`  [INFERRED]
  tools/create_charts.py → scandir/doc/benchmarks.md
- `Python Module scandir_rs` --rationale_for--> `GIL Release for Python Threads`  [EXTRACTED]
  pyscandir/README.md → README.md
- `Rust Linux Walk Benchmark Chart` --references--> `Rust Walk Benchmarks`  [EXTRACTED]
  scandir/doc/images/linux_walk_linux-5.9.png → scandir/doc/benchmarks.md

## Hyperedges (group relationships)
- **Three Main Directory Iteration APIs** — count_api, walk_api, scandir_api [EXTRACTED 1.00]

## Communities (47 total, 7 thin omitted)

### Community 0 - "Scandir Worker"
Cohesion: 0.07
Nodes (4): create_entry(), result2py(), Scandir, worker_thread()

### Community 1 - "Walk Worker"
Cohesion: 0.07
Nodes (3): update_toc(), Walk, worker_thread()

### Community 2 - "Count Worker"
Cohesion: 0.08
Nodes (3): check_and_expand_path(), Count, count_thread()

### Community 3 - "API Docs & Benchmarks"
Cohesion: 0.1
Nodes (28): Background Thread Pattern, Count Benchmarks, Scandir Benchmarks, Walk Benchmarks, Bincode Serialization, Context Manager Pattern, Count API, DirEntry Class (+20 more)

### Community 7 - "Python Tests"
Cohesion: 0.13
Nodes (11): CreateTempFileTree(), tempDir(), tempDir(), test_scandir_ext(), test_scandir_fast(), tempDir(), test_walk_toc(), test_walk_toc_extended() (+3 more)

### Community 9 - "Rust Tests"
Cohesion: 0.22
Nodes (16): cleanup(), create_temp_file_tree(), get_filename(), setup(), test_count(), test_count_extended(), test_count_follow_links(), test_count_skip_hidden() (+8 more)

### Community 11 - "FastProperties GUI"
Cohesion: 0.2
Nodes (10): addCheckButton(), FastProperties, formatBigNumbers(), formatByteSize(), GetFileIconWin(), GetFileOwnerLin(), GetFileOwnerWin(), getType() (+2 more)

### Community 12 - "Rust Benchmarks & Docs"
Cohesion: 0.18
Nodes (13): Create Charts Tool, Rust Count Benchmarks, Rust Scandir Benchmarks, Rust Walk Benchmarks, Rust Count API, Rust Linux Scandir Benchmark Chart, Rust Linux Walk Benchmark Chart, Comparison with scan_dir crate (+5 more)

### Community 13 - "Python Benchmark Runner"
Cohesion: 0.48
Nodes (5): BenchmarkDir(), GetDiskInfo(), RunCountBenchmarks(), RunScandirBenchmarks(), RunWalkBenchmarks()

### Community 14 - "Common Filter Methods"
Cohesion: 0.48
Nodes (6): create_filter(), filter_children(), filter_dir(), filter_direntry(), get_root_path_len(), start()

### Community 15 - "Scandir Bench"
Cohesion: 0.53
Nodes (5): benchmark_dir(), benchmarks(), create_test_data(), get_metadata_ext(), MetaDataExt

### Community 16 - "Walk Bench"
Cohesion: 0.53
Nodes (5): benchmark_dir(), benchmarks(), create_test_data(), get_metadata_ext(), MetaDataExt

### Community 17 - "Build Wheels"
Cohesion: 0.8
Nodes (4): BuildWheel(), GetPyEnvVersions(), Run(), ShowResult()

### Community 19 - "Count Bench"
Cohesion: 0.83
Nodes (3): benchmark_dir(), benchmarks(), create_test_data()

### Community 20 - "Walk Data Types"
Cohesion: 0.5
Nodes (3): WalkEntry, WalkEntryExt, WalkResult

## Knowledge Gaps
- **26 isolated node(s):** `MetaDataExt`, `MetaDataExt`, `Filter`, `WalkEntry`, `WalkEntryExt` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `check_and_expand_path()` connect `Count Worker` to `Scandir Worker`, `Walk Worker`, `Common Filter Methods`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **What connects `MetaDataExt`, `MetaDataExt`, `Filter` to the rest of the system?**
  _26 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Scandir Worker` be split into smaller, more focused modules?**
  _Cohesion score 0.07 - nodes in this community are weakly interconnected._
- **Should `Walk Worker` be split into smaller, more focused modules?**
  _Cohesion score 0.07 - nodes in this community are weakly interconnected._
- **Should `Count Worker` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `API Docs & Benchmarks` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `Scandir Data Types` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._