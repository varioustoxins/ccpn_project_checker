from ccpn_project_checker.DiskModelChecker import run_cli_checker
import sys

def main(file_path:str ):


    result = run_cli_checker(sys.argv[1])

    sys.exit(result)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: ccpn_project_checker <path_to_project>")
        sys.exit(1)

    main(sys.argv[1])