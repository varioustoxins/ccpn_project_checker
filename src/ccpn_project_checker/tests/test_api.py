import json
import os
import stat

from pathlib import Path

from ccpn_project_checker.DiskModelChecker import ModelChecker, ExitStatus
import pytest

from .api_test_data_internal import EXPECTED_INTERNAL, INTERNAL_PROJECTS, INTERNAL_TEST_DATA_PATH, ERROR_CODE, EXPECTEDS
from .api_test_data import expecteds, \
    ERROR_CODES_READ_PROTECTED, FILES_TO_PROTECT_BY_ERROR_CODE, ERROR_CODES_NOT_READ_PROTECTED
from .testing_utils import get_test_project_and_working_directory, setup_read_protected, \
    assert_error_in_expected_and_return, check_results_against_expected


@pytest.fixture
def cleanup_write_protected_files(tmp_path):
    yield
    for dirpath, dirnames, filenames in os.walk(tmp_path):
        for dirname in dirnames:
            dir_full_path = os.path.join(dirpath, dirname)
            current_permissions = stat.S_IMODE(os.lstat(dir_full_path).st_mode)
            os.chmod(dir_full_path, current_permissions | stat.S_IREAD)
        for filename in filenames:
            file_full_path = os.path.join(dirpath, filename)
            current_permissions = stat.S_IMODE(os.lstat(file_full_path).st_mode)
            os.chmod(file_full_path, current_permissions | stat.S_IREAD)

@pytest.mark.parametrize(
    "test_case",
    ERROR_CODES_READ_PROTECTED
)
@pytest.mark.usefixtures("cleanup_write_protected_files")
def test_memops_checker_read_protected(test_case, tmp_path, time_machine):
    time_machine.move_to(0, tick=False)
    file_path, expected = expecteds[test_case]
    read_protected_files = FILES_TO_PROTECT_BY_ERROR_CODE[test_case]

    tests_directory = Path(__file__).parent

    file_path = tests_directory / file_path

    file_path = setup_read_protected(file_path, tmp_path, read_protected_files)

    project_path, working_directory = get_test_project_and_working_directory(file_path)

    check_results_against_expected(expected, project_path, working_directory)



@pytest.mark.parametrize(
    "test_case",
    ERROR_CODES_NOT_READ_PROTECTED
    # ['EXO_LINKS_WITH_KEYS_OUTSIDE_THE_CCPN_CHARACTER_SET']
)
def test_memops_checker_normal(test_case, time_machine):
    time_machine.move_to(0, tick=False)
    file_path, expected = expecteds[test_case]

    tests_directory = Path(__file__).parent

    file_path = tests_directory / file_path

    project_path, working_directory = get_test_project_and_working_directory(file_path)

    check_results_against_expected(expected, project_path, working_directory)



def test_internal_error():
    file_path, expected = expecteds['GOOD_PROJECT_WITHOUT_ERRORS']
    checker = ModelChecker()

    def raise_exception(*args, **kwargs):
        raise Exception('test exception')

    checker._get_project_name = raise_exception
    result = checker.run(file_path)

    assert result == ExitStatus.EXIT_INTERNAL_ERROR


def test_Mfull_assignment_pH475_LH2():
    path = '/Users/garyt/Downloads/Mfull_assignment_pH475_LH2.ccpn'
    checker = ModelChecker()
    result = checker.run(path)

    for message in checker.messages:
        print(message[0])

    if len(checker.errors) > 0:
        print('There were errors')

@pytest.mark.parametrize(
    "file_path",
    INTERNAL_PROJECTS
)
def test_internal_tests(file_path, time_machine):
    time_machine.move_to(0, tick=False)
    checker = ModelChecker()

    result = checker.run(INTERNAL_TEST_DATA_PATH / file_path)

    if file_path in EXPECTED_INTERNAL:
        error_code = EXPECTED_INTERNAL[file_path][ERROR_CODE]
        assert result == error_code

        expected_errors = list(EXPECTED_INTERNAL[file_path][EXPECTEDS])

        for error in checker.errors:

                found_error = assert_error_in_expected_and_return(error, expected_errors)
                if found_error:
                    found_error = found_error.get()
                    expected_errors.remove(found_error)
                else:
                    print(error)
                    print('failure is', '\n'.join(found_error.messages))


        assert expected_errors == []


def test_get_top_object_key_types():

    # these are the types currently used as top object keys...

    EXPECTED_TYPES = ['Word', 'MolSystem', 'LongWord', 'NmrProject', 'MolType', 'Line', 'PositiveInt', 'Int']

    model_info_path = Path(__file__).parent.parent / 'model_info' / 'v_3_1_0_object_info.json'

    if not model_info_path.exists():
        pytest.skip(f'Model info file found, expected path was {str(model_info_path)}')

    with open(model_info_path, 'r') as fh:
        data = fh.read()

    json_data = json.loads(data)

    types = set()
    for object in json_data.values():
        name = object['name']

        role_keys = ['MolType', 'MolSystem', 'NmrProject']
        for super_object in object['supertype_names'] or name in role_keys:
            if 'TopObject' in super_object:
                for key in object['keys']:
                    key_type = object['key_types_names'][key][-1]

                    # for information
                    # print(f'{name}: {key}, {key_type}')
                    types.add(key_type)

    assert types == set(EXPECTED_TYPES)





