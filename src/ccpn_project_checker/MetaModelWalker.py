import json
import os

from os import walk
from pathlib import Path
import xml.etree.ElementTree as et
import sys
from textwrap import dedent

from ccpn_project_checker.DiskModelChecker import ObjectInfo

top_object_info_map = {}
guid_to_type = {}
short_name_to_guid = {}

TOP_OBJECT_GUID = "www.ccpn.ac.uk_Fogh_2006-09-14-16:28:57_00002"
# key types currently not in use
# LINE_GUID = "www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00033"
# WORD_GUID= "www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00037"
# MOL_SYSTEM = 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:54_00023'
# LONG_WORD = 'www.ccpn.ac.uk_Fogh_2007-09-12-18:31:28_00003'
# MOL_TYPE = 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:52_00024'
# INT = 'www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00032'


def _get_parents_upto(file_path, root_name):

    parts = list(reversed(file_path.parts))
    xml_index = parts.index(root_name)

    return list(reversed(parts[1:xml_index]))


def _get_value_type(key_object):
    return [elem.text for elem in key_object if elem.tag == "valueType"][0]


def _analyse_file(root, file_path):
    result = None

    guid = root.attrib["guid"]

    parent_guid = root.attrib["container"] if "container" in root.attrib else None
    name = root.attrib["name"]
    super_types = [elem for elem in root if elem.tag == "supertypes"]
    location = _get_parents_upto(file_path, "xml")

    # really we should be following the package hierarchy to get the containment
    if root.tag == "MetaPackage":
        if name == "Root":
            guid_to_type[guid] = [
                name,
            ]
        else:
            guid_to_type[guid] = location

        short_name = root.attrib["shortName"] if "shortName" in root.attrib else None
        if short_name:
            short_name_to_guid[short_name] = guid
    else:
        guid_to_type[guid] = [*location, name]

    if super_types:
        super_type_guids = [elem.text for elem in super_types[0] if elem.tag == "item"]

        keys = _get_key_names(root)

        key_objects = [
            elem
            for elem in root
            if "name" in elem.attrib and elem.attrib["name"] in keys
        ]

        key_model_types = {
            key_object.attrib["name"]: key_object.tag for key_object in key_objects
        }

        key_value_types = {
            key_object.attrib["name"]: _get_value_type(key_object)
            for key_object in key_objects
        }

        default_items = _get_key_defaults(key_objects)

        result = ObjectInfo(
            name=name,
            guid=guid,
            supertype_guids=super_type_guids,
            containment=location,
            parent_guid=parent_guid,
            keys=keys,
            key_type_guids=key_value_types,
            key_model_types=key_model_types,
            key_defaults=default_items,
        )

    return result


def _get_key_defaults(key_objects):
    result = {}
    for key_object in key_objects:
        name = key_object.attrib["name"]

        default_value_elements = [
            elem for elem in key_object if elem.tag == "defaultValue"
        ]
        if len(default_value_elements) > 0:
            result[name] = [elem.text for elem in default_value_elements[0]][0]

    return result


def _get_key_names(root):
    key_names = [elem for elem in root if elem.tag == "keyNames"]
    if key_names:
        keys = [elem.text for elem in key_names[0] if elem.tag == "item"]
    else:
        keys = []
    return keys


def _load_file(file_path):
    with open(file_path, "r") as fh:
        root = None
        try:
            root = et.fromstring(fh.read())
        except et.ParseError as e:
            msg = f"""
            Error: the file {file_path.parts[-1]} can't be parsed as XML
            ****************************************************************
            error code: XML_PARSE_ERROR
            caused by: {file_path}
            detailed message:
            {e}
            ****************************************************************"""
            print(dedent(msg), file=sys.stderr)

    return root


def _patch_tree(tree):
    # PairwiseConstraintItems don't have keys... they should!
    if tree.attrib["guid"] == "www.ccpn.ac.uk_Fogh_2007-10-17-10:43:15_00001":
        print(
            "Note: modifying PairwiseConstraintItem to have KeyNames", file=sys.stderr
        )
        key_names = et.Element("keyNames")
        tree.append(key_names)
        resonances_item = et.Element("item")
        resonances_item.text = "resonances"
        key_names.append(resonances_item)

    return tree


def _walk_meta_model(directory_path):
    print(f"starting walk of model xml files from {directory_path}")

    all_top_object_info = {}
    for directory_path, _, file_names in walk(directory_path):
        for file_name in file_names:
            file_path = Path(directory_path) / file_name
            if file_path.suffix != ".xml":
                continue
            tree = _load_file(file_path)
            top_object_info = None
            if tree:
                tree = _patch_tree(tree)
                top_object_info = _analyse_file(tree, file_path)
            if top_object_info:
                all_top_object_info[top_object_info.guid] = top_object_info

    return all_top_object_info


def _find_all_super_types(top_object_info, top_object_info_map):
    super_type_guids = top_object_info.supertype_guids
    super_type_objects = [
        top_object_info_map[guid]
        for guid in super_type_guids
        if guid in top_object_info_map
    ]
    for super_type_object_info in super_type_objects:
        parent_objects = _find_all_super_types(
            super_type_object_info, top_object_info_map
        )
        super_type_objects.extend(parent_objects)

    super_type_by_guid = {object.guid: object for object in super_type_objects}

    return super_type_by_guid.values()


# from https://stackoverflow.com/questions/3494906/how-do-i-merge-a-list-of-dicts-into-a-single-dict
def _merge_dicts(dict_list):
    return {key: value for child_dict in dict_list for key, value in child_dict.items()}


def _find_values_over_hierarchy(top_object_info, field_name, top_object_info_map):
    top_object_info_list = [
        top_object_info,
        *_find_all_super_types(top_object_info, top_object_info_map),
    ]
    key_types = [
        getattr(top_object_info, field_name) for top_object_info in top_object_info_list
    ]
    return _merge_dicts(key_types)


def build_top_info(root, model_version):
    global top_object_info_map

    model_root = root / "ccpnmodel" / "versions"

    model_version_root = model_root / model_version

    if not model_version_root.exists():
        print(f"Error: {model_version_root} does not exist, exiting", file=sys.stderr)
        sys.exit(1)

    top_object_info_map = _walk_meta_model(model_version_root)

    for top_object_info in top_object_info_map.values():
        top_object_info.supertype_names = [
            guid_to_type[guid] for guid in top_object_info.supertype_guids
        ]
        top_object_info.key_types_names = {
            key: guid_to_type[guid]
            for key, guid in top_object_info.key_type_guids.items()
        }

        key_defaults = _find_values_over_hierarchy(
            top_object_info, "key_defaults", top_object_info_map
        )
        key_type_guids = _find_values_over_hierarchy(
            top_object_info, "key_type_guids", top_object_info_map
        )
        key_model_types = _find_values_over_hierarchy(
            top_object_info, "key_model_types", top_object_info_map
        )
        key_types_names = _find_values_over_hierarchy(
            top_object_info, "key_types_names", top_object_info_map
        )

        top_object_info.key_defaults = key_defaults
        top_object_info.key_type_guids = key_type_guids
        top_object_info.key_model_types = key_model_types
        top_object_info.key_types_names = key_types_names


if __name__ == "__main__":
    import time

    start = time.time()

    model_version = "v_3_1_0"
    if len(sys.argv) ==1:
        root = Path(os.getcwd())

    if len(sys.argv) >1 :
        root = Path(sys.argv[1])

    if len(sys.argv) > 2:
        model_version = sys.argv[2]


    if not root.exists():
        print(f"Error: {root} does not exist, exiting", file=sys.stderr)
        sys.exit(1)

    build_top_info(root, model_version)

    end = time.time()

    print(f"elapsed time: {end - start}")

    file_path = Path(__file__)
    model_info_path = file_path.parent / "model_info"
    with open(model_info_path / f"{model_version}_object_info.json", "w") as fh:
        json_data = json.dumps(
            top_object_info_map, default=lambda obj: obj.__dict__, indent=4
        )  # json.dump(top_object_info[0], fh,)
        fh.write(json_data)

    with open(
        model_info_path / f"{model_version}_guid_to_storage_location.json", "w"
    ) as fh:
        json.dump(guid_to_type, fh, indent=4)

    with open(model_info_path / f"{model_version}_short_name_to_guid.json", "w") as fh:
        json.dump(short_name_to_guid, fh, indent=4)
