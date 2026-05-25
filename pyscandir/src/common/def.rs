use pyo3::prelude::*;

#[pyclass(eq, eq_int, from_py_object)]
#[derive(Debug, Clone, PartialEq)]
pub enum ReturnType {
    Base,
    Ext,
}

impl ReturnType {
    #[allow(clippy::wrong_self_convention)]
    pub fn from_object(&self) -> ::scandir::ReturnType {
        match &self {
            ReturnType::Base => ::scandir::ReturnType::Base,
            ReturnType::Ext => ::scandir::ReturnType::Ext,
        }
    }
}
