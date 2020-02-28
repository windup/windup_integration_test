import imp

from py.path import local

_rhamt_package_dir = local(imp.find_module("rhamt")[1])

#: The project root, ``rhamt_tests/``
project_path = _rhamt_package_dir.dirpath()

conf_path = project_path.join("conf")
