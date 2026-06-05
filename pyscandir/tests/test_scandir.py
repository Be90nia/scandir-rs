# -*- coding: utf-8 -*-

import pytest
from scandir_rs import Scandir, ReturnType

from .common import CreateTempFileTree


@pytest.fixture(scope="session", autouse=True)
def tempDir():
    tmpDir = CreateTempFileTree(10, 3, 10)
    yield tmpDir
    tmpDir.cleanup()


def test_scandir_fast(tempDir):
    sd = Scandir(tempDir.name, return_type=ReturnType.Base)
    contents = {}
    for dirEntry in sd:
        assert dirEntry.atime > 0.0
        assert dirEntry.ctime > 0.0
        assert dirEntry.mtime > 0.0
        assert not hasattr(dirEntry, "st_mode")
        contents[dirEntry.path] = dirEntry
    assert len(contents) == 186


def test_scandir_ext(tempDir):
    sd = Scandir(tempDir.name, return_type=ReturnType.Ext)
    contents = {}
    for dirEntry in sd:
        assert dirEntry.atime > 0.0
        assert dirEntry.ctime > 0.0
        assert dirEntry.mtime > 0.0
        assert hasattr(dirEntry, "st_mode")
        contents[dirEntry.path] = dirEntry
    assert len(contents) == 186


def test_collect_returns_scandir_results():
    """collect() should return ScandirResults with categorized attributes."""
    from scandir_rs import Scandir, ScandirResults
    tmpDir = CreateTempFileTree(3, 2, 3)
    try:
        sd = Scandir(tmpDir.name)
        result = sd.collect()
        assert result is not None
        assert isinstance(result, ScandirResults)
        assert hasattr(result, 'dirs')
        assert hasattr(result, 'files')
        assert hasattr(result, 'symlinks')
        assert hasattr(result, 'other')
        assert hasattr(result, 'errors')
        assert hasattr(result, 'results')
    finally:
        tmpDir.cleanup()


def test_collect_dirs_files_separated():
    """dirs and files should be properly separated."""
    from scandir_rs import Scandir
    tmpDir = CreateTempFileTree(3, 1, 5)
    try:
        sd = Scandir(tmpDir.name)
        result = sd.collect()
        assert result is not None
        assert len(result.dirs) >= 3, "Should find at least 3 directories"
        assert len(result.files) >= 5, "Should find at least 5 files"
        dir_paths = set(d.path for d in result.dirs)
        file_paths = set(f.path for f in result.files)
        assert len(dir_paths & file_paths) == 0, "No overlap between dirs and files"
    finally:
        tmpDir.cleanup()


def test_collect_results_backward_compat():
    """results field should still contain all entries for backward compat."""
    from scandir_rs import Scandir
    tmpDir = CreateTempFileTree(3, 1, 3)
    try:
        sd = Scandir(tmpDir.name)
        result = sd.collect()
        assert result is not None
        assert len(result.results) > 0, "results should contain entries"
        categorized = len(result.dirs) + len(result.files) + len(result.symlinks) + len(result.other)
        assert len(result.results) == categorized, "sum of categorized should equal results"
    finally:
        tmpDir.cleanup()
