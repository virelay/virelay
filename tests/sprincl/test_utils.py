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


def test_conditional_import_of_multiple_functions():
    match, fullmatch = import_or_stub('non_existing_module', ('match', 'fullmatch'))
    with pytest.raises(RuntimeError):
        match('aba', 'a')
    with pytest.raises(RuntimeError):
        fullmatch('aba', 'a')

    match, fullmatch = import_or_stub('re', ('match', 'fullmatch'))
    match('aba', 'a')
    fullmatch('aba', 'a')

    with pytest.raises(ImportError):
        _, _ = import_or_stub('re', ('findall', 'non_existing'))
