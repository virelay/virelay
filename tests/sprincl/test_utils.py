from sprincl.utils import import_or_stub

import pytest


def test_conditional_import():
    non_existing_module = import_or_stub('non_existing_module')
    non_existing_function = import_or_stub('non_existing_module', 'non_existing_function')
    re = import_or_stub('re')
    findall = import_or_stub('re', 'findall')

    with pytest.raises(RuntimeError):
        non_existing_module.f()
    with pytest.raises(RuntimeError):
        non_existing_function()
    re.findall('aba', 'a')
    findall('aba', 'a')

