from difflib import SequenceMatcher


from ccpn_project_checker.tests.testing_utils import  TEST_FILE, build_cli_output

def test_cli_checker(time_machine):
    time_machine.move_to(0, tick=False)
    EXPECTED = open(TEST_FILE).read().split('\n')
    EXPECTED_SET = set(EXPECTED)
    test_output = build_cli_output()
    for i,line in enumerate(test_output.splitlines()):
        if i <= 1:
            continue

        if 'in stand alone mode' in line:
            continue

        if not line in EXPECTED_SET:
            best_matches = {}
            matcher = SequenceMatcher()
            for j, expd in enumerate(EXPECTED):
                matcher.set_seqs(line, expd)
                best_matches.setdefault(matcher.ratio(),[]).append(((i, line), (j,expd)))
                best_match =  best_matches[max(best_matches.keys())]

                for match in best_match:
                    print(f"line: {match[0][0]} {match[0][1]}")
                    print(f"expd: {match[1][0]} {match[1][1]}")

                assert False, f"line not found: {line} in expected"




