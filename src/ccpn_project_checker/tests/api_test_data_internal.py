import os
import sys
from pathlib import Path

from ccpn_project_checker.DiskModelChecker import (
    _get_parent_path,
    ErrorCode,
    ErrorAndWarningData,
    _dedent_all,
)

ERROR_CODE = "error_code"
EXPECTEDS = "expecteds"

EXPECTED_INTERNAL = {
    # test case with bad xml in one of the files (contains a raw & symbol derived from ccpn internal
    "231211_hproNGF.ccpn": {
        ERROR_CODE: ErrorCode.BAD_XML,
        EXPECTEDS: [
            ErrorAndWarningData(
                code=ErrorCode.BAD_XML,
                cause="../test_data/231211_hproNGF.ccpn/ccpnv3/ccp/nmr/Nmr/prongf+prongf_user_2023-12-14-10-44-42-561_00001.xml",
                detail=_dedent_all("""\
                               could not read the file ../test_data/231211_hproNGF.ccpn/ccpnv3/ccp/nmr/Nmr/prongf+prongf_user_2023-12-14-10-44-42-561_00001.xml because\n'
                               while xml parsing ../test_data/231211_hproNGF.ccpn/ccpnv3/ccp/nmr/Nmr/prongf+prongf_user_2023-12-14-10-44-42-561_00001.xml 
                               i got the error not well-formed (invalid token): line 27381, column 381"""),
            ),
            ErrorAndWarningData(
                code=ErrorCode.EXO_LINKED_FILE_HAS_WRONG_KEY,
                cause="../test_data/231211_hproNGF.ccpn/ccpnv3/ccp/molecule/ChemElement/CCPN_reference+msd_ccpnRef_2007-12-11-11-36-46_00001.xml",
                detail=_dedent_all("""\
                               in the exo linked file CCPN_reference+msd_ccpnRef_2007-12-11-11-36-46_00001.xml
                               the key name [index 1] in the original link does not match the key expected key from the filename
                               key in the file name: CCPN reference key in the root file contents: CCPN_reference"""),
            ),
        ],
    }
}

INTERNAL_TEST_DATA_PATH = _get_parent_path(Path(os.getcwd()), 2) / "internal_test_data"
if INTERNAL_TEST_DATA_PATH.exists():
    INTERNAL_PROJECTS = INTERNAL_TEST_DATA_PATH.glob("*.ccpn")
else:
    INTERNAL_PROJECTS = []
    print(
        f"internal project test directory [{INTERNAL_TEST_DATA_PATH}] doesn't exist, tests skipped",
        file=sys.stderr,
    )
