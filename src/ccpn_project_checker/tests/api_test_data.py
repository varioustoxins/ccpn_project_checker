from pathlib import Path

from ccpn_project_checker.DiskModelChecker import ErrorAndWarningData, ErrorCode, _dedent_all


BAD_EXO_3_CONTENT_CORRECTIONS = {
    "583_00004 MOLS.MolSystem - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]": "583_00004 MOLS.MolSystem - xml is bad skipped [see errors at the end of the run for details]",
    "all the analysed linked top objects [8] appear to have the correct basic structure": _dedent_all("""only 7 of the 8 analysed top objects appear to have the correct basic structure
                  [see complete errors at the end of the the run for details]"""),
}
EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT = [
    # tranche 0 always runs
    ("analysis took 0.000 seconds", False),
    # tranche 1 pre good memops root
    ("target {project_name}.ccpn", False),
    ("project_name appears to be... {project_name}", False),
    ("the directory {project_name}.ccpn has the correct suffix", False),
    (
        "found an implementation directory {project_name}.ccpn/ccpnv3/memops/Implementation",
        False,
    ),
    (
        "the path {project_name}.ccpn/ccpnv3/memops/Implementation/{project_name}.xml is a possible memops root [name matches project]",
        False,
    ),
    ("The project in {project_name}.xml, was not renamed after saving", False),
    # tranche 2 post good memops root
    (
        "ccpn project memops root file found in {project_name}.ccpn/ccpnv3/memops/Implementation/{project_name}.xml",
        False,
    ),
    ("model version that saved this file appears to be 3.1.0", False),
    ("memops root data was stored at Sat Feb 24 16:16:06 2024", False),
    ("ccpnmr program version that saved this file appears to be 3.2.1", False),
]


EXPECTED_GOOD_EXO_LINKS = [
    ("searching for top object exo links, found 8", False),
    ("analysing exo links", False),
    (
        "  1. default_user_2024-02-24-15-54-35-583_00006 GUIT.GuiTask [keys: {{'nameSpace': 'user', 'name': 'View'}}]",
        True,
    ),
    (
        "  2. IsoSchemeProj_user_2008-08-01-11-46-16_00022 CCLB.LabelingScheme [keys: {{'name': 'uni_15N'}}]",
        True,
    ),
    (
        "  3. default_user_2024-02-24-15-54-35-583_00004 MOLS.MolSystem [keys: {{'code': 'default'}}]",
        True,
    ),
    (
        "  4. cam_wb104_2008-01-15-16-06-39_00031 NMRX.NmrExpPrototype [keys: {{'serial': '32'}}]",
        True,
    ),
    (
        "  5. default_user_2024-02-24-15-54-35-583_00001 NMR.NmrProject [keys: {{'name': 'default'}}]",
        True,
    ),
    (
        "  6. default_user_2024-02-24-15-54-35-583_00003 REFS.RefSampleComponentStore [keys: {{'name': 'default'}}]",
        True,
    ),
    (
        "  7. default_user_2024-02-24-15-54-35-583_00002 SAM.SampleStore [keys: {{'name': 'default'}}]",
        True,
    ),
    (
        "  8. default_user_2024-02-24-15-54-35-583_00005 GUIW.WindowStore [keys: {{'nmrProject': '_ccp_nmr_Nmr_NmrProject___default___'}}]",
        True,
    ),
    ("found 8 out of 8 top object files exo linked by the project", False),
    ("expected top object paths are:", False),
    ("  1. default_user_2024-02-24-15-54-35-583_00006 GUIT.GuiTask - [PROJECT] ccpnmr/gui/Task/user+View+default_user_2024-02-24-15-54-35-583_00006.xml", True),
    ("  2. IsoSchemeProj_user_2008-08-01-11-46-16_00022 CCLB.LabelingScheme - [REFERENCE] ccp/molecule/ChemCompLabel/uni_15N+IsoSchemeProj_user_2008-08-01-11-46-16_00022.xml", True),
    ("  3. default_user_2024-02-24-15-54-35-583_00004 MOLS.MolSystem - [PROJECT] ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml", True),
    ("  4. cam_wb104_2008-01-15-16-06-39_00031 NMRX.NmrExpPrototype - [REFERENCE] ccp/nmr/NmrExpPrototype/32+cam_wb104_2008-01-15-16-06-39_00031.xml", True),
    ("  5. default_user_2024-02-24-15-54-35-583_00001 NMR.NmrProject - [PROJECT] ccp/nmr/Nmr/default+default_user_2024-02-24-15-54-35-583_00001.xml", True),
    ("  6. default_user_2024-02-24-15-54-35-583_00003 REFS.RefSampleComponentStore - [PROJECT] ccp/lims/RefSampleComponent/default+default_user_2024-02-24-15-54-35-583_00003.xml", True),
    ("  7. default_user_2024-02-24-15-54-35-583_00002 SAM.SampleStore - [PROJECT] ccp/lims/Sample/default+default_user_2024-02-24-15-54-35-583_00002.xml", True),
    ("  8. default_user_2024-02-24-15-54-35-583_00005 GUIW.WindowStore - [PROJECT] ccpnmr/gui/Window/_ccp_nmr_Nmr_NmrProject___default___+default_user_2024-02-24-15-54-35-583_00005.xml", True),

    ("checking the contents of 8 linked top objects", False),
    (
        "  1. default_user_2024-02-24-15-54-35-583_00006 GUIT.GuiTask - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]",
        True,
    ),
    (
        "  2. IsoSchemeProj_user_2008-08-01-11-46-16_00022 CCLB.LabelingScheme - is ok [reference object assumed good (further analysis skipped)]",
        True,
    ),
    (
        "  3. default_user_2024-02-24-15-54-35-583_00004 MOLS.MolSystem - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]",
        True,
    ),
    (
        "  4. cam_wb104_2008-01-15-16-06-39_00031 NMRX.NmrExpPrototype - is ok [reference object assumed good (further analysis skipped)]",
        True,
    ),
    (
        "  5. default_user_2024-02-24-15-54-35-583_00001 NMR.NmrProject - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]",
        True,
    ),
    (
        "  6. default_user_2024-02-24-15-54-35-583_00003 REFS.RefSampleComponentStore - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]",
        True,
    ),
    (
        "  7. default_user_2024-02-24-15-54-35-583_00002 SAM.SampleStore - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]",
        True,
    ),
    (
        "  8. default_user_2024-02-24-15-54-35-583_00005 GUIW.WindowStore - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]",
        True,
    ),
    (
        "all the analysed linked top objects [8] appear to have the correct basic structure",
        False,
    ),
    ("checking the exo link keys in 8 top object file names", False),
    (
        "  1. default_user_2024-02-24-15-54-35-583_00006 GUIT.GuiTask - all keys are good",
        True,
    ),
    (
        "  2. IsoSchemeProj_user_2008-08-01-11-46-16_00022 CCLB.LabelingScheme - all keys are good",
        True,
    ),
    (
        "  3. default_user_2024-02-24-15-54-35-583_00004 MOLS.MolSystem - all keys are good",
        True,
    ),
    (
        "  4. cam_wb104_2008-01-15-16-06-39_00031 NMRX.NmrExpPrototype - all keys are good",
        True,
    ),
    (
        "  5. default_user_2024-02-24-15-54-35-583_00001 NMR.NmrProject - all keys are good",
        True,
    ),
    (
        "  6. default_user_2024-02-24-15-54-35-583_00003 REFS.RefSampleComponentStore - all keys are good",
        True,
    ),
    (
        "  7. default_user_2024-02-24-15-54-35-583_00002 SAM.SampleStore - all keys are good",
        True,
    ),
    (
        "  8. default_user_2024-02-24-15-54-35-583_00005 GUIW.WindowStore - all keys are good",
        True,
    ),
    ("8 of the 8 keys are good", False),
]


def update_notes(
    templates,
    file_name="",
    sub_directory="",
    replace_text={},
    replace_item={},
    delete=(),
    discard_beyond=None,
):
    def expand_file_name_template(template, project_name, sub_directory):
        return eval(f'f"""{template}"""')

    templates = list(templates)

    # TODO move this after template expansion
    if discard_beyond:
        new_templates = []
        for item in templates:
            if discard_beyond in item[0]:
                new_templates.append(item)
                break
            else:
                new_templates.append(item)
        templates = new_templates

    for target, replacement in replace_text.items():
        for i, template in enumerate(templates):
            if target in template[0]:
                templates[i] = (template[0].replace(target, replacement), template[1])

    sub_directory = f"/{sub_directory}" if sub_directory else ""
    result = [
        (
            expand_file_name_template(note[0], file_name, sub_directory),
            note[1],
        )
        for note in templates
    ]

    for i, item in enumerate(result):
        if item in replace_item.items():
            result[i] = replace_item[item]

    for i, item in enumerate(result):
        for deletion_item in delete:
            if deletion_item in item:
                result[i] = None
    result = [item for item in result if item is not None]

    return result


expecteds = {
    "MISSING_PROJECT": [
        "../test_data/no_such_file.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.MISSING_DIRECTORY,
                Path("no_such_file.ccpn"),
                "the directory no_such_file.ccpn doesn't exist",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                "no_such_file",
                discard_beyond="project_name appears to be",
            ),
        ],
    ],
    "PROJECT_IS_FILE": [
        "../test_data/project_is_file.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.IS_NOT_DIRECTORY,
                Path("project_is_file.ccpn"),
                "the path project_is_file.ccpn should be a directory, it isn't, its a file",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                "project_is_file",
                discard_beyond="project_name appears to be",
            ),
        ],
    ],
    "EMPTY_PROJECT": [
        "../test_data/empty_project.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.MISSING_DIRECTORY,
                Path("empty_project.ccpn/ccpnv3"),
                "the directory empty_project.ccpn/ccpnv3 doesn't exist",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                "empty_project",
                discard_beyond="has the correct suffix",
            ),
        ],
    ],
    "EMPTY_PROJECT_NO_EXTENSION": [
        "../test_data/empty_project_no_extension_ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.MISSING_DIRECTORY,
                Path("empty_project_no_extension_ccpn/ccpnv3"),
                "the directory empty_project_no_extension_ccpn/ccpnv3 doesn't exist",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                "empty_project_no_extension_ccpn",
                discard_beyond="project_name appears to be",
                replace_text={".ccpn": ""},
            ),
            (
                "ccpn project directories should have the suffix .ccpn the directory empty_project_no_extension_ccpn doesn't",
                False,
            ),
        ],
    ],
    "READ_PROTECTED_PROJECT": [
        "../test_data/no_read_empty_project.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.NOT_READABLE,
                Path("no_read_empty_project.ccpn"),
                "the path no_read_empty_project.ccpn is not readable",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                "no_read_empty_project",
                discard_beyond="project_name appears to be",
            ),
        ],
    ],
    "EMPTY_CCPNV3": [
        "../test_data/empty_ccpnv3.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.MISSING_DIRECTORY,
                Path("empty_ccpnv3.ccpn/ccpnv3/memops/Implementation"),
                "the directory empty_ccpnv3.ccpn/ccpnv3/memops/Implementation doesn't exist",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                "empty_ccpnv3",
                discard_beyond=" has the correct suffix",
            ),
        ],
    ],
    "READ_PROTECTED_CCPNV3": [
        "../test_data/no_read_ccpnv3.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.NOT_READABLE,
                Path("no_read_ccpnv3.ccpn/ccpnv3"),
                "the path no_read_ccpnv3.ccpn/ccpnv3 is not readable",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                "no_read_ccpnv3",
                discard_beyond="has the correct suffix",
            ),
        ],
    ],
    "EMPTY_IMPLEMENTATION": [
        "../test_data/empty_implementation.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.NO_MEMOPS_ROOT_FILES,
                Path("empty_implementation.ccpn/ccpnv3/memops/Implementation"),
                """no xml files which could be memops roots were found in empty_implementation.ccpn/ccpnv3/memops/Implementation
                         with the following extra messages being reported no root xml file found in empty_implementation.ccpn/ccpnv3/memops/Implementation""",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                "empty_implementation",
                discard_beyond="found an implementation directory",
            ),
        ],
    ],
    "MEMOPS_ROOT_XML_IS_DIRECTORY": [
        "../test_data/memops_root_xml_is_directory.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.IS_NOT_FILE,
                Path(
                    "memops_root_xml_is_directory.ccpn/ccpnv3/memops/Implementation/memops_root_xml_is_directory.xml"
                ),
                "memops_root_xml_is_directory.ccpn/ccpnv3/memops/Implementation/memops_root_xml_is_directory.xml is not a file it's a directory",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                "memops_root_xml_is_directory",
                discard_beyond="is a possible memops root",
            ),
        ],
    ],
    "GOOD_PROJECT_WITHOUT_ERRORS": [
        "../test_data/good_projects/empty_good_project.ccpn",
        [
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="empty_good_project",
                sub_directory="good_projects",
            ),
            *update_notes(EXPECTED_GOOD_EXO_LINKS),
        ],
    ],
    "GOOD_PROJECT_WITHOUT_ERRORS_RENAMED": [
        "../test_data/good_projects/empty_good_project_renamed.ccpn",
        [
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="empty_good_project_renamed",
                sub_directory="good_projects",
                replace_text={
                    "was probably renamed after saving": "was not renamed after saving"
                },
            ),
            *update_notes(EXPECTED_GOOD_EXO_LINKS),
        ],
    ],
    "MEMOPS_ROOT_READ_PROTECTED_GOOD_PROJECT": [
        "../test_data/memops_root_no_read_empty_good_project.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.NOT_READABLE,
                Path(
                    "memops_root_no_read_empty_good_project.ccpn/ccpnv3/memops/Implementation/memops_root_no_read_empty_good_project.xml"
                ),
                """no xml files which could be memops roots were found in memops_root_no_read_empty_good_project.ccpn/ccpnv3/memops/Implementation
                          with the following extra messages being reported the file memops_root_no_read_empty_good_project.ccpn/ccpnv3/memops/Implementation/memops_root_no_read_empty_good_project.xml is not a valid root xml file and
                          while passing this file i got the following messages:
                          while reading memops_root_no_read_empty_good_project.ccpn/ccpnv3/memops/Implementation/memops_root_no_read_empty_good_project.xml i got the error [Errno 13] Permission denied: 'memops_root_no_read_empty_good_project.ccpn/ccpnv3/memops/Implementation/memops_root_no_read_empty_good_project.xml
                      """,
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                "memops_root_no_read_empty_good_project",
                discard_beyond="is a possible memops root",
            ),
        ],
    ],
    "BAD_MEMOPS_ROOT_XML": [
        "../test_data/bad_memops_root_xml.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.BAD_XML,
                Path(
                    "bad_memops_root_xml.ccpn/ccpnv3/memops/Implementation/bad_memops_root_xml.xml"
                ),
                """no xml files which could be memops roots were found in bad_memops_root_xml.ccpn/ccpnv3/memops/Implementation
                   with the following extra messages being reported the file bad_memops_root_xml.ccpn/ccpnv3/memops/Implementation/bad_memops_root_xml.xml is not a valid root xml file and
                   while passing this file i got the following messages:
                   while xml parsing bad_memops_root_xml.ccpn/ccpnv3/memops/Implementation/bad_memops_root_xml.xml i got the error attributes construct error, line 1, column 36 (<string>, line 1)'
                """,
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="bad_memops_root_xml",
                discard_beyond="is a possible memops root",
            ),
        ],
    ],
    "MEMOPS_ROOT_NO_STORAGE_UNIT": [
        "../test_data/memops_root_no_storage_unit.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.NO_STORAGE_UNIT,
                Path(
                    "memops_root_no_storage_unit.ccpn/ccpnv3/memops/Implementation/memops_root_no_storage_unit.xml"
                ),
                """no xml files which could be memops roots were found in memops_root_no_storage_unit.ccpn/ccpnv3/memops/Implementation
                   with the following extra messages being reported the file memops_root_no_storage_unit.ccpn/ccpnv3/memops/Implementation/memops_root_no_storage_unit.xml is not a valid root xml file and
                   while passing this file i got the following messages:
                   expected storage unit but found NO-StorageUnit at root of memops_root_no_storage_unit.ccpn/ccpnv3/memops/Implementation/memops_root_no_storage_unit.xml""",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="memops_root_no_storage_unit",
                discard_beyond="is a possible memops root",
            ),
        ],
    ],
    "NO_MEMOPS_ROOT_ELEMENT": [
        "../test_data/empty_storage_unit.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.NO_ROOT_OR_TOP_OBJECT,
                Path(
                    "empty_storage_unit.ccpn/ccpnv3/memops/Implementation/empty_storage_unit.xml"
                ),
                """no xml files which could be memops roots were found in empty_storage_unit.ccpn/ccpnv3/memops/Implementation
                with the following extra messages being reported
                the file empty_storage_unit.ccpn/ccpnv3/memops/Implementation/empty_storage_unit.xml is not a valid root xml file and
                while passing this file i got the following messages:
                expected single root element under storage unit, found none
                """,
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="empty_storage_unit",
                discard_beyond="is a possible memops root",
            ),
        ],
    ],
    "ROOT_NOT_MEMOPS_ROOT_ELEMENT": [
        "../test_data/root_not_memops_root_element.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.ROOT_IS_NOT_MEMOPS_ROOT,
                Path(
                    "root_not_memops_root_element.ccpn/ccpnv3/memops/Implementation/root_not_memops_root_element.xml"
                ),
                """no xml files which could be memops roots were found in root_not_memops_root_element.ccpn/ccpnv3/memops/Implementation
                      with the following extra messages being reported
                      the file root_not_memops_root_element.ccpn/ccpnv3/memops/Implementation/root_not_memops_root_element.xml is not a valid root xml file and
                      while passing this file i got the following messages:
                      root_not_memops_root_element.ccpn/ccpnv3/memops/Implementation/root_not_memops_root_element.xml doesn't contain a IMPL.MemopsRoot
                      """,
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="root_not_memops_root_element",
                discard_beyond="is a possible memops root",
            ),
        ],
    ],
    "TOO_MANY_ROOT_ELEMENTS": [
        "../test_data/too_many_root_elements.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.MULTIPLE_ROOT_OR_TOP_OBJECTS_IN_STORAGE_UNIT,
                Path(
                    "too_many_root_elements.ccpn/ccpnv3/memops/Implementation/too_many_root_elements.xml"
                ),
                """'no xml files which could be memops roots were found in too_many_root_elements.ccpn/ccpnv3/memops/Implementation
                      with the following extra messages being reported the file too_many_root_elements.ccpn/ccpnv3/memops/Implementation/too_many_root_elements.xml is not a valid root xml file and
                      while passing this file i got the following messages:
                      expected single root element under storage unit, found 2
                      """,
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="too_many_root_elements",
                discard_beyond="is a possible memops root",
            ),
        ],
    ],
    "NO_EXO_LINKS": [
        "../test_data/no_exo_links.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.NO_EXO_LINKS_FOUND,
                Path("no_exo_links.ccpn/ccpnv3/memops/Implementation/no_exo_links.xml"),
                """no exo links were found in the memops root file no_exo_links.ccpn/ccpnv3/memops/Implementation/no_exo_links.xml""",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT, file_name="no_exo_links"
            ),
            ("analysing exo links", False),
            ("searching for top object exo links, found 0", False),
        ],
    ],
    # 'BASIC_EXO_LINKS_NOT_FOUND': [
    #     "../test_data/basic_exo_links_not_found.ccpn",
    #     [
    #         ErrorData(ErrorCode.BASIC_EXO_LINKS_NOT_FOUND,
    #                   Path('basic_exo_links_not_found.ccpn/ccpnv3/memops/Implementation/basic_exo_links_not_found.xml'),
    #
    #                   ''''in the file memops root file  ../test_data/basic_exo_links_not_found.ccpn/ccpnv3/memops/Implementation/basic_exo_links_not_found.xml
    #                       the following 7 basic exo links are missing:
    #                       GuiTask
    #                       LabelingScheme
    #                       MolSystem
    #                       NmrExpPrototype
    #                       RefSampleComponentStore
    #                       SampleStore
    #                       WindowStore'''
    #                   ),
    #         *update_notes(EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT, file_name='basic_exo_links_not_found'),
    #         ('searching for top object exo links, found 1', False),
    #         ('1. default_user_2024-02-24-15-54-35-583_00001 [type: NmrProject]', True),
    #     ]
    # ],
    "EXO_LINKED_FILE_MISSING": [
        "../test_data/delayed_errors/exo_linked_file_missing.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.EXO_LINKED_FILE_MISSING,
                "default_user_2024-02-24-15-54-35-583_00004",
                """missing top object file for exo link guid default_user_2024-02-24-15-54-35-583_00004""",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_linked_file_missing",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "contents of 8": "contents of 7",
                    "found 8 out of 8": "found 7 out of 8",
                    "8 of the 8": "7 of the 7",
                    "analysed top objects [8]": "analysed top objects [7]",
                    "583_00004 MOLS.MolSystem - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]": "583_00004 MOLS.MolSystem - the file is missing",
                    "analysed linked top objects [8] appear": "analysed linked top objects [7] appear",
                    "checking the exo link keys in 8": "checking the exo link keys in 7",
                    "583_00004 MOLS.MolSystem - all keys are good": "583_00004 MOLS.MolSystem - the file is missing",
                    "ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml":
                    "*file not found*"
                },
                delete=("all the analysed top objects [8]",),
            ),
            (
                "there are 1 missing top object files the list of exo links for the missing files are:",
                False,
            ),
            (
                "1. default_user_2024-02-24-15-54-35-583_00004 MOLS.MolSystem [keys: {'code': 'default'}]",
                True,
            ),
            (
                "empty directories [1] which may be orphaned containers found and listed below [warning]",
                False,
            ),
            (
                "  1. exo_linked_file_missing.ccpn/ccpnv3/ccp/molecule/MolSystem [warning]",
                True,
            ),
        ],
    ],
    "EXO_LINKED_FILE_NOT_VALID_XML": [
        "../test_data/delayed_errors/exo_linked_file_bad_xml.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.BAD_XML,
                "exo_linked_file_bad_xml.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                """could not read the file exo_linked_file_bad_xml.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml because
                       while xml parsing exo_linked_file_bad_xml.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml i got the error attributes construct error, line 1, column 36 (<string>, line 1) """,
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_linked_file_bad_xml",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS, replace_text=BAD_EXO_3_CONTENT_CORRECTIONS
            ),
        ],
    ],
    "EXO_LINKED_FILE_NO_STORAGE_UNIT": [
        "../test_data/delayed_errors/exo_linked_file_no_storage_unit.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.NO_STORAGE_UNIT,
                "exo_linked_file_no_storage_unit.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                """could not read the file exo_linked_file_no_storage_unit.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml because
                         expected storage unit but found _NoStorageUnit at root of exo_linked_file_no_storage_unit.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml
                      """,
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_linked_file_no_storage_unit",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS, replace_text=BAD_EXO_3_CONTENT_CORRECTIONS
            ),
        ],
    ],
    "EXO_LINKED_FILE_NO_TOP_OBJECT": [
        "../test_data/delayed_errors/exo_link_no_top_object.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.NO_ROOT_OR_TOP_OBJECT,
                "exo_link_no_top_object.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                """could not read the file exo_link_no_top_object.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml because
                         expected single root element under storage unit, found none""",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_link_no_top_object",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS, replace_text=BAD_EXO_3_CONTENT_CORRECTIONS
            ),
        ],
    ],
    "EXO_LINKED_FILE_TOO_MANY_TOP_OBJECTS": [
        "../test_data/delayed_errors/exo_link_too_many_top_objects.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.MULTIPLE_ROOT_OR_TOP_OBJECTS_IN_STORAGE_UNIT,
                "exo_link_too_many_top_objects.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                """could not read the file exo_link_too_many_top_objects.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml because
                         expected single root element under storage unit, found 2""",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_link_too_many_top_objects",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS, replace_text=BAD_EXO_3_CONTENT_CORRECTIONS
            ),
        ],
    ],
    "INTERNAL_AND_EXTERNAL_GUIDS_DISAGREE": [
        "../test_data/delayed_errors/external_guid_doesnt_match_internal.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.INTERNAL_AND_EXTERNAL_GUIDS_DISAGREE,
                "external_guid_doesnt_match_internal.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                """the guid in the file default+default_user_2024-02-24-15-54-35-583_00004.xml does not match the guid in the file name
                         file name guid: default_user_2024-02-24-15-54-35-583_00004 MOLS.MolSystem
                         file guid: dummy-internal-guid-for-testing unknown""",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="external_guid_doesnt_match_internal",
                sub_directory="delayed_errors",
            ),
            *update_notes(EXPECTED_GOOD_EXO_LINKS),
        ],
    ],
    "GOOD_PROJECT_EXTRA_XML_FILES": [
        "../test_data/warn_projects/empty_good_project_extra_xml_files.ccpn",
        [
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="empty_good_project_extra_xml_files",
                sub_directory="warn_projects",
            ),
            *update_notes(EXPECTED_GOOD_EXO_LINKS),
            (
                "there are 2 files in the project directory that are not linked to a file by an exo link [warning]",
                False,
            ),
            ("  1. ccp/molecule/MolSystem/molecule2.xml [warning]", True),
            ("  2. ccpnmr/gui/Task/task_2.xml [warning]", True),
            ("checking the contents of 2 detached top objects", False),
            (
                "  1. molecule2 *unknown-package*.*unknown-class* - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]",
                True,
            ),
            (
                "  2. task_2 *unknown-package*.*unknown-class* - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]",
                True,
            ),
            (
                "all the analysed detached top objects [2] appear to have the correct basic structure",
                False,
            ),
        ],
    ],
    "EXO_FILE_NO_PACKAGE_GUID": [
        "../test_data/delayed_errors/exo_file_no_package_guid.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.MISSING_PACKAGE_GUID,
                "exo_file_no_package_guid.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                "the top object has no packageGuid attribute in the element _StorageUnit in the file default+default_user_2024-02-24-15-54-35-583_00004.xml  MOLS.MolSystem",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_file_no_package_guid",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00004 MOLS.MolSystem - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]": "583_00004 MOLS.MolSystem - the top object has no packageGuid attribute in the element _StorageUnit in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem [ERROR]",
                    "all the analysed linked top objects [8] appear to have the correct basic structure": _dedent_all("""only 7 of the 8 analysed top objects appear to have the correct basic structure
                           [see complete errors at the end of the the run for details]"""),
                },
            ),
        ],
    ],
    "EXO_FILE_UNKNOWN_PACKAGE_GUID": [
        "../test_data/delayed_errors/exo_file_unknown_package_guid.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.UNKNOWN_PACKAGE_GUID,
                "exo_file_unknown_package_guid.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                "the package guid www.ccpn.ac.uk_Thompson_2006-08-16-14:22:54_00022 in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem is not recognised",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_file_unknown_package_guid",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00004 MOLS.MolSystem - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]": "583_00004 MOLS.MolSystem - the package guid www.ccpn.ac.uk_Thompson_2006-08-16-14:22:54_00022 in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem is not recognised [ERROR]",
                    "all the analysed linked top objects [8] appear to have the correct basic structure": _dedent_all("""only 7 of the 8 analysed top objects appear to have the correct basic structure
                           [see complete errors at the end of the the run for details]"""),
                },
            ),
        ],
    ],
    "BAD_ROOT_ELEMENT_NAME": [
        "../test_data/delayed_errors/exo_file_bad_root_element_name.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.BAD_ROOT_ELEMENT_NAME,
                "exo_file_bad_root_element_name.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                """the root elements name in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem doesn't have the correct name format
                         it should be of the form <SHORT_PACKAGE_NAME>.<TOP-OBJECT-NAME> but was MOLS-MolSystem""",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_file_bad_root_element_name",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00004 MOLS.MolSystem - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]": _dedent_all("""583_00004 MOLS.MolSystem - the root elements name in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem doesn't have the correct name format
                               it should be of the form <SHORT_PACKAGE_NAME>.<TOP-OBJECT-NAME> but was MOLS-MolSystem"""),
                    "all the analysed linked top objects [8] appear to have the correct basic structure": _dedent_all("""only 7 of the 8 analysed top objects appear to have the correct basic structure
                              [see complete errors at the end of the the run for details]"""),
                },
            ),
        ],
    ],
    "UNKNOWN_SHORT_PACKAGE_NAME": [
        "../test_data/delayed_errors/exo_file_unknown_short_package_name.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.UNKNOWN_SHORT_PACKAGE_NAME,
                "exo_file_unknown_short_package_name.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                """the short package name (GARYT) in the root element of the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem is not recognised""",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_file_unknown_short_package_name",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00004 MOLS.MolSystem - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]": "583_00004 MOLS.MolSystem - the short package name (GARYT) in the root element of the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem is not recognised [ERROR]",
                    "all the analysed linked top objects [8] appear to have the correct basic structure": _dedent_all("""only 7 of the 8 analysed top objects appear to have the correct basic structure
                            [see complete errors at the end of the the run for details]"""),
                },
            ),
        ],
    ],
    "SHORT_NAME_GUID_DOESNT_MATCH_PACKAGE_GUID": [
        "../test_data/delayed_errors/exo_file_short_name_guid_doesnt_match_package_guid.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.SHORT_NAME_GUID_DOESNT_MATCH_PACKAGE_GUID,
                "exo_file_short_name_guid_doesnt_match_package_guid.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                _dedent_all("""the guid for the short name CHEM [www.ccpn.ac.uk_Fogh_2006-08-16-14:22:51_00046]
                                    is not the same as the package guid www.ccpn.ac.uk_Fogh_2006-08-16-14:22:54_00022 [MOLS]
                                    for the root element in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem"""),
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_file_short_name_guid_doesnt_match_package_guid",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00004 MOLS.MolSystem - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]": _dedent_all("""583_00004 MOLS.MolSystem - the guid for the short name CHEM [www.ccpn.ac.uk_Fogh_2006-08-16-14:22:51_00046]
                              is not the same as the package guid www.ccpn.ac.uk_Fogh_2006-08-16-14:22:54_00022 [MOLS]
                              for the root element in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem [ERROR]"""),
                    "all the analysed linked top objects [8] appear to have the correct basic structure": _dedent_all("""only 7 of the 8 analysed top objects appear to have the correct basic structure
                            [see complete errors at the end of the the run for details]"""),
                },
            ),
        ],
    ],
    "EXO_FILE_TIME_ATTRIB_MISSING": [
        "../test_data/delayed_errors/exo_file_time_attrib_missing.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.EXO_FILE_TIME_ATTRIB_MISSING,
                "exo_file_time_attrib_missing.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                "in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem the attribute time is missing in the element _StorageUnit",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_file_time_attrib_missing",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00004 MOLS.MolSystem - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]": _dedent_all(
                        """583_00004 MOLS.MolSystem - in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem the attribute time is missing in the element _StorageUnit [ERROR]"""
                    ),
                    "all the analysed linked top objects [8] appear to have the correct basic structure": _dedent_all("""only 7 of the 8 analysed top objects appear to have the correct basic structure
                            [see complete errors at the end of the the run for details]"""),
                },
            ),
        ],
    ],
    "EXO_FILE_RELEASE_ATTRIB_MISSING": [
        "../test_data/delayed_errors/exo_file_release_attrib_missing.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.EXO_FILE_RELEASE_ATTRIB_MISSING,
                "exo_file_release_attrib_missing.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                "in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem the attribute release is missing in the element _StorageUnit",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_file_release_attrib_missing",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00004 MOLS.MolSystem - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]": _dedent_all(
                        """583_00004 MOLS.MolSystem - in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem the attribute release is missing in the element _StorageUnit [ERROR]"""
                    ),
                    "all the analysed linked top objects [8] appear to have the correct basic structure": _dedent_all("""only 7 of the 8 analysed top objects appear to have the correct basic structure
                            [see complete errors at the end of the the run for details]"""),
                },
            ),
        ],
    ],
    "EXO_FILE_RELEASE_DOESNT_MATCH_ROOT": [
        "../test_data/delayed_errors/exo_file_release_doesnt_match_root.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.EXO_FILE_RELEASE_DOESNT_MATCH_ROOT,
                "exo_file_release_doesnt_match_root.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                _dedent_all("""in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem the model version for the top object
                                    default_user_2024-02-24-15-54-35-583_00004 [0.1.0] is different from root 3.1.0"""),
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_file_release_doesnt_match_root",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00004 MOLS.MolSystem - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]": _dedent_all("""583_00004 MOLS.MolSystem - in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem the model version for the top object
                                          default_user_2024-02-24-15-54-35-583_00004 [0.1.0] is different from root 3.1.0 [ERROR]"""),
                    "all the analysed linked top objects [8] appear to have the correct basic structure": _dedent_all("""only 7 of the 8 analysed top objects appear to have the correct basic structure
                            [see complete errors at the end of the the run for details]"""),
                },
            ),
        ],
    ],
    "EXO_FILE_WRONG_STORAGE_LOCATION": [
        "../test_data/delayed_errors/exo_file_wrong_storage_location.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.EXO_FILE_WRONG_STORAGE_LOCATION,
                "exo_file_wrong_storage_location.ccpn/ccpnv3/ccp/nmr/Nmr/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                _dedent_all("""the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem is not stored in the correct place in the project
                                    it should be store in ccpnv3/ccp/molecule/MolSystem but is stored in ccpnv3/ccp/nmr/Nmr"""),
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_file_wrong_storage_location",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00004 MOLS.MolSystem - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]":
                    _dedent_all("""583_00004 MOLS.MolSystem - the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem is not stored in the correct place in the project
                                   it should be stored in ccpnv3/ccp/molecule/MolSystem but is stored in ccpnv3/ccp/nmr/Nmr [ERROR]"""),
                    "all the analysed linked top objects [8] appear to have the correct basic structure":
                    _dedent_all("""only 7 of the 8 analysed top objects appear to have the correct basic structure
                                   [see complete errors at the end of the the run for details]"""),
                    "MOLS.MolSystem - [PROJECT] ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml":
                    "MOLS.MolSystem - [PROJECT] ccp/nmr/Nmr/default+default_user_2024-02-24-15-54-35-583_00004.xml"
                },
            ),
        ],
    ],
    "EXO_FILE_TIME_ATTRIB_INVALID": [
        "../test_data/delayed_errors/exo_file_time_attrib_invalid.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.EXO_FILE_TIME_ATTRIB_INVALID,
                "exo_file_time_attrib_invalid.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                "in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem the attribute time [wibble] in the element _StorageUnit is not a valid time",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_file_time_attrib_invalid",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00004 MOLS.MolSystem - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]": "583_00004 MOLS.MolSystem - in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem the attribute time [wibble] in the element _StorageUnit is not a valid time [ERROR]",
                    "all the analysed linked top objects [8] appear to have the correct basic structure": _dedent_all("""only 7 of the 8 analysed top objects appear to have the correct basic structure
                            [see complete errors at the end of the the run for details]"""),
                },
            ),
        ],
    ],
    "EXO_FILE_RELEASE_ATTRIB_INVALID": [
        "../test_data/delayed_errors/exo_file_release_attrib_invalid.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.EXO_FILE_RELEASE_ATTRIB_INVALID,
                "exo_file_release_attrib_invalid.ccpn/ccpnv3/ccp/molecule/MolSystem/default+default_user_2024-02-24-15-54-35-583_00004.xml",
                _dedent_all("""in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem the attribute release [3.1a.0]
                                    the attribute release [3.1a.0] is not a valid version number
                                    it should be of the form <major>.<minor>.<patch>
                                    where <major>, <minor>, and <patch> can only contain digits with a possible prepended letter"""),
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_file_release_attrib_invalid",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00004 MOLS.MolSystem - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]": _dedent_all("""583_00004 MOLS.MolSystem - in the file default+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem the attribute release [3.1a.0]
                                          the attribute release [3.1a.0] is not a valid version number
                                          it should be of the form <major>.<minor>.<patch>
                                          where <major>, <minor>, and <patch> can only contain digits with a possible prepended letter [ERROR]"""),
                    "all the analysed linked top objects [8] appear to have the correct basic structure": _dedent_all("""only 7 of the 8 analysed top objects appear to have the correct basic structure
                            [see complete errors at the end of the the run for details]"""),
                },
            ),
        ],
    ],
    "EXO_LINKED_FILE_HAS_WRONG_KEY": [
        "../test_data/delayed_errors/exo_file_key_doesnt_match_root.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.EXO_LINKED_FILE_HAS_WRONG_KEY,
                "exo_file_key_doesnt_match_root.ccpn/ccpnv3/ccp/molecule/MolSystem/wibble+default_user_2024-02-24-15-54-35-583_00004.xml",
                _dedent_all("""in the exo linked file wibble+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem
                                    the key code [index 1] in the original link does not match the key expected key from the filename
                                    key in the file name: default key in the root file contents: wibble
                      """),
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_file_key_doesnt_match_root",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "3. default_user_2024-02-24-15-54-35-583_00004 MOLS.MolSystem - all keys are good": _dedent_all("""3. [key 1] default_user_2024-02-24-15-54-35-583_00004 MOLS.MolSystem - in the exo linked file wibble+default_user_2024-02-24-15-54-35-583_00004.xml MOLS.MolSystem
                                  the key code [index 1] in the original link does not match the key expected key from the filename
                                  key in the file name: default, key in the root file contents: wibble [ERROR]"""),
                    "8 of the 8 keys are good": "7 of the 8 keys are good",
                    "MolSystem/default+default":
                    "MolSystem/wibble+default"

                },
            ),
        ],
    ],
    "BADLY_FORMATTED_ROOT_EXO_LINK": [
        "../test_data/delayed_errors/bad_root_exo_link_element.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.BADLY_FORMATTED_ROOT_EXO_LINK,
                "bad_root_exo_link_element.ccpn/ccpnv3/memops/Implementation/bad_root_exo_link_element.xml",
                "the guid default_user_2024-02-24-15-54-35-583_00006 in the file bad_root_exo_link_element.xml appears to contain a badly formatted exo link",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="bad_root_exo_link_element",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "35-583_00006 GUIT.GuiTask [keys: {{'nameSpace': 'user', 'name': 'View'}}]": "35-583_00006 *unknown-package*.*unknown-class* - exo link detected but is incorrectly defined in root [error]",
                    "583_00006 GUIT.GuiTask - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]": "583_00006 *unknown-package*.*unknown-class* - is ok [saved on: Sat Feb 24 16:16:06 2024 model version: 3.1.0]",
                    "583_00006 GUIT.GuiTask - all keys are good": "583_00006 *unknown-package*.*unknown-class* - all keys are good",
                    "GUIT.GuiTask":
                    "None.None"
                },
            ),
            (
                "Error: the guid default_user_2024-02-24-15-54-35-583_00006 in the file bad_root_exo_link_element.xml appears to contain a badly formatted exo link",
                False,
            ),
        ],
    ],
    "BADLY_FORMATTED_EXO_LINK_0_CHILD_ELEMENTS": [
        "../test_data/delayed_errors/bad_embedded_exo_link_0_child_elements.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.BADLY_FORMATTED_EXO_LINK_KEY_DATA,
                "bad_embedded_exo_link_0_child_elements.ccpn/ccpnv3/memops/Implementation/bad_embedded_exo_link_0_child_elements.xml",
                _dedent_all("""in the file bad_embedded_exo_link_0_child_elements.xml the link REFS.RefSampleComponentStore with guid default_user_2024-02-24-15-54-35-583_00003
                                    has the wrong number of children for key name [0]"""),
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="bad_embedded_exo_link_0_child_elements",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00003 REFS.RefSampleComponentStore [keys: {{'name': 'default'}}]": "583_00003 REFS.RefSampleComponentStore - exo link detected but is incorrectly defined in root [error]"
                },
            ),
            (
                _dedent_all("""in the file bad_embedded_exo_link_0_child_elements.xml the link REFS.RefSampleComponentStore with guid default_user_2024-02-24-15-54-35-583_00003
                           has the wrong number of children for key name [0]"""),
                False,
            ),
        ],
    ],
    "BADLY_FORMATTED_EXO_LINK_0_ELEMENTS": [
        "../test_data/delayed_errors/bad_embedded_exo_link_0_elements.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.BADLY_FORMATTED_EXO_LINK_KEY_DATA,
                "bad_embedded_exo_link_0_elements.ccpn/ccpnv3/memops/Implementation/bad_embedded_exo_link_0_elements.xml",
                _dedent_all("""in the file bad_embedded_exo_link_0_elements.xml in the link REFS.RefSampleComponentStore with guid default_user_2024-02-24-15-54-35-583_00003
                           the key name has the wrong number of children (0) in its main element"""),
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="bad_embedded_exo_link_0_elements",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00003 REFS.RefSampleComponentStore [keys: {{'name': 'default'}}]": "583_00003 REFS.RefSampleComponentStore - exo link detected but is incorrectly defined in root [error]"
                },
            ),
            (
                _dedent_all("""in the file bad_embedded_exo_link_0_elements.xml in the link REFS.RefSampleComponentStore with guid default_user_2024-02-24-15-54-35-583_00003
                           the key name has the wrong number of children (0) in its main element"""),
                False,
            ),
        ],
    ],
    "BADLY_FORMATTED_ROLE_EXO_LINK_KEY_DATA_PARENT": [
        "../test_data/delayed_errors/bad_role_exo_link_key_element_parent.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.BADLY_FORMATTED_ROLE_EXO_LINK_KEY_DATA,
                "bad_role_exo_link_key_element_parent.ccpn/ccpnv3/memops/Implementation/bad_role_exo_link_key_element_parent.xml",
                _dedent_all("""in the file bad_role_exo_link_key_element_parent.xml in the link GUIW.WindowStore with guid default_user_2024-02-24-15-54-35-583_00005
                                    the key element nmrProject doesnt have children"""),
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="bad_role_exo_link_key_element_parent",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00005 GUIW.WindowStore [keys: {{'nmrProject': '_ccp_nmr_Nmr_NmrProject___default___'}}]": "583_00005 GUIW.WindowStore - exo link detected but is incorrectly defined in root [error]"
                },
            ),
            (
                _dedent_all("""in the file bad_role_exo_link_key_element_parent.xml in the link GUIW.WindowStore with guid default_user_2024-02-24-15-54-35-583_00005
                           the key element nmrProject doesnt have children"""),
                False,
            ),
        ],
    ],
    "BADLY_FORMATTED_ROLE_EXO_LINK_KEY_DATA_CHILD": [
        "../test_data/delayed_errors/bad_role_exo_link_key_element_children.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.BADLY_FORMATTED_ROLE_EXO_LINK_KEY_DATA,
                "bad_role_exo_link_key_element_children.ccpn/ccpnv3/memops/Implementation/bad_role_exo_link_key_element_children.xml",
                _dedent_all("""in the file bad_role_exo_link_key_element_children.xml in the link GUIW.WindowStore with guid default_user_2024-02-24-15-54-35-583_00005
                                    the key element nmrProject doesnt have children"""),
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="bad_role_exo_link_key_element_children",
                sub_directory="delayed_errors",
            ),
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00005 GUIW.WindowStore [keys: {{'nmrProject': '_ccp_nmr_Nmr_NmrProject___default___'}}]": "583_00005 GUIW.WindowStore - exo link detected but is incorrectly defined in root [error]"
                },
            ),
            (
                _dedent_all("""in the file bad_role_exo_link_key_element_children.xml in the link GUIW.WindowStore with guid default_user_2024-02-24-15-54-35-583_00005
                           the key element nmrProject doesnt have children"""),
                False,
            ),
        ],
    ],
    "FILE_NAME_HAS_NON_CCPN_ACSII_CHARACTERS": [
        "../test_data/delayed_errors/empty_good_project_with_non_ccpn_letter~.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.NON_CCPN_ASCII_CHARACTER,
                "empty_good_project_with_non_ccpn_letter~.ccpn",
                _dedent_all("""the ccpn project directory name empty_good_project_with_non_ccpn_letter~.ccpn contains characters outside the set [a-zA-Z0-9_] which is not allowed
                         value: empty_good_project_with_non_ccpn_letter~.ccpn
                         ______________________________________________^_____
                      """),
            ),
            ErrorAndWarningData(
                ErrorCode.NON_CCPN_ASCII_CHARACTER,
                "empty_good_project_with_non_ccpn_letter~.xml",
                _dedent_all("""the ccpn root file name empty_good_project_with_non_ccpn_letter~.xml contains characters outside the set [a-zA-Z0-9_] which is not allowed
                      value: empty_good_project_with_non_ccpn_letter~.xml
                      ______________________________________________^____"""),
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="empty_good_project_with_non_ccpn_letter~",
                sub_directory="warn_projects",
            ),
            (
                _dedent_all("""the ccpn project directory name empty_good_project_with_non_ccpn_letter~.ccpn contains characters outside the set [a-zA-Z0-9_] which is not allowed
                            value: empty_good_project_with_non_ccpn_letter~.ccpn
                            ______________________________________________^_____ [error]"""),
                False,
            ),
            (
                _dedent_all("""the ccpn root file name empty_good_project_with_non_ccpn_letter~.xml contains characters outside the set [a-zA-Z0-9_] which is not allowed
                           value: empty_good_project_with_non_ccpn_letter~.xml
                           ______________________________________________^____ [error]"""),
                False,
            ),
            *update_notes(EXPECTED_GOOD_EXO_LINKS),
        ],
    ],
    "GOOD_PROJECT_EXTRA_ROOT_XML_FILES": [
        "../test_data/warn_projects/empty_good_project_extra_root_xml_files.ccpn",
        [
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="empty_good_project_extra_root_xml_files",
                sub_directory="warn_projects",
            ),
            *update_notes(EXPECTED_GOOD_EXO_LINKS, sub_directory="warn_projects"),
            (
                _dedent_all("""more than one possible memops root file found in the implementation directory
                           empty_good_project_extra_root_xml_files.xml
                           empty_good_project_extra_root_xml_files_2.xml
                           [warning]"""),
                False,
            ),
            (
                "the file empty_good_project_extra_root_xml_files_2.xml is a possible orphaned memops root [warning]",
                False,
            ),
        ],
    ],
    "GOOD_PROJECT_MULTIPLE_ROOT_XML_FILES": [
        "../test_data/empty_good_project_multiple_root_xml_files.ccpn",
        [
            ErrorAndWarningData(
                code=ErrorCode.NO_MEMOPS_ROOT_FILES,
                cause="empty_good_project_multiple_root_xml_files.ccpn/ccpnv3/memops/Implementation",
                detail="""no xml files which could be memops roots were found in empty_good_project_multiple_root_xml_files.ccpn/ccpnv3/memops/Implementation
                          with the following extra messages being reported
                          more than one ccpn root file found in empty_good_project_multiple_root_xml_files.ccpn/ccpnv3/memops/Implementation and none match project name
                          roots are:
                          empty_good_project_multiple_root_xml_files.ccpn/ccpnv3/memops/Implementation/empty_good_project_mutiple_root_xml_files_1.xml
                          empty_good_project_multiple_root_xml_files.ccpn/ccpnv3/memops/Implementation/empty_good_project_mutiple_root_xml_files_2.xml""",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="empty_good_project_multiple_root_xml_files",
                discard_beyond="found an implementation directory",
            ),
            # *update_notes(EXPECTED_GOOD_EXO_LINKS),
            (
                _dedent_all("""more than one possible memops root file found in the implementation directory
                empty_good_project_mutiple_root_xml_files_1.xml
                empty_good_project_mutiple_root_xml_files_2.xml
                [warning]"""),
                False,
            ),
            (
                "the file empty_good_project_mutiple_root_xml_files_1.xml is a possible orphaned memops root [warning]",
                False,
            ),
            (
                "the file empty_good_project_mutiple_root_xml_files_2.xml is a possible orphaned memops root [warning]",
                False,
            ),
        ],
    ],
    "ROOT_EXO_LINK_MISSING_SOURCE_ELEMENT": [
        "../test_data/delayed_errors/root_exo_link_missing_source_element.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.EXO_LINK_ELEMENT_SOURCE_MISSING,
                "root_exo_link_missing_source_element.ccpn/ccpnv3/memops/Implementation/root_exo_link_missing_source_element.xml",
                _dedent_all("""in the file root_exo_link_missing_source_element.ccpn/ccpnv3/memops/Implementation/root_exo_link_missing_source_element.xml
                                    link MOLS.MolSystem with guid default_user_2024-02-24-15-54-35-583_00004 is missing its source element"""),
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="root_exo_link_missing_source_element",
            ),
            # TODO: this uses pre template version boo!
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00004 MOLS.MolSystem [keys: {{'code': 'default'}}]": "583_00004 MOLS.MolSystem - exo link detected but is incorrectly defined in root [error]"
                },
            ),
            (
                _dedent_all("""in the file root_exo_link_missing_source_element.ccpn/ccpnv3/memops/Implementation/root_exo_link_missing_source_element.xml
                           link MOLS.MolSystem with guid default_user_2024-02-24-15-54-35-583_00004 is missing its source element [error]"""),
                False,
            ),
        ],
    ],
    "ROOT_EXO_LINK_TOO_MANY_SOURCE_ELEMENTS": [
        "../test_data/delayed_errors/root_exo_link_too_many_source_elements.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.EXO_LINK_ELEMENT_TOO_MANY_SOURCES,
                "root_exo_link_too_many_source_elements.ccpn/ccpnv3/memops/Implementation/root_exo_link_too_many_source_elements.xml",
                _dedent_all("""in the file root_exo_link_too_many_source_elements.ccpn/ccpnv3/memops/Implementation/root_exo_link_too_many_source_elements.xml
                                    link MOLS.MolSystem with guid default_user_2024-02-24-15-54-35-583_00004 has too many link elements [2] there should be 1"""),
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="root_exo_link_too_many_source_elements",
            ),
            # TODO: this uses pre template version boo!
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00004 MOLS.MolSystem [keys: {{'code': 'default'}}]": "583_00004 MOLS.MolSystem - exo link detected but is incorrectly defined in root [error]"
                },
            ),
            (
                _dedent_all("""in the file root_exo_link_too_many_source_elements.ccpn/ccpnv3/memops/Implementation/root_exo_link_too_many_source_elements.xml
                           link MOLS.MolSystem with guid default_user_2024-02-24-15-54-35-583_00004 has too many link elements [2] there should be 1 [error]"""),
                False,
            ),
        ],
    ],
    "WARN_EMPTY_CONTAINERS": [
        "../test_data/warn_projects/empty_good_project_with_empty_containers.ccpn",
        [
            # ErrorData(ErrorCode.WARNING_EMPTY_CONTAINER,
            #           'empty_good_project_with_empty_containers.ccpn',
            #            dedent_all("""in the file root_exo_link_too_many_source_elements.ccpn/ccpnv3/memops/Implementation/root_exo_link_too_many_source_elements.xml
            #                         link MOLS.MolSystem with guid default_user_2024-02-24-15-54-35-583_00004 has too many link elements [2] there should be 1""")),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="empty_good_project_with_empty_containers",
            ),
            *update_notes(EXPECTED_GOOD_EXO_LINKS, replace_text={}),
            (
                "empty directories [2] which may be orphaned containers found and listed below [warning]",
                False,
            ),
            (
                "  1. empty_good_project_with_empty_containers.ccpn/ccpnv3/ccp/molsim/Symmetry [warning]",
                True,
            ),
            (
                "  2. empty_good_project_with_empty_containers.ccpn/ccpnv3/ccp/molecule/LabeledMolecule [warning]",
                True,
            ),
        ],
    ],
    "EXO_LINKS_WITH_KEYS_OUTSIDE_THE_CCPN_CHARACTER_SET": [
        "../test_data/delayed_errors/exo_links_with_keys_outside_ccpn_character_set.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.NON_CCPN_ASCII_CHARACTER,
                ["default_user_2024-02-24-15-54-35-583_00006"],
                _dedent_all("""in the file exo_links_with_keys_outside_ccpn_character_set.ccpn/ccpnv3/memops/Implementation/exo_links_with_keys_outside_ccpn_character_set.xml
                               there are exo link keys [1] which contain characters outside the ccpn character set"""),
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="exo_links_with_keys_outside_ccpn_character_set",
            ),
            # TODO: this uses pre template version boo!
            *update_notes(
                EXPECTED_GOOD_EXO_LINKS,
                replace_text={
                    "583_00006 GUIT.GuiTask [keys: {{'nameSpace': 'user', 'name': 'View'}}]":
                    "583_00006 GUIT.GuiTask [keys: {{'nameSpace': 'user', 'name': 'View~'}}]",
                    "00006 GUIT.GuiTask - [PROJECT] ccpnmr/gui/Task/user+View+default_user_2024-02-24-15-54-35-583_00006.xml":
                    "00006 GUIT.GuiTask - [PROJECT] ccpnmr/gui/Task/user+View~+default_user_2024-02-24-15-54-35-583_00006.xml"
                },
            ),
            (
                _dedent_all("""in the file exo_links_with_keys_outside_ccpn_character_set.ccpn/ccpnv3/memops/Implementation/exo_links_with_keys_outside_ccpn_character_set.xml
                         there are exo link keys [1] which contain characters outside the ccpn character set which are listed below [error]"""),
                False,
            ),
            (
                _dedent_all("""1. [name]. default_user_2024-02-24-15-54-35-583_00006 GUIT.GuiTask  name: View~ [error]
                              key: View~
                              _________^"""),
                False,
            ),
        ],
    ],
    "WARNING_ROOT_FILE_MISSING_TIME_ATTRIBUTE": [
        "../test_data/warn_projects/root_file_missing_time.ccpn",
        [
            # ErrorAndWarningData(
            #     ErrorCode.ROOT_FILE_TIME_ATTRIB_MISSING,
            #     'root_file_missing_time.ccpn/ccpnv3/ccp/Implementation/root_file_missing_time.xml',
            #     'in the file root_file_missing_time.xml the attribute time is missing in the element _StorageUnit'
            #     ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="root_file_missing_time",
                sub_directory="warn_projects",
                replace_text={
                    "memops root data was stored at Sat Feb 24 16:16:06 2024": "in the file root_file_missing_time.xml the attribute time is missing in the element _StorageUnit [warning]"
                },
            ),
            *update_notes(EXPECTED_GOOD_EXO_LINKS),
        ],
    ],
    "WARNING_ROOT_FILE_TIME_ATTRIBUTE_BAD_FORMAT": [
        "../test_data/warn_projects/root_file_badly_formatted_time.ccpn",
        [
            # ErrorAndWarningData(
            #     ErrorCode.ROOT_FILE_TIME_ATTRIB_MISSING,
            #     'root_file_missing_time.ccpn/ccpnv3/ccp/Implementation/root_file_missing_time.xml',
            #     'in the file root_file_missing_time.xml the attribute time is missing in the element _StorageUnit'
            #     ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="root_file_badly_formatted_time",
                sub_directory="warn_projects",
                replace_text={
                    "memops root data was stored at Sat Feb 24 16:16:06 2024": "in the file root_file_badly_formatted_time.xml the attribute time [2024 Sat Feb 24 16:16:06] is badly formatted in the element _StorageUnit [warning]"
                },
            ),
            *update_notes(EXPECTED_GOOD_EXO_LINKS),
        ],
    ],
    "ROOT_VERSION_MISSING": [
        "../test_data/root_version_missing.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.ROOT_MODEL_VERSION_MISSING,
                "root_version_missing.ccpn/ccpnv3/memops/Implementation/root_version_missing.xml",
                "in the file root_version_missing.xml the attribute release is missing in the element _StorageUnit",
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="root_version_missing",
                sub_directory="warn_projects",
                discard_beyond="ccpn project memops root file found in",
            ),
        ],
    ],
    "ROOT_VERSION_BAD_FORMAT": [
        "../test_data/root_version_badly_formatted.ccpn",
        [
            ErrorAndWarningData(
                ErrorCode.ROOT_MODEL_VERSION_BAD,
                "root_version_badly_formatted.ccpn/ccpnv3/memops/Implementation/root_version_badly_formatted.xml",
                _dedent_all("""in the file root_version_badly_formatted.xml the attribute release [a3.1.0]
                              is not a valid version number it should be of the form <major>.<minor>.<patch> where <major>,
                              <minor> can only contain digits and <patch> can contain digits with a possible appended letter
                              can't continue as can't determine model version"""),
            ),
            *update_notes(
                EXPECTED_GOOD_NOTES_READ_MEMOPS_ROOT,
                file_name="root_version_badly_formatted",
                sub_directory="warn_projects",
                discard_beyond="ccpn project memops root file found",
            ),
        ],
    ],
}

TEST_IDS = list(expecteds.keys())

ERROR_CODES_READ_PROTECTED = [
    error_code for error_code in TEST_IDS if "READ_PROTECTED" in error_code
]
ERROR_CODES_NOT_READ_PROTECTED = [
    error_code for error_code in TEST_IDS if "READ_PROTECTED" not in error_code
]
FILES_TO_PROTECT_BY_ERROR_CODE = {
    "READ_PROTECTED_PROJECT": [
        ("no_read_empty_project.ccpn", False),
    ],
    "READ_PROTECTED_CCPNV3": [
        ("no_read_ccpnv3.ccpn/ccpnv3", False),
    ],
    "MEMOPS_ROOT_READ_PROTECTED_GOOD_PROJECT": [
        (
            "memops_root_no_read_empty_good_project.ccpn/ccpnv3/memops/Implementation/memops_root_no_read_empty_good_project.xml",
            False,
        ),
    ],
}
ERROR_CODES_TO_READ_PROTECTED_FILES = {
    ErrorCode.READ_PROTECTED_PROJECT: ("no_read_empty_project.ccpn", False),
    ErrorCode.READ_PROTECTED_CCPNV3: ("no_read_ccpnv3.ccpn/ccpnv3", False),
}

ERRORS_NOT_NEEDING_TEST_SETS = set([ErrorCode.INTERNAL_ERROR, ErrorCode.MISSING_ATTRIB])
