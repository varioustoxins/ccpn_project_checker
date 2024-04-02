from project_checker.tests.testing_utils import build_cli_output, TEST_FILE
from freezegun import freeze_time

@freeze_time("2012-01-14")
def make_cli_test_file():

    test_output = build_cli_output()
    with open(TEST_FILE, 'w') as f:
        f.write(test_output)


if __name__ == '__main__':
    make_cli_test_file()