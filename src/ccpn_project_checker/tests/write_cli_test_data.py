from ccpn_project_checker.tests.testing_utils import build_cli_output, TEST_FILE
import time_machine

@time_machine.travel(0,tick=False)
def make_cli_test_file():

    test_output = build_cli_output()
    with open(TEST_FILE, 'w') as f:
        f.write(test_output)


if __name__ == '__main__':
    make_cli_test_file()