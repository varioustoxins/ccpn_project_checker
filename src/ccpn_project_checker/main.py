from ccpn_project_checker.DiskModelChecker import run_cli_checker
import sys

def main():
    result = run_cli_checker()

    sys.exit(result)

