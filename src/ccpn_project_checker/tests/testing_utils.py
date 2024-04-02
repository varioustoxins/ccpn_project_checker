# https://stackoverflow.com/questions/75048986/way-to-temporarily-change-the-directory-in-python-to-execute-code-without-affect
import os
import shutil
import stat
import sys
from difflib import SequenceMatcher
from io import StringIO
from textwrap import dedent
from time import sleep

from pathlib import Path

from ccpn_project_checker.tests.api_test_data import ERROR_CODES_NOT_READ_PROTECTED, expecteds
from ccpn_project_checker.util import different_cwd

TEST_DIRECTORY = Path(__file__).parent / '..' / 'test_data'
TEST_FILE = TEST_DIRECTORY / 'cli_test_output.txt'

class RedirectedStdoutToMemory:
    def __init__(self):
        self.new_output = StringIO()

    def __enter__(self):
        self.saved_stdout_output = sys.stdout
        self.saved_stderr_output = sys.stderr
        sys.stdout = self.new_output
        sys.stderr = self.new_output

        return self.new_output

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.saved_stdout_output
        sys.stderr = self.saved_stderr_output


from ccpn_project_checker.DiskModelChecker import (
    ErrorAndWarningData,
    ModelChecker,
    ExitStatus, run_cli_checker,
)
from ccpn_project_checker.optional import Optional


def check_results_against_expected(expected, file_path, test_directory):
    expected = list(expected)

    with different_cwd(test_directory):
        checker = ModelChecker()
        project_root = Path(test_directory).parts[-1]

        good_project = project_root == "good_projects"
        warn_project = project_root == "warn_projects"
        delayed_error_project = project_root == "delayed_errors"

        result = checker.run(file_path)

        if good_project:
            expected_exit_status = ExitStatus.EXIT_OK
        elif warn_project:
            expected_exit_status = ExitStatus.EXIT_WARN
        elif delayed_error_project:
            expected_exit_status = ExitStatus.EXIT_ERROR
        else:
            expected_exit_status = ExitStatus.EXIT_ERROR_INCOMPLETE

        if result != expected_exit_status:
            print(f"expected exit status {expected_exit_status} but got {result}")

        missing_errors = []
        for error in checker.errors:
            if isinstance(error, ErrorAndWarningData):
                found_error = assert_error_in_expected_and_return(error, expected)
                if not found_error:
                    msg = f"""\
                        failed to find error
                        code: {error.code}
                        cause: {error.cause}
                        detail: {error.detail}

                        because {found_error.messages}
                    """
                    print(dedent(msg), file=sys.stderr)
                    missing_errors.append(error)
                else:
                    found_error = found_error.get()
                    expected.remove(found_error)

        unexpected_messages = []
        for message in checker.messages:
            if message[0] == "":
                continue

            if 'in stand alone mode' in message[0]:
                continue

            if message in expected:
                # print('unexpected message:', message)
                expected.remove(message)
            else:
                unexpected_messages.append(message)

        BAR = "|"
        if unexpected_messages:
            unexpected_messages = [
                f"{BAR}{message}{BAR}" for message in unexpected_messages
            ]

            print("unexpected messages:")
            for unexpected_message in unexpected_messages:
                print(dedent(unexpected_message), file=sys.stderr)

        remaining_messages = [
            f"{BAR}{message}{BAR}"
            for message in expected
            if not isinstance(message, ErrorAndWarningData)
        ]
        if remaining_messages:
            print("remaining messages:", file=sys.stderr)
            for remaining_message in remaining_messages:
                print(dedent(remaining_message), file=sys.stderr)

            print("checker errors:")
            for error in checker.errors:
                print(dedent(str(error)), file=sys.stderr)
        
        if len(expected) > 0:
            print("expected messages and which were not found:", expected)

        assert missing_errors == []

        assert result == expected_exit_status

        assert unexpected_messages == []

        assert expected == []


def get_test_project_and_working_directory(file_path):
    file_path = Path(file_path)
    project_index = None

    for i, part in enumerate(list(file_path.parts)):
        if part.endswith(".ccpn") or part.endswith("_ccpn"):
            project_index = i
            break

    if not project_index:
        raise ValueError(f"couldn't find project directory in {file_path}")

    directory_offset = project_index
    project_path = Path(*file_path.parts[directory_offset:])
    working_directory = Path(*file_path.parts[:directory_offset])
    return project_path, working_directory


def make_path_unreadable_by_owner(path):
    old_mode = stat.S_IMODE(os.lstat(path).st_mode)
    new_mode = old_mode & ~stat.S_IRUSR
    os.chmod(path, new_mode)


def path_is_readable_by_owner(path):
    current_permissions = stat.S_IMODE(os.lstat(path).st_mode)

    return bool(current_permissions & stat.S_IRUSR)


def setup_read_protected(file_path, tmp_path, files_to_protect=()):
    file_path = Path(file_path).resolve()
    tmp_path = Path(tmp_path)

    new_root = tmp_path / file_path.parts[-1]
    shutil.copytree(file_path, new_root)

    can_read_path = False
    for i in range(10):
        for target, recursive in files_to_protect:
            target_path = tmp_path / target
            make_path_unreadable_by_owner(target_path)
            can_read_path = path_is_readable_by_owner(target_path)
            if can_read_path == 0:
                sleep(0.01)
            else:
                break

    assert (
        not bool(can_read_path)
    ), f"couldn't set the path {target_path} to read only!"

    return new_root


def match_ratio(expected, actual):
    matcher = SequenceMatcher(None, expected, actual)
    return matcher.ratio()


def lstrip_all(text):
    return "\n".join([elem.lstrip() for elem in text.split("\n")])


def assert_error_in_expected_and_return(error, expected, match_distance=0.99):
    result = None
    failures = []

    error_count = 0
    for expected_error in expected:
        if isinstance(expected_error, ErrorAndWarningData):
            error_count += 1

            # for some reason pytest? is screwing up the comparison of the error codes possibly by reloading the enum
            # so we have to compare the values rather than the ids of the enums
            if error.code.value != expected_error.code.value:
                failures.append(
                    f"error code expected: {expected_error.code}, found: {error.code}"
                )
                continue

            if str(expected_error.cause) != str(error.cause):
                failures.append(
                    f"cause expected: {expected_error.cause[:30]}..., found: {error.cause[:30]}..."
                )
                continue

            detail_distance = SequenceMatcher(
                None, lstrip_all(expected_error.detail), lstrip_all(error.detail)
            ).ratio()
            if detail_distance < match_distance:
                failures.append(
                    f"detail expected: {expected_error.detail[:30]}..., found: {error.detail[:30]}..."
                )
                continue

            result = expected_error
            break

    if not result and not error_count:
        failures = ["no errors defined!"]

    return Optional.of(result, messages=failures)



def build_cli_output():
    with RedirectedStdoutToMemory() as saved_stdout:
        print(file=sys.stderr)
        max_length_of_test_case_name = max(
            [len(test_case) for test_case in ERROR_CODES_NOT_READ_PROTECTED]
        )
        for test_case in ERROR_CODES_NOT_READ_PROTECTED:
            print(file=sys.stderr)
            test_case_name = f" {test_case} ".center(max_length_of_test_case_name, "-")
            print(f"{'-'*20}{test_case_name}{'-'*20}", file=sys.stderr)
            file_path, expected = expecteds[test_case]

            tests_directory = Path(__file__).parent

            file_path = tests_directory / file_path

            project_path, working_directory = get_test_project_and_working_directory(
                file_path
            )

            with different_cwd(working_directory):
                exit_code = run_cli_checker(project_path)

            print(file=sys.stderr)
            print(
                f"command exited with exit code: {exit_code}, [{ExitStatus(exit_code)}]",
                file=sys.stderr,
            )

        print(file=sys.stderr)
        dummy_name = '-'*max_length_of_test_case_name
        filler = f'-{dummy_name}-'
        print(f"{'-' * 20}{filler}{'-' * 20}", file=sys.stderr)

    return saved_stdout.getvalue()
