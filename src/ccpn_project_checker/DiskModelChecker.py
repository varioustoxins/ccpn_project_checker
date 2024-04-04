import argparse
import json
import os
import string
import sys
from dataclasses import dataclass
from datetime import datetime
from functools import cache
from time import time
from enum import auto, Enum
from pathlib import Path

from textwrap import dedent

from lxml import etree as ET
from lxml.etree import Element, ETCompatXMLParser

from typing import List, Dict, Any, Tuple, Union

from dateutil import parser as time_parser

from ccpn_project_checker.optional.optional import Optional
from ccpn_project_checker.optional.something import Something

ET_COMPAT_PARSER = ETCompatXMLParser()


class ExitStatus(Enum):
    EXIT_OK = 0  # the project is good
    EXIT_ERROR_INCOMPLETE = 1  # the project is bad enough to halt analysis early
    EXIT_ERROR = 2  # the project is bad
    EXIT_INTERNAL_ERROR = 3  # the run failed and there was an internal error analysis did not complete
    EXIT_WARN = 4  # the project is usable but there are some worry features (orphaned files etc)


NEW_LINE = "\n"


def _dedent_all(lines):
    lines = lines.split("\n")
    lines = [line.strip() for line in lines]
    lines = "\n".join(lines)
    return lines


# copied from ccpn util move to our own util
REPLACEMENT_FILENAME_CHAR = "_"
SEPARATOR_FILENAME_CHAR = "+"
BASIC_VALID_FILENAME_CHARACTERS = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" + REPLACEMENT_FILENAME_CHAR
)
VALID_FILENAME_CHARACTERS = BASIC_VALID_FILENAME_CHARACTERS + "-." + SEPARATOR_FILENAME_CHAR


def _make_valid_ccpn_file_path(path):
    """Replace invalid chars in path to assure Python 2.1 (used in ObjectDomain) compatibility"""
    # used in ApiPath.py
    ll = []
    for ii, char in enumerate(path):
        if char not in VALID_FILENAME_CHARACTERS:
            char = REPLACEMENT_FILENAME_CHAR
        ll.append(char)
    return "".join(ll)


class ErrorCode(Enum):
    MISSING_DIRECTORY = auto()
    IS_NOT_DIRECTORY = auto()
    IS_NOT_FILE = auto()
    NO_MEMOPS_ROOT_FILES = auto()
    NOT_READABLE = auto()
    READ_PROTECTED_PROJECT = auto()
    READ_PROTECTED_CCPNV3 = auto()
    BAD_XML = auto()
    NO_STORAGE_UNIT = auto()
    NO_ROOT_OR_TOP_OBJECT = auto()
    MULTIPLE_ROOT_OR_TOP_OBJECTS_IN_STORAGE_UNIT = auto()
    MULTIPLE_MEMOPS_ROOT_FILES = auto()
    ROOT_IS_NOT_TOP_OBJECT = auto()
    ROOT_IS_NOT_MEMOPS_ROOT = auto()
    ROOT_HAS_NO_MODEL_VERSION = auto()
    NO_EXO_LINKS_FOUND = auto()
    EXO_LINK_ELEMENT_SOURCE_MISSING = auto()
    EXO_LINK_ELEMENT_TOO_MANY_SOURCES = auto()
    # BASIC_EXO_LINKS_NOT_FOUND = auto()
    EXO_LINKED_FILE_MISSING = auto()
    EXO_LINKED_FILE_HAS_WRONG_KEY = auto()
    BADLY_FORMATTED_EXO_LINK_KEY_DATA = auto()
    INTERNAL_AND_EXTERNAL_GUIDS_DISAGREE = auto()
    MISSING_PACKAGE_GUID = auto()
    UNKNOWN_PACKAGE_GUID = auto()
    BAD_ROOT_ELEMENT_NAME = auto()
    UNKNOWN_SHORT_PACKAGE_NAME = auto()
    SHORT_NAME_GUID_DOESNT_MATCH_PACKAGE_GUID = auto()
    EXO_FILE_WRONG_STORAGE_LOCATION = auto()
    MISSING_ATTRIB = auto()  # only used internally
    EXO_FILE_TIME_ATTRIB_MISSING = auto()
    EXO_FILE_TIME_ATTRIB_INVALID = auto()
    EXO_FILE_RELEASE_ATTRIB_MISSING = auto()
    EXO_FILE_RELEASE_ATTRIB_INVALID = auto()
    EXO_FILE_RELEASE_DOESNT_MATCH_ROOT = auto()
    BADLY_FORMATTED_ROOT_EXO_LINK = auto()
    BADLY_FORMATTED_ROLE_EXO_LINK_KEY_DATA = auto()
    INTERNAL_ERROR = auto()
    WARNING_DETACHED_FILES = auto()
    BAD_GUID_FORMAT = auto()
    NON_CCPN_ASCII_CHARACTER = auto()
    WARNING_EMPTY_CONTAINER = auto()
    ROOT_FILE_TIME_ATTRIB_MISSING = auto()
    ROOT_FILE_TIME_ATTRIB_BAD_FORMAT = auto()
    ROOT_MODEL_VERSION_BAD = auto()
    ROOT_MODEL_VERSION_MISSING = auto()


@dataclass
class ExoLinkInfo:
    short_package_name: Union[str, None]
    class_name: Union[str, None]
    keys: Dict[str, str]
    type_guid: Union[str, None]
    key_names: List[str]

    valid: bool = True

    @property
    def short_name(self):
        return f"{self.short_package_name}.{self.class_name}"


# TODO this should be a dataclass
class ObjectInfo:
    def __init__(
        self,
        guid,
        name,
        supertype_guids,
        parent_guid,
        containment,
        keys,
        key_type_guids,
        key_model_types,
        key_defaults,
    ):
        self.guid = guid
        self.name = name
        self.supertype_guids = supertype_guids
        self.supertype_names = []
        self.parent_guid = parent_guid
        self.containment = containment
        self.keys = keys
        self.key_type_guids = key_type_guids
        self.key_model_types = key_model_types
        self.key_types_names = {}
        self.key_defaults = key_defaults

    @classmethod
    def from_storage(cls, object_dict):
        guid = object_dict["guid"]
        name = object_dict["name"]
        supertype_guids = object_dict["supertype_guids"]
        parent_guid = object_dict["parent_guid"]
        containment = object_dict["containment"]
        keys = object_dict["keys"]
        key_type_guids = object_dict["key_type_guids"]
        key_model_types = object_dict["key_model_types"]
        key_defaults = object_dict["key_defaults"]

        return cls(
            guid,
            name,
            supertype_guids,
            parent_guid,
            containment,
            keys,
            key_type_guids,
            key_model_types,
            key_defaults,
        )

    def __repr__(self):
        return f"""TopObjectInfo(
            guid={self.guid},
            name={self.name},
            supertype_guids={self.supertype_guids},
            parent_guid={self.parent_guid},
            containment={self.containment},
            keys={self.keys},
            key_type_guids={self.key_type_guids},
            key_model_types={self.key_model_types},
            key_defaults={self.key_defaults}
        )"""


class BadProjectException(Exception):
    pass


class StorageLocation(Enum):
    PROJECT = auto()
    REFERENCE = auto()


def _check_guid(guid):
    dash_parts = guid.split("_")

    errors = []

    if len(dash_parts) != 4:
        errors.append(
            f"there must be 4 parts separated by _s i got [{len(dash_parts)}]"
        )

    else:
        if not dash_parts[0].isalnum():
            errors.append(f"part 1 must be alphanumeric, i got {dash_parts[0]}")

        if not dash_parts[1].isalnum():
            errors.append(f"part 2 must be alphanumeric, i got {dash_parts[1]}")

        part3_parts = dash_parts[2].split("-")
        if not len(part3_parts) == 6:
            errors.append(
                f"part 3 must have 6 components separated by -s i got {dash_parts[2]}"
            )

        are_numbers = [part.isdigit() for part in part3_parts]
        if not all(are_numbers):
            errors.append(
                f"the components of part 3 must be 6 digits i got {dash_parts[2]}"
            )

        if not dash_parts[-1].isdigit():
            errors.append("part 4 must be digits")

    result = None if len(errors) > 0 else guid
    error_code = ErrorCode.BAD_GUID_FORMAT if len(errors) > 0 else None
    msgs = errors if len(errors) > 0 else None

    return Optional.of(result, error_code, msgs)


def _is_valid_time_format(time_string):
    try:
        datetime.strptime(time_string, "%a %b %d %H:%M:%S %Y")
        result = True
    except Exception:
        result = False

    return result


def _get_guid_time_and_serial(guid):
    dash_parts = guid.split("_")
    part3_parts = dash_parts[2].split("-")
    if len(part3_parts) == 6:
        date_time = datetime.strptime(dash_parts[2], "%Y-%m-%d-%H-%M-%S")
    else:
        date_time = None
    return date_time, int(dash_parts[-1])


def _is_ascii_string(string):
    if not string.isascii():
        messages = []
        lines = string.split("\n")
        for i, line in enumerate(lines, start=1):
            if not line.isascii():
                indicator = ["^" if ord(char) > 127 else "." for char in line]
                if len(lines) == 1:
                    msg = f"""\
                        {line}
                        {indicator}
                    """
                else:
                    msg = f""" \
                        line {i}
                        {line}
                        {indicator}
                    """
                messages.append(msg)
        header = (
            "lines found with non ascii characters"
            if len(lines) > 1
            else "line contains no ascii characters"
        )
        messages = [header, *messages]
        result = Optional.of(messages=messages)
    else:
        result = Optional.of(str)

    return result


def one(targets):
    count = 0
    for target in targets:
        if target:
            count += 1

    return count == 1


def _tree_has_storage_unit(tree):
    root = tree.getroot()
    return isinstance(root, ET.Element) and root.tag == "_StorageUnit"


def _read_file(file_path):
    try:
        with open(file_path, "rb") as fh:
            result = Optional.of(
                fh.read()
            )  # NOTE ET elements do not obey truthiness on validity but maybe containment!
    except Exception as e:
        result = Optional.empty(
            messages=[f"while reading {file_path} i got the error {e}"],
            error_code=ErrorCode.NOT_READABLE,
        )

    return result


def _get_storage_unit(tree, file_path):
    if tree:
        tree = tree.get()

        if tree.tag == "_StorageUnit":
            result = Something(
                tree, Optional
            )  # NOTE ET elements do not obey truthiness on validity but maybe containment!
        else:
            result = Optional.empty(
                messages=[
                    f"expected storage unit but found {tree.tag} at root of {file_path}"
                ],
                error_code=ErrorCode.NO_STORAGE_UNIT,
            )
    else:
        result = tree

    return result


def _parse_xml(file_text, file_path):
    if file_text:
        file_text = file_text.get()

        try:
            tree = ET.fromstring(file_text, parser=ET_COMPAT_PARSER)
            result = Something(tree, Optional)

        except Exception as e:
            message = f"while xml parsing {file_path} i got the error {e}"
            result = Optional.of(messages=[message], error_code=ErrorCode.BAD_XML)
    else:
        result = file_text

    return result


def _get_single_root(storage_unit):
    if storage_unit:
        storage_unit = storage_unit.get()

        roots = [elem for elem in storage_unit]
        if len(roots) == 0:
            result = Optional.empty(
                messages=[
                    "expected single root element under storage unit, found none"
                ],
                error_code=ErrorCode.NO_ROOT_OR_TOP_OBJECT,
            )
        elif len(roots) == 1:
            result = Something(roots[0], Optional)
        else:
            result = Optional.empty(
                messages=[
                    f"expected single root element under storage unit, found {len(roots)}"
                ],
                error_code=ErrorCode.MULTIPLE_ROOT_OR_TOP_OBJECTS_IN_STORAGE_UNIT,
            )
    else:
        result = storage_unit

    return result


@cache
def _get_root_element(file_path):
    tree = _read_tree(file_path)
    storage_unit = _get_storage_unit(tree, file_path)
    root = _get_single_root(storage_unit)

    return root, storage_unit


def _read_tree(file_path):
    text = _read_file(file_path)
    tree = _parse_xml(text, file_path)
    return tree


def _get_parent_path(path, count=1):
    for i in range(count):
        path = path.parent
    return path


def _get_data_dir():
    resolved_path = Path(__file__).resolve()
    ccpn_base = _get_parent_path(resolved_path, 4)

    return ccpn_base / "ccpnmodel" / "data" / "ccpnv3"


@dataclass
class ObjectIdentifier:
    storage_location: StorageLocation
    containment: List[str]
    keys: List[str]
    guid: str
    path: Union[Path, None] = None

    def exists(self):
        return self.path is not None


@dataclass(frozen=True)
class ErrorAndWarningData:
    code: ErrorCode
    cause: Any
    detail: str
    is_warning: bool = False

    def __str__(self):
        type_ = "error" if not self.is_warning else "warning"
        result = f"""\
            {type_} [{self.code.name}]
            cause: {str(self.cause)}
            message 
            {self.detail}
        """
        return result


class ModelChecker:
    def __init__(self, warnings_are_errors=False):
        self._warnings_are_errors = warnings_are_errors
        self._start_time = 0.0
        self._end_time = 0.0
        self._model_version = None
        self.messages: List[Tuple[str, bool]] = []
        self.errors: List[ErrorAndWarningData] = []
        self.warnings: List[ErrorAndWarningData] = []
        self.internal_error = False
        self.stop_error = False

        self._guid_to_storage_location = None
        self._object_info_map = None
        self._short_package_name_to_guid = None

    def _get_attrib(self, storage_unit, attrib_name, source):
        error_code = None
        msgs = []
        cause = None
        if attrib_name in storage_unit.attrib:
            result = storage_unit.attrib[attrib_name]
        else:
            result = None
            msg = f"""
                    couldn't find the attribute {attrib_name} in the storage unit {storage_unit.tag}
                    the source of the storage unit was {source}
                """
            msgs = [msg]
            error_code = ErrorCode.MISSING_ATTRIB
            cause = storage_unit

        return Optional.of(result, msgs, error_code, cause)

    def _error_if_name_is_outside_ccpn_letter_set(
        self, value, param, is_filename=False, extras="", suffixes=None
    ):
        in_ccpn_letter_set = self._name_is_in_ccpn_letter_set(
            value, is_filename, extras, suffixes
        )

        ccpn_short_character_set = "a-zA-Z0-9_" + extras

        stem, suffix = self._get_file_and_suffix(value)

        if not in_ccpn_letter_set:
            pointers = self._highlight_letters_outside_ccpn_character_set(
                stem, suffix, extras
            )

            msg = f"""\
                the {param} {value} contains characters outside the set [{ccpn_short_character_set}] which is not allowed
                value: {value}
                _______{pointers}"""
            msg = _dedent_all(msg)
            self._report_error(ErrorCode.NON_CCPN_ASCII_CHARACTER, value, msg)
            self._add_note(f"{msg} [error]")

    def _highlight_letters_outside_ccpn_character_set(
        self, stem="", suffix="", extras=""
    ):
        ccpn_character_set = VALID_FILENAME_CHARACTERS + extras

        pointers = []
        for letter in stem:
            if letter not in ccpn_character_set:
                pointers.append("^")
            else:
                pointers.append("_")
        pointers.append("_" * len(suffix))
        return "".join(pointers)

    def _get_file_and_suffix(self, file_path, suffixes=None):
        file_path = Path(file_path)
        suffix = file_path.suffix
        if not suffixes or suffix in suffixes:
            stem = file_path.stem
            suffix = file_path.suffix
        else:
            stem = file_path
            suffix = ""

        return stem, suffix

    def _name_is_in_ccpn_letter_set(self, target, is_filename, extras="", suffixes=()):
        ccpn_character_set = BASIC_VALID_FILENAME_CHARACTERS + extras

        if is_filename:
            target, suffix = self._get_file_and_suffix(target, suffixes)

        result = set(str(target)).issubset(ccpn_character_set)
        # raise Exception(result, target, ccpn_character_set)
        return result

    def _load_json_file_or_raise_exception(self, file_path):
        try:
            with open(file_path, "r") as fh:
                result = json.loads(fh.read())
        except Exception as e:
            raise Exception(
                f"INTERNAL ERROR: while reading {file_path} i got the error {e}"
            )

        return result

    def _info_path(self):
        return Path(__file__).parent / "model_info"

    def _load_model_info(self):
        if not self._model_version:
            raise Exception(
                "INTERNAL ERROR: model version not set, can't proceed further"
            )

        model_version = self._model_version.replace(".", "_")
        model_version = f"v_{model_version}"

        self._guid_to_storage_location = self._load_json_file_or_raise_exception(
            self._info_path() / f"{model_version}_guid_to_storage_location.json"
        )
        self._object_info_map = self._load_json_file_or_raise_exception(
            self._info_path() / f"{model_version}_object_info.json"
        )
        self._object_info_map = self._load_object_info(self._object_info_map)
        self._short_package_name_to_guid = self._load_json_file_or_raise_exception(
            self._info_path() / f"{model_version}_short_name_to_guid.json"
        )
        self._guid_to_short_name = {
            value: key for key, value in self._short_package_name_to_guid.items()
        }
        self._short_object_name_to_guid = self._build_object_name_to_guid()

    def _build_object_name_to_guid(self):
        object_name_to_guid = {}
        for guid, object_info in self._object_info_map.items():
            object_name = object_info.name
            package_guid = object_info.parent_guid
            package_short_name = self._guid_to_short_name[package_guid]
            short_object_name = f"{package_short_name}.{object_name}"
            object_name_to_guid[short_object_name] = guid
        return object_name_to_guid

    def run(self, project_path):
        project_path = Path(project_path)

        self._start_time = time()
        try:
            self._add_note(f"target {project_path}")

            project_name = self._get_project_name(project_path)
            self._add_note(f"project_name appears to be... {project_name}")

            self._error_if_name_is_outside_ccpn_letter_set(
                project_path.parts[-1],
                "ccpn project directory name",
                is_filename=True,
                suffixes=[".ccpn"],
            )

            project_dir = Path(project_path)
            project_dir = self._get_readable_directory_or_exit(project_dir)

            self._note_if_project_doesnt_end_with_suffix_ccpn(project_dir)

            model_directory = project_dir / "ccpnv3"
            model_directory = self._get_readable_directory_or_exit(model_directory)

            implementation_directory = model_directory / "memops" / "Implementation"
            implementation_directory = self._get_readable_directory_or_exit(
                implementation_directory
            )

            implementation_directory_relative = (
                self._get_relative_root_implementation_directory(
                    implementation_directory
                )
            )
            self._add_note(
                f"found an implementation directory {str(implementation_directory_relative)}"
            )

            memops_root_file_path = self._get_memops_root_file_path_or_exit(
                implementation_directory, project_name
            )

            memops_root_file_path_relative = (
                self._get_relative_root_implementation_directory(memops_root_file_path)
            )

            self._add_note(
                f"ccpn project memops root file found in {str(memops_root_file_path_relative)}"
            )

            self._error_if_name_is_outside_ccpn_letter_set(
                memops_root_file_path_relative.parts[-1],
                "ccpn root file name",
                is_filename=True,
                suffixes=[".xml"],
            )

            # self._note_if_path_is_non_ascii(memops_root_file_path)
            #
            # self._note_if_file_has_non_ascii_characters(memops_root_file_path)

            self._note_key_model_information(memops_root_file_path)

            self._load_model_info()

            exo_links = self._analyze_project_root_exo_links(memops_root_file_path)

            self._check_if_exo_link_keys_outside_ccpn_character_set(
                exo_links, memops_root_file_path
            )

            self._exit_if_no_memops_root_exo_links(exo_links, memops_root_file_path)

            # self._exit_if_basic_exo_links_missing(exo_links, memops_root_file_path)

            project_top_object_identifiers, reference_top_object_identifiers = (
                self._get_top_object_file_identifiers(model_directory)
            )

            all_identifiers = {
                **project_top_object_identifiers,
                **reference_top_object_identifiers,
            }
            matched_top_objects = self._match_exolinks_with_files(
                exo_links, all_identifiers
            )

            files_with_no_exolinks = self._match_files_with_no_exo_links(
                exo_links,
                project_top_object_identifiers,
                memops_root_file_path_relative,
            )

            self._check_for_empty_containers(model_directory)

            self._note_if_there_are_detached_files(files_with_no_exolinks)

            self._note_if_there_are_missing_exo_links(exo_links, matched_top_objects)

            self._note_top_object_paths(exo_links, matched_top_objects)

            # self._note_if_project_files_paths_not_ascii(project_top_object_identifiers.values(),
            #                                             model_directory)

            # do this on other found files as well but don't exit error
            self._check_if_top_object_guid_matches_external(
                matched_top_objects, model_directory, exo_links
            )

            self._check_matched_top_objects_hierarchy_and_contents(
                matched_top_objects.values(), model_directory, exo_links, linked=True
            )

            self._check_matched_top_object_keys(
                matched_top_objects, exo_links, model_directory
            )

            if files_with_no_exolinks:
                self._check_matched_top_objects_hierarchy_and_contents(
                    files_with_no_exolinks, model_directory, exo_links, linked=False
                )

        except BadProjectException:
            pass
        except Exception as e:
            import traceback

            traceback_text = traceback.format_exc()

            msg = f"""\
            {traceback_text}
            
            there was an internal error str({e}) see traceback above """

            self._report_error(ErrorCode.INTERNAL_ERROR, __file__, msg)
            self.internal_error = True
            self.stop_error = True

        self._end_time = time()
        self._note_runtime()

        if self.internal_error:
            result = ExitStatus.EXIT_INTERNAL_ERROR
        elif not self.errors and not self.warnings:
            result = ExitStatus.EXIT_OK
        elif self.errors:
            if self.stop_error:
                result = ExitStatus.EXIT_ERROR_INCOMPLETE
            else:
                result = ExitStatus.EXIT_ERROR
        elif self.warnings:
            result = ExitStatus.EXIT_WARN

        else:
            result = ExitStatus.EXIT_INTERNAL_ERROR

        return result

    def _check_if_exo_link_keys_outside_ccpn_character_set(
        self, exo_links, project_root_file_path
    ):
        bad_keys = []
        for i, (guid, exo_link_info) in enumerate(exo_links.items()):
            for j, (key_name, key) in enumerate(exo_link_info.keys.items()):
                if not self._name_is_in_ccpn_letter_set(key, False):
                    short_name = exo_link_info.short_name
                    pointers = self._highlight_letters_outside_ccpn_character_set(key)
                    bad_keys.append((guid, short_name, key_name, key, pointers, j))

        if bad_keys:
            msg = f"""\
                in the file {project_root_file_path}
                there are exo link keys [{len(bad_keys)}] which contain characters outside the ccpn character set"""
            msg = _dedent_all(msg)
            guids = [bad_key[0] for bad_key in bad_keys]
            self._report_error(ErrorCode.NON_CCPN_ASCII_CHARACTER, guids, msg)

            self._add_note(f"{msg} which are listed below [error]")
            for i, (guid, short_name, key_name, key, pointers, key_index) in enumerate(
                bad_keys, start=1
            ):
                msg = f"""\
                    {i:>3}. [{key_name}]. {guid} {short_name}  {key_name}: {key} [error]
                    key: {key}
                    _____{pointers}"""
                msg = _dedent_all(msg)
                self._add_note(msg)

    def _check_for_empty_containers(self, model_directory):
        empty_containers = []
        for dir_path, dir_names, file_names in os.walk(model_directory):
            xml_file_names = [
                file_name for file_name in file_names if file_name.endswith(".xml")
            ]
            if not dir_names and not xml_file_names:
                empty_containers.append(dir_path)

        if empty_containers:
            msg = f"empty directories [{len(empty_containers)}] which may be orphaned containers found and listed below [warning]"
            self._add_note(msg)
            for i, empty_container in enumerate(empty_containers, start=1):
                msg = f"possibly empty_container found at {empty_container}"
                self._report_warning(
                    ErrorCode.WARNING_EMPTY_CONTAINER, empty_container, msg
                )
                self._add_note(f"{i:>3}. {empty_container} [warning]", True)

    def _note_runtime(self):
        self._add_note()
        self._add_note(
            f"analysis took {self._end_time - self._start_time:4.3f} seconds"
        )

    def _get_top_object_file_identifiers(self, model_directory):
        reference_data_files, project_exo_files = self._get_project_and_ref_data_files(
            model_directory
        )
        project_top_object_identifiers = self._files_to_object_identifiers(
            project_exo_files, StorageLocation.PROJECT
        )
        reference_top_object_identifiers = self._files_to_object_identifiers(
            reference_data_files, StorageLocation.REFERENCE
        )
        return project_top_object_identifiers, reference_top_object_identifiers

    def _get_memops_root_file_path_or_exit(
        self, implementation_directory, project_name
    ):
        memops_root_file_path = self._get_memops_root_file_path(
            implementation_directory, project_name
        )
        if not memops_root_file_path:
            msg = f"""no xml files which could be memops roots were found in {implementation_directory} """
            if memops_root_file_path.messages:
                msg = f"""\
                      {msg}
                      with the following extra messages being reported {NEW_LINE.join(memops_root_file_path.messages)}
                """
                msg = dedent(msg)
            cause = (
                memops_root_file_path.cause
                if memops_root_file_path.cause
                else implementation_directory
            )
            error_code = (
                memops_root_file_path.error_code
                if memops_root_file_path.error_code
                else (ErrorCode.NO_MEMOPS_ROOT_FILES)
            )
            self._report_stop_error(error_code, cause, msg)

        return memops_root_file_path.get()

    def _get_readable_directory_or_exit(self, directory_path: Path) -> Path:
        readable_directory = self._get_readable_directory(directory_path)

        if not readable_directory:
            self._report_stop_error(
                readable_directory.error_code,
                directory_path,
                "".join(readable_directory.messages),
            )

        return readable_directory.get()

    @staticmethod
    def _get_readable_directory(directory_path: Path):
        msgs = []
        error_code = None
        if not directory_path.exists():
            msg = f"the directory {directory_path} doesn't exist"
            error_code = ErrorCode.MISSING_DIRECTORY
            msgs.append(msg)

        if not msgs and not directory_path.is_dir():
            msg = (
                f"the path {directory_path} should be a directory, it isn't, its a file"
            )

            error_code = ErrorCode.IS_NOT_DIRECTORY
            msgs.append(msg)

        if (not msgs) and (not os.access(directory_path, os.R_OK)):
            msg = f"the path {directory_path} is not readable"
            error_code = ErrorCode.NOT_READABLE
            msgs.append(msg)

        result = directory_path if error_code is None else None

        return Optional.of(result, messages=msgs, error_code=error_code)

    def _note_if_project_doesnt_end_with_suffix_ccpn(self, project_dir):
        if not project_dir.suffix == ".ccpn":
            msg = f"""\
                ccpn project directories should have the suffix .ccpn the directory {project_dir.parts[-1]} doesn't 
            """
        else:
            msg = f"""\
                the directory {project_dir.parts[-1]} has the correct suffix
            """
        msg = dedent(msg)
        return self._add_note(msg)

    @staticmethod
    def _find_project_name_in_paths(project_file_path, xml_file_paths):
        check = [xml_file_path == project_file_path for xml_file_path in xml_file_paths]
        return one(check)

    def _get_memops_root_file_path(
        self, implementation_directory: Path, project_name: str
    ):
        xml_file_paths = [
            child
            for child in implementation_directory.iterdir()
            if child.suffix == ".xml"
        ]
        if len(xml_file_paths) == 0:
            result = Optional.empty(
                messages=[f"no root xml file found in {implementation_directory}"]
            )
        else:
            project_file_name = f"{project_name}.xml"

            if len(xml_file_paths) >= 1:
                root_file_names = [
                    xml_file_path.parts[-1] for xml_file_path in xml_file_paths
                ]
                root_file_names = sorted(root_file_names)

                if len(xml_file_paths) > 1:
                    msg = f"""\
                    more than one possible memops root file found in the implementation directory
                    {NEW_LINE.join(root_file_names)}"""
                    msg = _dedent_all(msg)

                    xml_file_paths = sorted(xml_file_paths)
                    self._report_warning(
                        ErrorCode.MULTIPLE_MEMOPS_ROOT_FILES, xml_file_paths, msg
                    )
                    self._add_note(f"{msg}\n[warning]", False)

                for xml_file_path in xml_file_paths:
                    if xml_file_path.parts[-1] == project_file_name:
                        self._add_note(
                            f"the path {xml_file_path} is a possible memops root [name matches project]",
                            False,
                        )
                    else:
                        self._report_warning(
                            ErrorCode.MULTIPLE_MEMOPS_ROOT_FILES,
                            implementation_directory,
                            msg,
                        )
                        self._add_note(
                            f"the file {xml_file_path.parts[-1]} is a possible orphaned memops root [warning]",
                            False,
                        )

                root_files = self._get_memops_root_files(xml_file_paths)

                if root_files:
                    root_files = root_files.get()
                    project_path = implementation_directory / project_file_name
                    project = self._find_project_name_in_paths(project_path, root_files)
                    if project:
                        result = Optional.of(project_path)
                        self._add_note(
                            f"The project in {project_file_name}, was not renamed after saving"
                        )

                    elif not project and len(root_files) == 1:
                        root_path = root_files[0]
                        result = Optional.of(root_path)
                        self._add_note(
                            f"The project in {project_file_name}, was probably renamed after saving"
                        )

                    else:
                        all_relative_roots = [
                            str(
                                self._get_relative_root_implementation_directory(
                                    root_path
                                )
                            )
                            for root_path in root_files
                        ]
                        msg = f"""
                            more than one ccpn root file found in {implementation_directory} and none match project name
                            roots are:
                            {NEW_LINE.join(all_relative_roots)}
                        """
                        result = Optional.empty(messages=[msg])
                else:
                    if len(xml_file_paths) == 1:
                        message = f"""\
                            the file {xml_file_paths[0]} is not a valid root xml file and 
                            while passing this file i got the following messages:
                            {NEW_LINE.join(root_files.messages)}
                        """
                        cause = xml_file_paths[0]
                    else:
                        message = f"""\
                        no valid root xml file found in the implementation directory:
                        {implementation_directory}
                        but when passing some of the files in the implementation directory i got the following messages:
                        {NEW_LINE.join(root_files.messages)}
                        """
                        cause = xml_file_paths
                    message = dedent(message)
                    result = Optional.empty(
                        messages=[message],
                        error_code=root_files.error_code,
                        cause=cause,
                    )
            else:
                result = Optional.empty(
                    messages=[f"no xml files found in {implementation_directory}"]
                )

        return result

    def _get_memops_root_files(self, xml_file_paths):
        messages = []
        root_file_paths = []
        error = None
        cause = None
        for xml_file_path in xml_file_paths:
            if xml_file_path.suffix == ".xml" and xml_file_path.is_dir():
                self._report_stop_error(
                    ErrorCode.IS_NOT_FILE,
                    xml_file_path,
                    f"{xml_file_path} is not a file it's a directory",
                )

            root, _ = _get_root_element(xml_file_path)

            if root:
                root = root.get()
                if root.tag == "IMPL.MemopsRoot":
                    root_file_paths.append(xml_file_path)
                else:
                    error = ErrorCode.ROOT_IS_NOT_MEMOPS_ROOT
                    cause = xml_file_path
                    messages.append(
                        f"{xml_file_path} doesn't contain a IMPL.MemopsRoot"
                    )
            elif root.messages:
                error = root.error_code if not error else error
                cause = xml_file_path if error else None
                messages.extend(root.messages)

        return Optional.of(
            root_file_paths, messages=messages, error_code=error, cause=cause
        )

    @staticmethod
    def _get_project_name(project_dir_path):
        project_name = Path(project_dir_path).parts[-1]
        if project_name.endswith(".ccpn"):
            project_name = project_name[:-5]

        return project_name

    @staticmethod
    def _get_relative_root_implementation_directory(target_path_string):
        target_path = Path(target_path_string)
        if target_path.is_dir():
            result = Path(*target_path.parts[-4:])
        else:
            result = Path(*target_path.parts[-5:])
        return result

    def _find_model_data_files(self, data_directory):
        files = []
        if data_directory.exists():
            for elem in os.walk(data_directory):
                for file_name in elem[-1]:
                    if not file_name.endswith(".xml"):
                        continue
                    file_path = Path(elem[0], file_name)
                    files.append(file_path.relative_to(data_directory))
        else:
            with open(self._info_path() / "data_file_names.txt") as fh:
                files = [Path(file_name) for file_name in fh.readlines()]
            self._add_note(
                "using v3.1.0 cached data files from 25/03/2024 in stand alone mode"
            )

        return files

    def _analyze_project_root_exo_links(self, project_root_file_path):
        # TODO should cache these results
        with open(project_root_file_path, "rb") as f:
            file = f.read()
        root = ET.fromstring(file, parser=ET_COMPAT_PARSER)
        soup = Element("root")
        soup.append(root)

        proto_exo_links = soup.findall(".//IMPL.GuidString")

        exo_links_to_types = {}
        for proto_exo_link in proto_exo_links:
            # TODO: add tests for guid format
            # exo_link_guid = proto_exo_link.text
            exo_link_guid = proto_exo_link.text
            #TODO: add the check that the first part of the name is exo?
            try:
                exo_link_parent = proto_exo_link.getparent()

                if exo_link_parent is not None:
                    exo_link_type = exo_link_parent.tag.split(".")
                    if len(exo_link_type) != 2:
                        raise Exception()
                    exo_link_type = exo_link_type[-1]
                    exo_link_type = exo_link_type.split("-")
                    if len(exo_link_type) != 2:
                        raise Exception()
                    exo_link_type = exo_link_type[-1]

                    short_package = exo_link_parent.tag.split(".")
                    if len(short_package) != 2:
                        raise Exception()
                    short_package = short_package[0]

            except Exception:
                exo_link_type = None
                short_package = None

                msg = f"the guid {exo_link_guid} in the file {project_root_file_path.parts[-1]} appears to contain a badly formatted exo link"
                self._report_error(
                    ErrorCode.BADLY_FORMATTED_ROOT_EXO_LINK, project_root_file_path, msg
                )
                self._add_note(f"Error: {msg}")

            exo_links_to_types[exo_link_guid] = (short_package, exo_link_type)

        exo_link_keys = {}
        guid_to_object_info = {}
        role_exo_link_keys = set()
        self._add_note(
            f"searching for top object exo links, found {len(exo_links_to_types)}"
        )

        self._add_note("analysing exo links")
        for i, (guid, (short_package, type_)) in enumerate(
            exo_links_to_types.items(), start=1
        ):
            if short_package is None or type_ is None:
                continue

            link_name = f"{short_package}.{type_}"
            link = soup.findall(f'.//{link_name}[@guid="{guid}"]')

            num_links = len(link)
            if num_links == 0:
                msg = f"""\
                in the file {project_root_file_path}
                link {link_name} with guid {guid} is missing its source element"""
                msg = _dedent_all(msg)
                self._report_error(
                    ErrorCode.EXO_LINK_ELEMENT_SOURCE_MISSING,
                    project_root_file_path,
                    msg,
                )
                self._add_note(f"{msg} [error]")
                continue
            elif len(link) > 1:
                msg = f"""\
                      in the file {project_root_file_path}
                      link {link_name} with guid {guid} has too many link elements [{num_links}] there should be 1"""
                msg = _dedent_all(msg)
                self._report_error(
                    ErrorCode.EXO_LINK_ELEMENT_TOO_MANY_SOURCES,
                    project_root_file_path,
                    msg,
                )
                self._add_note(f"{msg} [error]")
                continue

            link = link[0]

            object_name = f"{short_package}.{type_}"
            top_object_guid = self._short_object_name_to_guid[object_name]
            top_object_info = self._object_info_map[top_object_guid]
            guid_to_object_info[guid] = top_object_info
            keys = top_object_info.keys
            key_model_types = top_object_info.key_model_types
            key_type_guids = top_object_info.key_type_guids

            key_values = {}
            exo_link_keys[guid] = key_values
            for key in keys:
                if key in link.attrib:
                    key_value = link.attrib[key]
                elif key in top_object_info.key_defaults:
                    key_value = top_object_info.key_defaults[key]
                elif key_model_types[key] == "MetaRole":
                    key_value = self._build_role_key(
                        guid,
                        key,
                        key_type_guids,
                        link,
                        link_name,
                        project_root_file_path,
                    )

                    role_exo_link_keys.add((guid, key))

                else:
                    key_value = self._build_embedded_attribute_key(
                        guid,
                        key,
                        key_type_guids,
                        link,
                        link_name,
                        project_root_file_path,
                    )

                key_type_guid = top_object_info.key_type_guids[key]
                key_class = (
                    self._object_info_map[key_type_guid].name
                    if key_type_guid in self._object_info_map
                    else None
                )
                if key_class:
                    key_value = (
                        _make_valid_ccpn_file_path(key_value)
                        if key_value and key_class == "Line"
                        else key_value
                    )

                key_values[key] = key_value

        self._format_exo_link_role_keys(
            exo_link_keys, exo_links_to_types, role_exo_link_keys
        )

        for i, (guid, (short_package, type_)) in enumerate(
            exo_links_to_types.items(), start=1
        ):
            short_package = (
                "*unknown-package*" if short_package is None else short_package
            )
            type_ = "*unknown-class*" if type_ is None else type_
            short_name = f"{short_package}.{type_}"
            exo_link_key_for_guid = (
                exo_link_keys[guid] if guid in exo_link_keys else None
            )
            if guid in exo_link_keys and None not in exo_link_key_for_guid.values():
                msg = f"{i:>3}. {guid} {short_name} [keys: {exo_link_key_for_guid}]"
            else:
                msg = f"{i:>3}. {guid} {short_name} - exo link detected but is incorrectly defined in root [error]"
            self._add_note(msg, no_prefix=True)

        result = {}
        for guid in exo_links_to_types:
            item_exo_link_short_package, item_exo_link_type = (
                exo_links_to_types[guid] if guid in exo_links_to_types else (None, None)
            )
            item_exo_link_keys = exo_link_keys[guid] if guid in exo_link_keys else {}
            valid = item_exo_link_short_package != (None, None)
            object_info = (
                guid_to_object_info[guid] if guid in guid_to_object_info else None
            )
            object_guid = object_info.guid if object_info else None
            key_names = object_info.keys if object_info else []

            result[guid] = ExoLinkInfo(
                item_exo_link_short_package,
                item_exo_link_type,
                item_exo_link_keys,
                object_guid,
                key_names,
                valid=valid,
            )

        return result

    def _format_exo_link_role_keys(
        self, exo_link_keys, exo_links_to_types, role_exo_link_keys
    ):
        for guid, key in role_exo_link_keys:
            role_key_guid = exo_link_keys[guid][key]
            if role_key_guid in exo_links_to_types:
                role_short_object_name = ".".join(exo_links_to_types[role_key_guid])
                role_object_guid = self._short_object_name_to_guid[
                    role_short_object_name
                ]
                role_object_info = self._object_info_map[role_object_guid]
                role_exo_link_keys = exo_link_keys[role_key_guid]

                role_containment = "_".join(
                    [*role_object_info.containment, role_object_info.name]
                )
                exo_role_keys = [
                    role_exo_link_keys[key] for key in role_object_info.keys
                ]
                exo_role_keys = "__".join(exo_role_keys)
                exo_role_keys = f"__{exo_role_keys}__"
                full_key = f"_{role_containment}_{exo_role_keys}_"
            else:
                full_key = None

            exo_link_keys[guid][key] = full_key

    def _build_embedded_attribute_key(
        self, guid, key, key_type_guids, links, link_name, project_root_file_path
    ):
        key_type_guid = key_type_guids[key]
        key_object_info = self._object_info_map[key_type_guid]
        key_type_name = key_object_info.name
        key_object_package_guid = key_object_info.parent_guid
        key_object_package_short_name = self._guid_to_short_name[
            key_object_package_guid
        ]
        key_object_name = f"{key_object_package_short_name}.{key_type_name}"
        child_name = f"{link_name}.{key}"
        elems = [elem for elem in links if elem.tag == child_name]
        num_elems = len(elems)

        ok = True
        if num_elems != 1:
            msg = f"""\
                    in the file {project_root_file_path.parts[-1]} in the link {link_name} with guid {guid}
                    the key {key} has the wrong number of children ({num_elems}) in its main element"""
            msg = _dedent_all(msg)
            self._report_error(
                ErrorCode.BADLY_FORMATTED_EXO_LINK_KEY_DATA, project_root_file_path, msg
            )
            self._add_note(msg)
            ok = False

        elem = elems[0] if ok else None
        elem_children = (
            [child for child in elem if child.tag == key_object_name] if ok else []
        )
        num_elem_children = len(elem_children)

        if ok and num_elem_children != 1:
            msg = f"""\
                    in the file {project_root_file_path.parts[-1]} the link {link_name} with guid {guid}
                    has the wrong number of children for key {key} [{num_elem_children}]"""
            msg = _dedent_all(msg)
            self._report_error(
                ErrorCode.BADLY_FORMATTED_EXO_LINK_KEY_DATA, project_root_file_path, msg
            )
            self._add_note(msg)
            ok = False

        elem_key_child = elem_children[0] if ok else None
        key_value = elem_key_child.text if ok else None

        return key_value

    def _build_role_key(
        self, guid, key, key_type_guids, link, link_name, project_root_file_path
    ):
        # key_object_name = f'{link.name}.{key}'
        key_object_name = f"{link.tag}.{key}"

        key_object = link.find(f".//{key_object_name}")
        key_type_guid = key_type_guids[key]
        key_object_info = self._object_info_map[key_type_guid]
        key_type_name = key_object_info.name
        key_object_package_guid = key_object_info.parent_guid
        key_object_package_short_name = self._guid_to_short_name[
            key_object_package_guid
        ]

        key_object_name_exo = f"{key_object_package_short_name}.exo-{key_type_name}"
        key_object_values = key_object.findall(f".//{key_object_name_exo}")
        num_elems = len(key_object_values)

        ok = True
        if num_elems < 1:
            # NOT CURRENTLY POSSIBLE TO TEST THIS
            msg = f"""\
                in the file {project_root_file_path.parts[-1]} in the link {link_name} with guid {guid}
                the key {key} has no children in its main element"""
            msg = _dedent_all(msg)
            self._report_error(
                ErrorCode.BADLY_FORMATTED_ROLE_EXO_LINK_KEY_DATA,
                project_root_file_path,
                msg,
            )
            self._add_note(msg)
            ok = False
        elif num_elems > 1:
            msg = f"""\
                in the file {project_root_file_path.parts[-1]} in the link {link_name} with guid {guid}
                the key {key} has the wrong number of children ({num_elems}) in its main element it should be 1"""
            msg = _dedent_all(msg)
            self._report_error(
                ErrorCode.BADLY_FORMATTED_ROLE_EXO_LINK_KEY_DATA,
                project_root_file_path,
                msg,
            )
            self._add_note(msg)
            ok = False

        key_object_value = key_object_values[0]

        elem_key_child = key_object_value.find(".//IMPL.GuidString") if ok else None

        if elem_key_child is None:
            msg = f"""\
                in the file {project_root_file_path.parts[-1]} in the link {link_name} with guid {guid}
                the key element {key} doesnt have children"""
            msg = _dedent_all(msg)
            self._report_error(
                ErrorCode.BADLY_FORMATTED_ROLE_EXO_LINK_KEY_DATA,
                project_root_file_path,
                msg,
            )
            self._add_note(msg)
            ok = False

        key_value = elem_key_child.text if ok else None

        return key_value

    def _get_project_and_ref_data_files(self, project_root_directory):
        data_dir = _get_data_dir()
        ccpn_reference_data_files = self._find_model_data_files(data_dir)

        project_files = self._find_model_data_files(project_root_directory)

        return ccpn_reference_data_files, project_files

    @staticmethod
    def _files_to_object_identifiers(
        file_paths: List[Path], storage_location: StorageLocation
    ) -> Dict[str, ObjectIdentifier]:
        result = {}
        for file_path in file_paths:
            *keys, guid_xml = file_path.parts[-1].split("+")
            guid = guid_xml.split(".")[0]
            containment = file_path.parts[:-1]
            result[guid] = ObjectIdentifier(
                storage_location, list(containment), keys, guid, file_path
            )

        return result

    @staticmethod
    def _match_exolinks_with_files(exo_links, top_object_identifiers):
        result = {}
        for exo_link_guid in exo_links:
            result.setdefault(exo_link_guid, None)
            if exo_link_guid in top_object_identifiers:
                result[exo_link_guid] = top_object_identifiers[exo_link_guid]
            else:
                result[exo_link_guid] = ObjectIdentifier(
                    StorageLocation.PROJECT, [], [], exo_link_guid
                )

        return result

    # def _note_if_path_is_non_ascii(self, file_path):
    #
    #     file_path_is_ascii = _is_ascii_string(str(file_path))
    #     if not file_path_is_ascii:
    #         msg = \
    #             f'''
    #             the file path
    #             {str(file_path)}
    #             contains non ascii characters:
    #
    #             {NEW_LINE.join(file_path_is_ascii.messages)}
    #         '''
    #         self.add_note(msg)

    # TODO: check for excaped xml characters...
    def _note_if_file_has_non_ascii_characters(self, file_path):
        with open(file_path) as fh:
            memops_root_lines = fh.read()
            memops_root_contents_are_ascii = _is_ascii_string(memops_root_lines)
            if not memops_root_contents_are_ascii:
                msg = f"""
                    the contents of the memops root file
                    {file_path}
                    are not ascii
                    
                    {NEW_LINE.join(memops_root_contents_are_ascii)}
                """
                self._add_note(msg)

    # def _note_if_project_files_paths_not_ascii(self, object_identifiers, model_root_directory):
    #     for object_identifier in object_identifiers:
    #         if not object_identifier or object_identifier.storage_location == StorageLocation.REFERENCE:
    #             continue
    #
    #         if relative_path := object_identifier.path:
    #             full_path = model_root_directory / relative_path
    #             self._note_if_path_is_non_ascii(relative_path)
    #             self._note_if_file_has_non_ascii_characters(full_path)

    def _check_if_top_object_guid_matches_external(
        self, matched_top_objects, model_root_directory, exo_links
    ):
        for object_identifier in matched_top_objects.values():
            if (
                not object_identifier.exists()
                or object_identifier.storage_location == StorageLocation.REFERENCE
            ):
                continue

            full_path = model_root_directory / object_identifier.path
            tree, _ = _get_root_element(full_path)

            if tree:
                tree = tree.get()
                file_name_short = (
                    exo_links[object_identifier.guid].short_name
                    if object_identifier.guid in exo_links
                    else "unknown"
                )
                file_guid_short = (
                    exo_links[tree.attrib["guid"]].short_name
                    if tree.attrib["guid"] in exo_links
                    else "unknown"
                )
                if not tree.attrib["guid"] == object_identifier.guid:
                    msg = f"""
                        the guid in the file {object_identifier.path.parts[-1]} does not match the guid in the file name
                        file name guid: {object_identifier.guid} {file_name_short}
                        file guid: {tree.attrib['guid']} {file_guid_short}
                    """
                    self._report_error(
                        ErrorCode.INTERNAL_AND_EXTERNAL_GUIDS_DISAGREE, full_path, msg
                    )
            else:
                # error_msg =
                error_code = (
                    tree.error_code if tree.error_code else ErrorCode.NOT_READABLE
                )
                msg = f"""\
                    could not read the file {full_path} because
                    {NEW_LINE.join(tree.messages)}  
                """
                self._report_error(error_code, full_path, msg)

    def _note_if_there_are_missing_exo_links(self, exo_links, matched_top_objects):
        count = sum(
            [1 for guid in matched_top_objects if matched_top_objects[guid].exists()]
        )

        exo_link_count = len(exo_links)
        missing_count = exo_link_count - count
        self._add_note(
            f"found {count} out of {len(exo_links)} top object files exo linked by the project"
        )

        if missing_count:
            msg = f"there are {missing_count} missing top object files the list of exo links for the missing files are:"
            msg = dedent(msg)
            self._add_note(msg)
            missing_top_object_guids = [
                guid
                for guid in matched_top_objects
                if not matched_top_objects[guid].exists()
            ]
            # add key parsing and predict full filenames...
            for i, guid in enumerate(missing_top_object_guids, start=1):
                exo_link_info = exo_links[guid]
                keys = exo_link_info.keys
                self._add_note(
                    f"{i}. {guid} {exo_link_info.short_name} [keys: {keys}]",
                    no_prefix=True,
                )

                self._report_error(
                    ErrorCode.EXO_LINKED_FILE_MISSING,
                    guid,
                    f"missing top object file for exo link guid {guid}",
                )

    @staticmethod
    def _match_files_with_no_exo_links(
        exo_links, file_identifiers, memops_root_file_path
    ):
        result = []
        exo_link_guids = exo_links.keys()
        for file_identifier in file_identifiers.values():
            # discount files in memops root directory they are not detached exolinked files they are extra roots
            if file_identifier.path.parts[:-1] == memops_root_file_path.parts[-3:-1]:
                continue

            if file_identifier.guid not in exo_link_guids:
                result.append(file_identifier)
        return result

    def _note_if_there_are_detached_files(self, files_with_no_exolinks):
        if len(files_with_no_exolinks) > 0:
            num_files = len(files_with_no_exolinks)
            # TODO this could be neater
            msg = f"""\
                there are {num_files} files in the project directory that are not linked to a file by an exo link [warning]
                """
            msg = dedent(msg)
            self._add_note(msg)

            for i, file_identifier in enumerate(files_with_no_exolinks, start=1):
                msg = f"the file {file_identifier.path} is not linked to a file by an exo link"
                self._report_warning(
                    ErrorCode.WARNING_DETACHED_FILES, file_identifier.path, msg
                )
                self._add_note(
                    f"{i:>3}. {file_identifier.path} [warning]", no_prefix=True
                )

    def _report_error(self, code: ErrorCode, cause: object, details: str):
        details = "\n".join([detail.lstrip() for detail in details.split("\n")])
        self.errors.append(ErrorAndWarningData(code, cause, details))

    def _report_stop_error(self, code: ErrorCode, cause: object, details: str):
        self._report_error(code, cause, details)
        self.stop_error = True
        raise BadProjectException()

    def _report_warning(self, code: ErrorCode, cause: object, details: str):
        if self._warnings_are_errors:
            self._report_error(code, cause, details)
        else:
            details = "\n".join([detail.lstrip() for detail in details.split("\n")])
            self.warnings.append(
                ErrorAndWarningData(code, cause, details, is_warning=True)
            )

    def _add_note(self, msg: str = "", no_prefix=False):
        self.messages.append((msg.rstrip(), no_prefix))

    def _exit_if_no_memops_root_exo_links(self, exo_links, memops_root_file_path):
        if len(exo_links) == 0:
            msg = f"""\
                no exo links were found in the memops root file {memops_root_file_path}
            """
            self._report_stop_error(
                ErrorCode.NO_EXO_LINKS_FOUND, memops_root_file_path, msg
            )

    # I don't think we can do this...?
    # def _exit_if_basic_exo_links_missing(self, exo_links, memops_root_file_path):
    #     expected_types = ['GuiTask', 'LabelingScheme', 'MolSystem', 'NmrExpPrototype',
    #                       'NmrProject', 'RefSampleComponentStore', 'SampleStore', 'WindowStore']
    #     missing = [type_ for type_ in expected_types if type_ not in exo_links.values()]
    #     if missing:
    #         msg = f'''\
    #             in the file memops root file  {memops_root_file_path}
    #             the following {(len(missing))} basic exo links are missing:
    #             {NEW_LINE.join(missing)}
    #         '''
    #         self._report_stop_error(ErrorCode.BASIC_EXO_LINKS_NOT_FOUND, memops_root_file_path, msg)

    def _note_key_model_information(self, project_root_file_path):
        # TODO: read with optionsl code and cache and other equivalents
        with open(project_root_file_path, "rb") as f:
            file = f.read()
        root = ET.fromstring(file, parser=ET_COMPAT_PARSER)
        soup = Element("root")
        soup.append(root)

        # model version
        # TODO: check StorageUnit is under root
        storage_unit = soup.findall(".//_StorageUnit")[0]
        model_version = (
            storage_unit.attrib["release"] if "release" in storage_unit.attrib else None
        )

        if not model_version:
            msg = f"in the file {project_root_file_path.parts[-1]} the attribute release is missing in the element {storage_unit.tag}"
            self._report_stop_error(
                ErrorCode.ROOT_MODEL_VERSION_MISSING, project_root_file_path, msg
            )

        version_ok = self._check_version_format(model_version)
        if not version_ok:
            msg = f"""in the file {project_root_file_path.parts[-1]} the attribute release [{model_version}]
                             is not a valid version number it should be of the form <major>.<minor>.<patch> where <major>, 
                             <minor> can only contain digits and <patch> can contain digits with a possible appended letter
                             can't continue as can't determine model version"""
            msg = _dedent_all(msg)
            self._report_stop_error(
                ErrorCode.ROOT_MODEL_VERSION_BAD, project_root_file_path, msg
            )

        self._add_note(
            f"model version that saved this file appears to be {model_version}", False
        )
        self._model_version = model_version

        storage_time = (
            storage_unit.attrib["time"] if "time" in storage_unit.attrib else None
        )
        storage_time_format_ok = storage_time and _is_valid_time_format(storage_time)
        # TODO check we have a model version and that it's a valid one
        if storage_time and storage_time_format_ok:
            self._add_note(f"memops root data was stored at {storage_time}")
        elif not storage_time:
            msg = f"in the file {project_root_file_path.parts[-1]} the attribute time is missing in the element {storage_unit.tag}"
            self._report_warning(
                ErrorCode.ROOT_FILE_TIME_ATTRIB_MISSING, project_root_file_path, msg
            )
            self._add_note(f"""{msg} [warning]""")
        elif not storage_time_format_ok:
            msg = f"in the file {project_root_file_path.parts[-1]} the attribute time [{storage_time}] is badly formatted in the element {storage_unit.tag}"
            self._report_warning(
                ErrorCode.ROOT_FILE_TIME_ATTRIB_BAD_FORMAT, project_root_file_path, msg
            )
            self._add_note(f"""{msg} [warning]""")

        # program version
        object_version = soup.findall(".//IMPL.DataObject._objectVersion")
        version = object_version[0].findall(".//IMPL.String")

        if len(version) == 0 or len(version) > 0 and not version[0].text:
            msg = f"no ccpnmr program version information found in the memops root file {project_root_file_path}"
            self._report_stop_error(
                ErrorCode.ROOT_HAS_NO_MODEL_VERSION, project_root_file_path, msg
            )
        else:
            msg = f"ccpnmr program version that saved this file appears to be {version[0].text.strip()}"
            self._add_note(msg, False)

    def _check_matched_top_objects_hierarchy_and_contents(
        self, matched_top_objects, model_directory, exo_links, linked
    ):
        linked = "linked" if linked else "detached"
        active_objects = [obj for obj in matched_top_objects if obj.exists()]
        num_active_objects = len(active_objects)
        self._add_note()
        msg = f"""checking the contents of {num_active_objects} {linked} top objects"""
        self._add_note(msg)

        num_good = 0
        for i, object_identifier in enumerate(matched_top_objects, start=1):
            guid = object_identifier.guid

            exo_link = exo_links[guid] if guid in exo_links else None
            if not exo_link:
                exo_link = ExoLinkInfo(None, None, {}, None, [], valid=False)
            short_name = (
                "*unknown-package*.*unknown-class*"
                if exo_link.short_name == "None.None"
                else exo_link.short_name
            )

            if not object_identifier.exists():
                msg = f"""{i:>3}. {guid} {short_name} - the file is missing"""
                self._add_note(msg, no_prefix=True)
                continue

            if object_identifier.storage_location == StorageLocation.REFERENCE:
                msg = f"""{i:>3}. {guid} {short_name} - is ok [reference object assumed good (further analysis skipped)]"""
                self._add_note(msg, no_prefix=True)
                num_good += 1
                continue

            file_path = Path(model_directory) / object_identifier.path

            tree, storage_unit = _get_root_element(file_path)

            if not tree:
                msg = f"""{i:>3}. {guid} {short_name} - xml is bad skipped [see errors at the end of the run for details]"""
                self._add_note(msg, no_prefix=True)
                continue

            tree = tree.get()
            storage_unit = storage_unit.get()

            # check it exists first
            package_guid = self._get_attrib(storage_unit, "packageGuid", file_path)
            if not package_guid:
                msg = f"the top object has no packageGuid attribute in the element {storage_unit.tag} in the file {file_path.parts[-1]} {short_name}"
                self._report_error(ErrorCode.MISSING_PACKAGE_GUID, file_path, msg)
                self._add_note(f"""{i:>3}. {guid} {short_name} - {msg} [ERROR]""", True)
                continue

            package_guid = package_guid.get()

            if package_guid in self._guid_to_storage_location:
                package_path = self._guid_to_storage_location[package_guid]
            else:
                msg = f"the package guid {package_guid} in the file {file_path.parts[-1]} {short_name} is not recognised"
                self._report_error(ErrorCode.UNKNOWN_PACKAGE_GUID, file_path, msg)
                self._add_note(f"""{i:>3}. {guid} {short_name} - {msg} [ERROR]""", True)
                continue

            tag_parts = tree.tag.split(".")

            if len(tag_parts) != 2:
                msg = _dedent_all(f"""the root elements name in the file {file_path.parts[-1]} {short_name} doesn't have the correct name format
                                     it should be of the form <SHORT_PACKAGE_NAME>.<TOP-OBJECT-NAME> but was {tree.tag}""")
                self._report_error(ErrorCode.BAD_ROOT_ELEMENT_NAME, file_path, msg)
                self._add_note(f"""{i:>3}. {guid} {short_name} - {msg}""", True)
                continue

            short_package_name, type_ = tag_parts
            # TODO: not tested
            # if tree.tag != short_name:
            #     msg = f"""the root element name in the file {file_path.parts[-1]} {short_name}
            #               is not the same as the short package name [{short_name}]"""
            #     msg = dedent_all(msg)
            #     self._report_error(ErrorCode.ROOT_ELEMENT_NAME_DOESNT_MATCH_SHORT_NAME, file_path, msg)
            #     self.add_note(f'''{i:>3}. {guid} {short_name} - {msg} [ERROR]''', True)
            #     continue

            if short_package_name not in self._short_package_name_to_guid:
                msg = f"the short package name ({short_package_name}) in the root element of the file {file_path.parts[-1]} {short_name} is not recognised"
                self._report_error(ErrorCode.UNKNOWN_SHORT_PACKAGE_NAME, file_path, msg)
                self._add_note(f"""{i:>3}. {guid} {short_name} - {msg} [ERROR]""", True)
                continue
            short_name_guid = self._short_package_name_to_guid[short_package_name]

            if short_name_guid != package_guid:
                msg = f"""the guid for the short name {short_package_name} [{short_name_guid}] 
                          is not the same as the package guid {package_guid} [{self._guid_to_short_name[package_guid]}] 
                          for the root element in the file {file_path.parts[-1]} {short_name}"""
                msg = _dedent_all(msg)
                self._report_error(
                    ErrorCode.SHORT_NAME_GUID_DOESNT_MATCH_PACKAGE_GUID, file_path, msg
                )
                self._add_note(f"""{i:>3}. {guid} {short_name} - {msg} [ERROR]""", True)
                continue

            # not really fatal could be a warning
            storage_time = self._get_attrib(storage_unit, "time", file_path)
            if not storage_time:
                msg = f"in the file {file_path.parts[-1]} {short_name} the attribute time is missing in the element {storage_unit.tag}"
                self._report_error(
                    ErrorCode.EXO_FILE_TIME_ATTRIB_MISSING, file_path, msg
                )
                self._add_note(f"""{i:>3}. {guid} {short_name} - {msg} [ERROR]""", True)
                continue
            else:
                storage_time = storage_time.get()

            try:
                time_parser.parse(storage_time)
            except Exception:
                msg = f"in the file {file_path.parts[-1]} {short_name} the attribute time [{storage_time}] in the element {storage_unit.tag} is not a valid time"
                self._report_error(
                    ErrorCode.EXO_FILE_TIME_ATTRIB_INVALID, file_path, msg
                )
                self._add_note(f"""{i:>3}. {guid} {short_name} - {msg} [ERROR]""", True)
                continue

            storage_release = self._get_attrib(storage_unit, "release", file_path)
            if not storage_release:
                msg = f"in the file {file_path.parts[-1]} {short_name} the attribute release is missing in the element {storage_unit.tag}"
                self._report_error(
                    ErrorCode.EXO_FILE_RELEASE_ATTRIB_MISSING, file_path, msg
                )
                self._add_note(f"""{i:>3}. {guid} {short_name} - {msg} [ERROR]""", True)
                continue
            else:
                storage_release = storage_release.get()

            storage_release_version_ok = self._check_version_format(storage_release)
            if not storage_release_version_ok:
                msg = f"""in the file {file_path.parts[-1]} {short_name} the attribute release [{storage_release}]
                          the attribute release [{storage_release}] is not a valid version number
                          it should be of the form <major>.<minor>.<patch>
                          where <major>, <minor>, and <patch> can only contain digits with a possible prepended letter"""
                msg = _dedent_all(msg)
                self._report_error(
                    ErrorCode.EXO_FILE_RELEASE_ATTRIB_INVALID, file_path, msg
                )
                self._add_note(f"""{i:>3}. {guid} {short_name} - {msg} [ERROR]""", True)
                continue

            if storage_release != self._model_version:
                msg = f"""in the file {file_path.parts[-1]} {short_name} the model version for the top object
                           {guid} [{storage_release}] is different from root {self._model_version}"""
                msg = _dedent_all(msg)
                self._report_error(
                    ErrorCode.EXO_FILE_RELEASE_DOESNT_MATCH_ROOT, file_path, msg
                )
                self._add_note(f"""{i:>3}. {guid} {short_name} - {msg} [ERROR]""", True)
                continue

            containment_correct = object_identifier.containment == package_path
            if not containment_correct:
                msg = f"""\
                the file {file_path.parts[-1]} {short_name} is not stored in the correct place in the project
                it should be stored in ccpnv3/{'/'.join(package_path)} but is stored in ccpnv3/{'/'.join(object_identifier.containment)}"""
                msg = _dedent_all(msg)
                self._report_error(
                    ErrorCode.EXO_FILE_WRONG_STORAGE_LOCATION, file_path, msg
                )
                self._add_note(f"""{i:>3}. {guid} {short_name} - {msg} [ERROR]""", True)
                continue

            storage_release = storage_release.replace("_", ".")

            msg = f"""{i:>3}. {guid} {short_name} - is ok [saved on: {storage_time} model version: {storage_release}]"""
            self._add_note(msg, no_prefix=True)
            num_good += 1

        if num_good == num_active_objects:
            self._add_note(
                f"all the analysed {linked} top objects [{num_good}] appear to have the correct basic structure"
            )
        else:
            msg = f"""\
            only {num_good} of the {num_active_objects} analysed top objects appear to have the correct basic structure 
            [see complete errors at the end of the the run for details]
            """
            self._add_note(_dedent_all(msg))

    def _check_version_format(self, storage_release):
        storage_release_parts = storage_release.split(".")
        num_release_parts = len(storage_release_parts)
        storage_release_version_ok = True

        if num_release_parts != 3:
            storage_release_version_ok = False

        if storage_release_version_ok and len(storage_release_parts[-1]) > 0:
            last_part = storage_release_parts[-1]
            storage_release_version_ok = True

        if storage_release_version_ok:
            last_part = last_part.rstrip(string.ascii_letters)
            num_remaining_characters = len(last_part)
            if num_remaining_characters == 0:
                storage_release_version_ok = False

        if storage_release_version_ok:
            if last_part.isdigit():
                storage_release_version_ok = True

        for part in storage_release_parts[:-1]:
            if not len(part) > 0:
                storage_release_version_ok = False
                break
            if not part.isdigit():
                storage_release_version_ok = False
                break

        return storage_release_version_ok

    def _load_object_info(self, _top_object_info_map):
        return {
            guid: ObjectInfo.from_storage(object_dict)
            for guid, object_dict in _top_object_info_map.items()
        }

    def _check_matched_top_object_keys(
        self, matched_top_objects, exo_links, model_directory
    ):
        active_objects = [obj for obj in matched_top_objects.values() if obj.exists()]
        num_active_objects = len(active_objects)

        self._add_note()
        self._add_note(
            f"checking the exo link keys in {num_active_objects} top object file names"
        )

        good_object_count = 0
        for i, (guid, object_info) in enumerate(matched_top_objects.items(), start=1):
            if not object_info.exists():
                self._add_note(
                    f"{i:>3}. {guid} {exo_links[guid].short_name} - the file is missing",
                    no_prefix=True,
                )
                continue

            ok = True
            exo_link_info = exo_links[guid]
            short_name = exo_link_info.short_name

            key_names = exo_link_info.key_names
            bad_key_number = 1
            for j, key_name in enumerate(key_names):
                file_name_key = exo_link_info.keys[key_name]
                file_contents_key = object_info.keys[j]

                if file_name_key is not None and (file_name_key != file_contents_key):
                    msg = f"""\
                    in the exo linked file {object_info.path.parts[-1]} {short_name}
                    the key {key_name} [index {j+1}] in the original link does not match the key expected key from the filename 
                    key in the file name: {file_name_key}, key in the root file contents: {file_contents_key}"""
                    msg = _dedent_all(msg)
                    self._report_error(
                        ErrorCode.EXO_LINKED_FILE_HAS_WRONG_KEY,
                        Path(model_directory, object_info.path),
                        msg,
                    )
                    self._add_note(
                        f"""{i:>3}. [key {j + 1}] {guid} {short_name} - {msg} [ERROR]""",
                        True,
                    )
                    bad_key_number += 1
                    ok = False
            if ok:
                short_name = (
                    "*unknown-package*.*unknown-class*"
                    if short_name == "None.None"
                    else short_name
                )
                self._add_note(
                    f"{i:>3}. {guid} {short_name} - all keys are good", no_prefix=True
                )
                good_object_count += 1

        self._add_note(f"{good_object_count} of the {num_active_objects} keys are good")

    def _note_top_object_paths(self, exo_links, matched_top_objects):
        self._add_note('expected top object paths are:')
        for i, guid in enumerate(exo_links, start=1):
            if guid in matched_top_objects:
                short_name = exo_links[guid].short_name
                location= matched_top_objects[guid].storage_location.name
                file_path = matched_top_objects[guid].path
                if file_path:
                    self._add_note(f'{i:>3}. {guid} {short_name} - [{location}] {file_path}', True)
                else:
                    self._add_note(f'{i:>3}. {guid} {short_name} - [{location}] *file not found*', True)


def _display_notes(checker):
    print(file=sys.stderr)

    global_indent = ""
    for message, no_prefix in checker.messages:
        if "[error]" in message.lower() or "[warning]" in message.lower():
            global_indent = "   "
            break

    for message, no_prefix in checker.messages:
        if message == "":
            print(file=sys.stderr)
            continue
        else:
            prefix = "NOTE: " if not no_prefix else "  "
            if "[error]" in message.lower():
                indent = "*E "
            elif "[warning]" in message.lower():
                indent = "*W "
            else:
                indent = global_indent

            message_parts = message.split("\n")
            extra_indent = ""
            if (
                len(message_parts) > 1
                and message_parts[0].lstrip(" ")[0] in string.digits
            ):
                indented_message_0 = (
                    message_parts[0]
                    .lstrip(" ")
                    .lstrip(string.digits)
                    .lstrip(".")
                    .lstrip(" ")
                )
                extra_indent = " " * (len(message_parts[0]) - len(indented_message_0))

            for i, message_part in enumerate(message_parts):
                active_extra_indent = extra_indent if i > 0 else ""
                print(
                    f"{indent}{prefix}{active_extra_indent}{message_part}",
                    file=sys.stderr,
                )


def _display_fatal_error(error_data: ErrorAndWarningData):
    if error_data:
        msg = f"""\
            STOP! there was a fatal error while analysing the project
            
            error code: {error_data.code.name}
            caused by: {error_data.cause}
            detailed message:
            {error_data.detail}
        """.rstrip()

        msg = dedent(msg)
        max_length = max([len(line) for line in msg.split("\n")])
        print(file=sys.stderr)
        print("*" * max_length, file=sys.stderr)
        print(msg, file=sys.stderr)
        print("*" * max_length, file=sys.stderr)


def _indent_all(msg, indent=3):
    SPACE = " "
    return "\n".join([f"{SPACE*indent}{line}" for line in msg.split("\n")])


def _display_errors(checker, type_="ERRORS"):
    if type_ == "ERRORS":
        source = checker.errors
    elif type_ == "WARNINGS":
        source = checker.warnings
    else:
        print(f"unknown type {type_} for errors or warnings", file=sys.stderr)
        source = None

    if source:
        note_stars = ""
        for message, _ in checker.messages:
            if "[error]" in message.lower() or "[warning]" in message.lower():
                note_stars = (
                    f" - see items with *{type_[0]}s in the margin above for further context"
                )
                break

        print(file=sys.stderr)
        num_items = len(checker.errors) if type_ == "ERRORS" else len(checker.warnings)
        print(f"{type_} [{num_items}]:{note_stars}", file=sys.stderr)
        print(file=sys.stderr)

        for i, data in enumerate(source, start=1):
            msg = f"{i:>3}. code: {data.code.name}"

            msg2 = f"""\
                caused by: {data.cause}
                detailed message: {data.detail.strip()} 
            """
            msg = _dedent_all(msg)
            msg2 = _indent_all(_dedent_all(msg2))
            print(msg, file=sys.stderr)
            print(msg2, file=sys.stderr)

    if checker.stop_error and type_ == "ERRORS":
        print(file=sys.stderr)
        print(
            f"NOTE: the last error [{len(checker.errors)}] prevented a complete analysis of the project",
            file=sys.stderr,
        )


def run_checker(file_path, warnings_are_errors=False):
    checker = ModelChecker(warnings_are_errors=warnings_are_errors)

    return checker.run(file_path), checker


def run_cli_checker(file_path=None, warnings_are_errors=False):
    if not file_path:
        args = _parse_args()
        warnings_are_errors = args.warnings_are_errors
        file_path = args.project_path[0]

    exit_status, checker = run_checker(file_path, warnings_are_errors)

    exit_status_message = {
        ExitStatus.EXIT_OK: "The project was ok",
        ExitStatus.EXIT_ERROR: "There was an error in the project that would prevent it loading",
        ExitStatus.EXIT_ERROR_INCOMPLETE: "There was an error [the last one listed] in the project that prevented complete processing",
        ExitStatus.EXIT_INTERNAL_ERROR: "There was an internal error in the project checker, please see the traceback and report this to ccpn!",
        ExitStatus.EXIT_WARN: "The project was ok and is use able but there were some warnings",
    }

    _display_notes(checker)
    _display_errors(checker, type_="ERRORS")
    _display_errors(checker, type_="WARNINGS")

    print(
        f"Overall status {exit_status.name} [{exit_status.value}]: {exit_status_message[exit_status]}",
        file=sys.stderr,
    )

    return exit_status.value


def _parse_args():
    parser = argparse.ArgumentParser(
        description="check the integrity of a ccpn V3 project and report errors and warnings"
    )
    parser.add_argument(
        "project_path", type=str, help="the path to the project to check", nargs=1
    )
    parser.add_argument(
        "-w",
        "--warnings-are-errors",
        action="store_true",
        help="treat warnings as errors",
    )

    return parser.parse_args()
