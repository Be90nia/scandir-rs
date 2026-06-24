use std::path::PathBuf;

use crate::ReturnType;

#[derive(Debug, Clone)]
pub struct Options {
    pub root_path: PathBuf,
    pub sorted: bool,
    pub skip_hidden: bool,
    pub max_depth: usize,
    pub max_file_cnt: usize,
    pub dir_include: Option<Vec<String>>,
    pub dir_exclude: Option<Vec<String>>,
    pub file_include: Option<Vec<String>>,
    pub file_exclude: Option<Vec<String>>,
    pub case_sensitive: bool,
    pub follow_links: bool,
    pub return_type: ReturnType,
}
