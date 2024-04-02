import sys, os
from pathlib import Path

import pytest
from ccpn_project_checker.util import different_cwd

def run_tests():
    root_path = Path(os.path.realpath(__file__)).parent.resolve() / 'tests'
    with different_cwd(root_path):
        retcode = pytest.main(['--rootdir', root_path, '-vvv'])
        sys.exit(retcode)


if __name__ == '__main__':
    run_tests()