#![cfg_attr(windows, feature(junction_point))]

use std::io::Error;

use scandir::{ReturnType, Scandir};
#[cfg(target_os = "linux")]
use scandir::ScandirResult;

mod common;

#[test]
fn test_scandir() -> Result<(), Error> {
    #[cfg(unix)]
    let temp_dir = common::create_temp_file_tree(3, 3, 4, 5, 6, 7)?;
    #[cfg(windows)]
    let temp_dir = common::create_temp_file_tree(3, 3, 4, 5, 3)?;
    let entries = Scandir::new(temp_dir.path(), Some(true))?.collect()?;
    #[cfg(unix)]
    assert_eq!(210, entries.results.len());
    #[cfg(windows)]
    assert_eq!(126, entries.results.len());
    assert_eq!(0, entries.errors.len());
    #[cfg(target_os = "linux")]
    match entries.results.first().unwrap() {
        ScandirResult::DirEntry(d) => {
            assert_eq!("dir3", &d.path);
            assert!(d.is_dir);
            #[cfg(target_os = "linux")]
            assert!(d.st_size <= 4096); // Directories on tmpfs can have a size smaller than 4096
            #[cfg(target_os = "macos")]
            assert_eq!(96, d.st_size);
            #[cfg(windows)]
            assert_eq!(0, d.st_size);
        }
        _ => panic!("Wrong type"),
    }
    common::cleanup(temp_dir)
}

#[test]
fn test_scandir_skip_hidden() -> Result<(), Error> {
    #[cfg(unix)]
    let temp_dir = common::create_temp_file_tree(3, 3, 4, 5, 6, 7)?;
    #[cfg(windows)]
    let temp_dir = common::create_temp_file_tree(3, 3, 4, 5, 3)?;
    let scandir = Scandir::new(temp_dir.path(), Some(true))?;
    let mut scandir = scandir.skip_hidden(true);
    let entries = scandir.collect()?;
    #[cfg(unix)]
    assert_eq!(192, entries.results.len());
    #[cfg(windows)]
    assert_eq!(108, entries.results.len());
    assert_eq!(0, entries.errors.len());
    #[cfg(target_os = "linux")]
    match entries.results.first().unwrap() {
        ScandirResult::DirEntry(d) => {
            assert!(["dir1", "dir2", "dir3"].contains(&d.path.as_str()));
            assert!(d.is_dir);
            #[cfg(target_os = "linux")]
            assert!(d.st_size <= 4096); // Directories on tmpfs can have a size smaller than 4096
            #[cfg(target_os = "macos")]
            assert_eq!(96, d.st_size);
            #[cfg(windows)]
            assert_eq!(0, d.st_size);
        }
        _ => panic!("Wrong type"),
    }
    common::cleanup(temp_dir)
}

#[test]
fn test_scandir_extended() -> Result<(), Error> {
    #[cfg(unix)]
    let temp_dir = common::create_temp_file_tree(3, 3, 4, 5, 6, 7)?;
    #[cfg(windows)]
    let temp_dir = common::create_temp_file_tree(3, 3, 4, 5, 3)?;
    let entries = Scandir::new(temp_dir.path(), Some(true))?
        .return_type(ReturnType::Ext)
        .collect()?;
    #[cfg(unix)]
    assert_eq!(210, entries.results.len());
    #[cfg(windows)]
    assert_eq!(126, entries.results.len());
    assert_eq!(0, entries.errors.len());
    #[cfg(target_os = "linux")]
    match entries.results.first().unwrap() {
        ScandirResult::DirEntryExt(d) => {
            assert!(["dir1", "dir2", "dir3"].contains(&d.path.as_str()));
            assert!(d.is_dir);
            #[cfg(target_os = "linux")]
            assert!(d.st_size <= 4096); // Directories on tmpfs can have a size smaller than 4096
            #[cfg(target_os = "macos")]
            assert_eq!(96, d.st_size);
            #[cfg(windows)]
            assert_eq!(0, d.st_size);
        }
        _ => panic!("Wrong type"),
    }
    common::cleanup(temp_dir)
}

#[test]
fn test_scandir_follow_links() -> Result<(), Error> {
    #[cfg(unix)]
    let temp_dir = common::create_temp_file_tree(3, 3, 4, 5, 6, 7)?;
    #[cfg(windows)]
    let temp_dir = common::create_temp_file_tree(3, 3, 4, 5, 3)?;
    let entries = Scandir::new(temp_dir.path(), Some(true))?
        .follow_links(true)
        .collect()?;
    #[cfg(unix)]
    assert_eq!(210, entries.results.len());
    #[cfg(windows)]
    assert_eq!(234, entries.results.len());
    assert_eq!(0, entries.errors.len());
    #[cfg(target_os = "linux")]
    match entries.results.first().unwrap() {
        ScandirResult::DirEntry(d) => {
            assert_eq!("dir3", &d.path);
            assert!(d.is_dir);
            #[cfg(target_os = "linux")]
            assert!(d.st_size <= 4096); // Directories on tmpfs can have a size smaller than 4096
            #[cfg(target_os = "macos")]
            assert_eq!(96, d.st_size);
            #[cfg(windows)]
            assert_eq!(0, d.st_size);
        }
        _ => panic!("Wrong type"),
    }
    common::cleanup(temp_dir)
}

#[test]
fn test_scandir_categorizes_dirs_and_files() -> Result<(), Error> {
    #[cfg(unix)]
    let temp_dir = common::create_temp_file_tree(3, 3, 4, 5, 6, 7)?;
    #[cfg(windows)]
    let temp_dir = common::create_temp_file_tree(3, 3, 4, 5, 3)?;
    let entries = Scandir::new(temp_dir.path(), Some(true))?.collect()?;
    assert!(entries.dirs().next().is_some(), "dirs should contain subdirectories");
    assert!(entries.files().next().is_some(), "files should contain regular files");
    assert_eq!(
        entries.results.len(),
        entries.dirs().count() + entries.files().count() + entries.symlinks().count() + entries.other().count(),
        "results total should equal sum of categorized fields"
    );
    assert_eq!(0, entries.errors.len());
    common::cleanup(temp_dir)
}

#[test]
fn test_scandir_categorization_types() -> Result<(), Error> {
    #[cfg(unix)]
    let temp_dir = common::create_temp_file_tree(3, 3, 4, 5, 6, 7)?;
    #[cfg(windows)]
    let temp_dir = common::create_temp_file_tree(3, 3, 4, 5, 3)?;
    let entries = Scandir::new(temp_dir.path(), Some(true))?.collect()?;
    for entry in entries.dirs() {
        assert!(entry.is_dir(), "entry in dirs should be a directory");
    }
    for entry in entries.files() {
        assert!(entry.is_file(), "entry in files should be a file");
    }
    for entry in entries.symlinks() {
        assert!(entry.is_symlink(), "entry in symlinks should be a symlink");
    }
    common::cleanup(temp_dir)
}

#[test]
fn test_scandir_results_backward_compat() -> Result<(), Error> {
    #[cfg(unix)]
    let temp_dir = common::create_temp_file_tree(3, 3, 4, 5, 6, 7)?;
    #[cfg(windows)]
    let temp_dir = common::create_temp_file_tree(3, 3, 4, 5, 3)?;
    let entries = Scandir::new(temp_dir.path(), Some(true))?.collect()?;
    assert!(!entries.results.is_empty(), "results field should still contain all entries");
    #[cfg(unix)]
    assert_eq!(210, entries.results.len());
    #[cfg(windows)]
    assert_eq!(126, entries.results.len());
    let categorized = entries.dirs().count() + entries.files().count() + entries.symlinks().count() + entries.other().count();
    assert_eq!(entries.results.len(), categorized, "sum of categorized should equal results");
    common::cleanup(temp_dir)
}
