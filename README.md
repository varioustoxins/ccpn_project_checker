# ccpn-project-checker

This is a small utility for checking the basic structure of a ccpn v3 project

## Installation

The program maybe installed as a command line tool using pipx:

```bash 
pipx install ccpn_project_checker
```

to force the installation to use a particular python distribution use:

```bash
pipx install ccpn_project_checker --python <PATH-TO-PYTHON-EXECUTABLE> 
```

where <PATH-TO-PYTHON-EXECUTABLE> is the path to a python executable e.g. `/usr/local/bin/python3` or something
equivalent

## Uninstalling

To remove the tool type

```bash
pipx uninstall ccpn_project_checker
```

## Invocation

to check a project type:

```bash
check-project Sec5Part4.ccpn
```

this will produce output most of which is a series of notes describing the project, for example the output for the
file `Sec5Part4.ccpn` is (note that the output is quite verbose so I have cut out the middle section):

```
NOTE: target Sec5Part4.ccpn
NOTE: project_name appears to be... Sec5Part4

...

NOTE: analysis took 0.078 seconds
Overall status EXIT_OK [0]: The project was ok

```

The first thing to not here is that the exit status is OK, this means that the project is ok and is useable as far as
the rules the project checker uses to check the contents, note the project could till fail to load because of more
subtle errors than the onse checked here.

The possible exit statuses are:

| Status name           | exit code | Meaning                                                                           |
|-----------------------|-----------|-----------------------------------------------------------------------------------|
| EXIT_OK               | 0         | the project is good                                                               |
| EXIT_ERROR_INCOMPLETE | 1         | the project is bad enough to halt analysis early                                  |
| EXIT_ERROR            | 2         | project analysis completed but the project has errors                             | 
| EXIT_INTERNAL_ERROR   | 3         | the run failed and there was an internal error analysis did not complete          |
| EXIT_WARN             | 4         | the project is usable but there are some worry features (e.g. orphaned files etc) |

the exit code is returned to the shell so that it can be used in scripts etc.

```bash
echo $?`
0
```

if we run the checker on a file with errors we again get a set of notes but this is followed by a list of one or more
errors

```
check-project Sec5Part4.ccpn
```

for example

```
NOTE: target Broken.ccpn
NOTE: project_name appears to be... Broken
NOTE: the directory Broken.ccpn has the correct suffix

NOTE: analysis took 0.000 seconds

ERRORS [1]:

1. code: MISSING_DIRECTORY
   caused by: Broken.ccpn/ccpnv3/memops/Implementation
   detailed message: the directory Broken.ccpn/ccpnv3/memops/Implementation doesn't exist
   

NOTE: the last error [1] prevented a complete analysis of the project
Overall status EXIT_ERROR_INCOMPLETE [1]: There was an error [the last one listed] in the project that prevented complete processing
```

The cause of this failure is that the directory `Broken.ccpn/ccpnv3/memops/Implementation` is missing.
This is a fatal error and the analysis stops at this point.

## Testing the installation

the checker also ships with a test suite that can be run using the command:

```bash
test-check-project
```

this will run pytest on the test suite and should produce output similar to that below
(note again much of the output has been elided for reasons of space):

```
=========================================================================== test session starts ============================================================================
platform darwin -- Python 3.10.13, pytest-8.1.1, pluggy-1.4.0 -- /Users/garyt/Library/Application Support/pipx/venvs/ccpn-project-checker/bin/python
cachedir: .pytest_cache
rootdir: /Users/garyt/Library/Application Support/pipx/venvs/ccpn-project-checker/lib/python3.10/site-packages/ccpn_project_checker/tests
plugins: time-machine-2.14.1
collected 58 items                                                                                                                                                         

test_api.py::test_memops_checker_read_protected[READ_PROTECTED_PROJECT] PASSED                                                                                       [  1%]
...                                                                                                                   [ 98%]
test_cli.py::test_cli_checker PASSED                                                                                                                                 [100%]

====================================================================== 57 passed, 1 skipped in 2.53s =======================================================================
```

you should see that all the tests pass if they do not then there is a problem with the installation and you should
contact the developer on his [github issues page]( https://github.com/varioustoxins/ccpn_project_checker/issues).
Note you may see a skipped test, in this case this is a test on a set of internal ccpn test projects which are not
part of the distribution and so this test is skipped.

## Using the project checker as a library

The project checker can also be used as a library, for example to check a project in a python program you can use the
following code:

```python

from ccpn_project_checker.DiskModelChecker import ModelChecker

file_path = 'Sec5Part4.ccpn'
checker = ModelChecker()
exit_code = checker.run(file_path)

```

This gives an exit code and a checker that has errors warning and notes that can be accessed using the `errors`
`warnings` and `notes` attributes of the checker object.

The exit_code is an instance of the enumeration DiskModelChecker.ExitStatus which ios defined as follows

````python
from enum import Enum


class ExitStatus(Enum):
    EXIT_OK = 0  # the project is good
    EXIT_ERROR_INCOMPLETE = 1  # the project is bad enough to halt analysis early
    EXIT_ERROR = 2  # the project is bad
    EXIT_INTERNAL_ERROR = 3  # the run failed and there was an internal error analysis did not complete
    EXIT_WARN = 4  # the project is usable but there are some worry features (orphaned files etc)
````

these mirror the comand line exit codes listed in the table above.

The messages stored in the checker object are stored as a list of tuples with the first element being the message  
and the second being a `bool` defining if the message should be indented or not (True indicates the note expects to
be printed without a prefix, False indictates the not expects a prefix such as 'NOTE:').

Warnings and Errors are both stored in a dataclass defined as follows

```python
from dataclasses import dataclass
from ccpn_project_checker.DiskModelChecker import ErrorCode
from typing import Any


@dataclass
class ErrorAndWarningData:
    code: ErrorCode
    cause: Any
    detail: str
    is_warning: bool = False
```

where:

`code` is an error code drawn from the enumeration ErrorCode which is defined below
`cause` is the object that caused the error, typically a path but i varies depending on error code
`detail` is a detailed message about the error
`is_warning` is a boolean that is True if the error is a warning and False if it is an error

All warnings maybe treated as errors using the parameter `warnings_are_errors` provided to the constructor
of the ModelChecker class; this parameter is False by default.

## Error Codes and Meanings

| Error code                                   | explanation                                                                                                                                                                                                                                                        |
|----------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| MISSING_DIRECTORY                            | the project directory provide doesn't exist                                                                                                                                                                                                                        |       
| IS_NOT_DIRECTORY                             | a part of the project that should be a directory  appears to be something else most probably a file                                                                                                                                                                |
| IS_NOT_FILE                                  | a part of the project that should be a file is a directory                                                                                                                                                                                                         |
| NO_MEMOPS_ROOT_FILES                         | when looking at the project there are no xml files in  `<PROJECT>.ccpn/ccpnv3/memops/Implementation` which should contain the root of the projects storage                                                                                                         |
| NOT_READABLE                                 | a file or directory in the project is not readable                                                                                                                                                                                                                 |
| READ_PROTECTED_PROJECT                       | the root project file `<PROJECT>.ccpn/ccpnv3/memops/Implementation/<PROJECT.xml>` is not readable                                                                                                                                                                  |
| READ_PROTECTED_CCPNV3                        | the ccpnv3 directory `<PROJECT>.ccpn/ccpnv3>` is not readable                                                                                                                                                                                                      |
| BAD_XML                                      | one of the projects xml files is not correcly formatted xml, the detail will contain a complete diagnosis from the lxml parser. If this occurse on the root project file it is a fatal error otherwise the checker will check as many files as can be read.        |
| NO_STORAGE_UNIT                              | each xml file should contains _exactly_ one storage unit with the structure ```xml <_StorageUnit ...></_StorageUnit>. This was missing from the root of the xmnl in the file                                                                                       |
| NO_ROOT_OR_TOP_OBJECT                        | each _StorageUnit should contain _exactly_ one element[^1] no child elements were found it was missing.                                                                                                                                                            |
| MULTIPLE_ROOT_OR_TOP_OBJECTS_IN_STORAGE_UNIT | each _StorageUnit should contain _exactly_ one element[^1] multiple elements were found.                                                                                                                                                                           |
| ROOT_IS_NOT_TOP_OBJECT                       | the child of the `_StorageUnit` in a non root project file was not a descendant of `IMPL.TopObject`                                                                                                                                                                |
| ROOT_IS_NOT_MEMOPS_ROOT                      | the child of the `_StorageUnit` in the root project file was not of type `IMPL.MemopsRoot`                                                                                                                                                                         |
| ROOT_HAS_NO_MODEL_VERSION                    | the `_StorageUnit` in the root project file shoudl have an attribute release which defines the current version of the dat model being saved. If this is missing or badly formatted its a fatal error as the version of the model being read cannot be ascertained. |
| NO_EXO_LINKS_FOUND                           | the root project file has no exo links [maybe this should be a warning, its not possible for a ccpn project but is otherwise legal]                                                                                                                                |
| EXO_LINK_ELEMENT_SOURCE_MISSING              | each exo link has a `link-location` identified by the guid the exo link encloses, this `link location` couldsn't be found                                                                                                                                          |
| EXO_LINK_ELEMENT_TOO_MANY_SOURCES            | each exo link has a `link-location` identified by the guid the exo link encloses, there should be one `link location` but more than one was found                                                                                                                  |
| # BASIC_EXO_LINKS_NOT_FOUND                  | this tested for a basic set of exo links and could be a warning but is unreliable as an error, it is currently disabled                                                                                                                                            |
| EXO_LINKED_FILE_MISSING                      | the exo linked file an exo link's guid points   to couldn't be found                                                                                                                                                                                               |
| EXO_LINKED_FILE_HAS_WRONG_KEY                | an exo link file was found using its guid but the keys in the files key don't maytch those expected                                                                                                                                                                |
| BADLY_FORMATTED_EXO_LINK_KEY_DATA            | the `link-location` is not correctly formatted and doesn't contain the corrrect elements for its keys                                                                                                                                                              |
| INTERNAL_AND_EXTERNAL_GUIDS_DISAGREE         | the name of an exo linked file contains its `instance-guid`, it is also present on the top object in the file; the two do not agree.                                                                                                                               |
| MISSING_PACKAGE_GUID                         | the exo linked file doesn't have the attribute `packageGuid` in its `<_StorageUnit>` element which identifies the package it should be stored in.                                                                                                                  |
| UNKNOWN_PACKAGE_GUID                         | the exo linked files packageGuid attribute in its `<_StorageUnit>` doesn't idnetify a known package.                                                                                                                                                               |
| BAD_ROOT_ELEMENT_NAME                        | the root element in the file doesn't have the correct tag /name which should be of the form `<SHORT_PACKAGE_NAME>.<TOP-OBJECT-NAME>`                                                                                                                               |
| UNKNOWN_SHORT_PACKAGE_NAME                   | the root element in the file doesn't have the correct tag /name contains a short package name which isn't known                                                                                                                                                    |
| SHORT_NAME_GUID_DOESNT_MATCH_PACKAGE_GUID    | the root element in the file has a short package name which doesn't match the `packageGuid` of its `<_StorageUnit>`                                                                                                                                                |
| EXO_FILE_WRONG_STORAGE_LOCATION              | the root element in the file has a short package name which doesn't its storage location / package directory in the file system                                                                                                                                    |
| MISSING_ATTRIB                               | only used internally an expected attribute on an xml elemenet is missing                                                                                                                                                                                           |  
| EXO_FILE_TIME_ATTRIB_MISSING                 | the `<_StorageUnit>` in the file doesn't have a `time` attribute [warning]                                                                                                                                                                                         |
| EXO_FILE_TIME_ATTRIB_INVALID                 | the `<_StorageUnit>` in the file doesn't have a  correctly formatted `time` attribute it should have the format "%a %b %d %H:%M:%S %Y" [warning]                                                                                                                   |
| EXO_FILE_RELEASE_ATTRIB_MISSING              | the `<_StorageUnit>` in the file doesn't have a  `release` attribute                                                                                                                                                                                               |
| EXO_FILE_RELEASE_ATTRIB_INVALID              | the `<_StorageUnit>` in the file doesn't have a correcly formatted `release` attribute. It should have the form described below in *The _StorageUnit Element*                                                                                                      |
| EXO_FILE_RELEASE_DOESNT_MATCH_ROOT           | the release version of the model in the `<_StorageUnit>` doesn't match that of he projects root                                                                                                                                                                    |
| BADLY_FORMATTED_ROOT_EXO_LINK                | the `exo-link` in the  file is badly formatted and is not of the form `<SHORT-PACKAGE-NAME>.exo-<CLASS=NAME>`                                                                                                                                                      |
| BADLY_FORMATTED_ROLE_EXO_LINK_KEY_DATA       | when building a role / reference key the `exo-link` in the  file is badly formatted / missing                                                                                                                                                                      |
| INTERNAL_ERROR                               | An internal error occured an Exception was raised                                                                                                                                                                                                                  |
| WARNING_DETACHED_FILES                       | There were top objects in the project that were not referenced by the root file of the project                                                                                                                                                                     |
| BAD_GUID_FORMAT                              | The `GUID` had an unexpected format the format of a `GUID` is described below in GUIDs [warning] This is not an error as long as the name is still globall unique                                                                                                  |
| NON_CCPN_ASCII_CHARACTER                     | Characters outside the CCN character set [A-Za-z0-9] + [+_] were found in a filename                                                                                                                                                                               |
| WARNING_EMPTY_CONTAINER                      | A storage location was foudn that didn't contain a `TopObject` xml file                                                                                                                                                                                            |
| ROOT_FILE_TIME_ATTRIB_MISSING                | the `<_StorageUnit>` in the root file doesn't have a `time` attribute [warning]                                                                                                                                                                                    |
| ROOT_FILE_TIME_ATTRIB_BAD_FORMAT             | the `<_StorageUnit>` in the root file doesn't have a  correctly formatted `time` attribute it should have the format "%a %b %d %H:%M:%S %Y" [warning]                                                                                                              |
| ROOT_MODEL_VERSION_BAD                       | the `<_StorageUnit>` in the root file doesn't have a  `release` attribute                                                                                                                                                                                          |
| ROOT_MODEL_VERSION_MISSING                   | the `<_StorageUnit>` in the root file doesn't have a correcly formatted `release` attribute. It should have the form described below in *The _StorageUnit Element*    |


## Supporting Utilities

The project checker also ships with a number of supporting utilities that can be used to assist in checking the contents 
of a project.

`MetaModelWalker.py` is a program that can be used to read the metamodel files in a distribution and generate
`v_3_1_0_guid_to_storage_location.json` - a dictionary that maps guids to the storage location of the object in the project
`v_3_1_0_object_info.json` - a dictionary that maps `class-guid`s to instances of `ObjectInfo`
```python
from dataclasses import dataclass
from typing import List,Dict
@dataclass
class ObjectInfo:

        
        guid: str                       # the class-guid
        name: str                       # the name of the class
        supertype_guids: List[str]      # the guids of the supertypes of the class
        parent_guid: str                # the guid of the parent element [a package]
        containment: List[str]          # the names of the packages that contain the class 
        keys: List[str]                 # the names of the key attributes of the class that uniquely identify and instance in the project
        key_type_guids: Dict[str, str]  # the guids of the types of the keys
        key_model_types: Dict[str, str] # the model types of the keys [either MetaAttribute or MetaRole]
        key_defaults: Dict[str, str]    # the default values of the keys
    

```

an example entry for a MOLE.Molecule

```json
"www.ccpn.ac.uk_Fogh_2006-08-16-14:22:54_00039": {
        "guid": "www.ccpn.ac.uk_Fogh_2006-08-16-14:22:54_00039",
        "name": "Molecule",
        "supertype_guids": [
            "www.ccpn.ac.uk_Fogh_2006-09-14-16:28:57_00002"
        ],
        "supertype_names": [
            [
                "memops",
                "Implementation",
                "TopObject"
            ]
        ],
        "parent_guid": "www.ccpn.ac.uk_Fogh_2006-08-16-14:22:54_00038",
        "containment": [
            "ccp",
            "molecule",
            "Molecule"
        ],
        "keys": [
            "name"
        ],
        "key_type_guids": {
            "name": "www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00033"
        },
        "key_model_types": {
            "name": "MetaAttribute"
        },
        "key_types_names": {
            "name": [
                "memops",
                "Implementation",
                "Line"
            ]
        },
        "key_defaults": {}
    },
```
`v_3_1_0_short_name_to_guid.json` a dictionary that maps package short names to guids

`MetaModelWalker.py` can be run as a command line tool using the command

```bash 
  scripts/walk-metamodel <MODEL-ROOT-DIRECTORY> <MODEL-VERSION>
```

by default <MODEL-ROOT-DIRECTORY> is the current directory and <MODEL-VERSION> is v_3_1_0

it is assumed that the model shoud be read from the directory `<MODEL-ROOT-DIRECTORY> "ccpnmodel" / "versions" / <MODEL-VERSION> `

`MetaModelWalker.py` can also be used as a library by importing the `MetaModelWalker` class and using the `build_top_info` method


## CCPN Project Structure

> [!Note]
> we will use the project Sec5Par4.ccpn as an example throughout this section

A ccpn v3 project [hence forrward a v3 project] is stored in a directory hierarchy with a specific structure containing
a series of XML files. The name of the top level directory is `<PROJECT-NAME>.ccpn` where `<PROJECT-NAME>` is the name of the project,
the `.ccp`n suffix is not required even for ccpn v3 project but is added by ccpn programs for the convenience of the user.

## Packages

All data in a v3 project is stored in packages, a package is a collection of data that is stored in files in a 
structured hierarchy of directories in much the same way that python modules are saved in packages. The package hierarchy of the `Sec5Part4.ccpn`
project is shown below as a tree.

```
.
├── ccp
│   ├── general
│   │   └── DataLocation
│   │       └── standard+default_user_2022-02-23-14-57-20-615_00001.xml
│   ├── lims
│   │   ├── RefSampleComponent
│   │   │   └── default+default_user_2022-02-23-14-57-20-616_00003.xml
│   │   └── Sample
│   │       └── default+default_user_2022-02-23-14-57-20-616_00002.xml
│   ├── molecule
│   │   ├── MolSystem
│   │   │   └── default+default_user_2022-02-23-14-57-20-617_00001.xml
│   │   └── Molecule
│   │       └── Sec5+Sec5Part1_user_2022-02-23-15-20-24-415_00001.xml
│   └── nmr
│       └── Nmr
│           └── default+default_user_2022-02-23-14-57-20-616_00001.xml
├── ccpnmr
│   └── gui
│       ├── Task
│       │   └── user+View+default_user_2022-02-23-14-57-20-617_00003.xml
│       └── Window
│           └── _ccp_nmr_Nmr_NmrProject___default___+default_user_2022-02-23-14-57-20-617_00002.xml
└── memops
    └── Implementation
        └── Sec5Part4.xml
```

The tree can be divided into two parts a root package `memops/Implementation` and a series of exolinked packages such as `ccp/general` and `ccpnmr/gui`.
Note that the file stored in the root package has a plane text name which is usually the same as the name of the project,
in this case `Sec5Part4.xml`. The files stored in the exo linked packages have names that are a mixture of `guids` and  `keys` 
[*vide infra*] and are stored in the rest of the tree [*the exo linked package tree*]. An example of an exo linked file and package would be 
`Sec5+Sec5Part1_user_2022-02-23-15-20-24-415_00001.xml` which defines a molecul and is stored in the package `molecule/Molecule`.
All files in the tree are xml files, in older versions of the ccpn data model backup files of the `<FILE-NAME>.xml.bak` were also stored
alongside the main files, but this is no longer the case, instead there are `archive` and `backup` directories containing complete saved and readable models at the same 
place in the hierarch as the ccpnv3 directory.

Packages can have two names a short two letter name such as `IMPL` which is equivalent to the second longer name `memops/Implementation`.
All packages and all typed elements in the project / model are also identified by a globally unique identifier or GUID 
such as `www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00025` these values are date and serial number based and are unique to a
particlular element in a project or model and should not repeat anywhere e ver excapt for the same elemement (i.e. across the universe!).

Note short and long names are not mixed, gerenally short names are used inside XML files as element tags and long names are used to name directory hierarchies.

The structure of a `GUID` is described elsewhere, see the section GUIDs

## GUIDs

Globally unique identifiers or GUIDs are used to identify all elements in a ccpn project. A GUID is a string of the form
`www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00025` where the first part is the domain of the element (www.ccpn.ac.uk_Fogh), the second part is the date
the element was created (2006-08-16-14:22:53) and the third part is a serial number (00025). The parts are separated by underscores.
The form of the domain varies dependinmg on the form of the GUID.
The CCPN data model uses two forms of GUID those defining classes in the model and those defining instances of classes in the model.
We shall call these `class guids` and `instance guids` respectively.
The first form the `class-guid` is usually of the form `www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00025`
the second form is used to define instances of classes in the model and is of the form `default_user_2022-02-23-14-57-20-617_00003`

All class guids can be found in the files `model_info/v_3-1_0_short_name_to_guid.json` `model_info/v_3_1_0_object_info.json`
and `model_info/v_3-1_0_guid_to_storage_location.json`

## The Root Package and its Contents

The reading of project starts at the root XML file which is stored in the directory
`<PROJECT-NAME>.ccpn/ccpnv3/memops/Implementation` generally in a file called
`<PROJECT-NAME>.ccpn/ccpnv3/memops/Implementation/<PROJECT-NAME>.xml`. However, the exact name of the root file is not
required to match the PROJECT-NAME, but it must have the .xml suffix and be the only xml file in the `ccpnv3/memops/Implementation` directory. The roots file contains information about the root storage element of the project,
in the case of a ccpn NMR project this is an element with the tag `IMPL.MemopsRoot`. All other componenets of the
project
are then stored in a series of XML files in the other directories in the project and will be referenced by exo links
from
the project root file [*vide infra*].

## The _StorageUnit Element

All v3 project files (both root and exo files) have a consistent structure they are XML files, and so they start with an
XML declaration
`<?xml version="1.0" encoding="UTF-8"?>`. they then always have a contain a storage element of the form
`<_StorageUnit ...> ... </_StorageUnit>` which is the root elemenet of the XML file. There can only be a single storage
elemement in the file. The <_StorageUnit> has a number of attributes which are common across all v3 files, these are

`time` the time the file was stored, the format of this attribute is "%a %b %d %H:%M:%S %Y" e.g. Tue May 10 12:29:35
2022"

`release` the version of the data model used to store the project. This is a triplet of the form <MAJOR>.<MINOR>.<PATCH>
<MAJOR> and <MINIOR> must be integers but patch can also have a prefix letter which is usally a or b to indicate an
alpha or beta version e.g 3.1.0

`packageGuid` is a guid indicating which package the file should be stored in for example
www.ccpn.ac.uk_Fogh_2006-08-16-14:22:53_00025 which defines the implimentation package. A list of guids and package
short names is included in the ccpn_project-checker in the file `model_info/v_3-1_0_short_name_to_guid.json`
the storage location of the package defined by the guid can be found in the file
`model_info/v_3_1_0_guid_to_storage_location.json`

`originator` defines which program wrote the file and is usually `CCPN Python XmlIO`

__nota bene__ only the `time` and `guid` attributes are required for reading of the model.

## The Root element of the Root File

The root elemenet of the root file is a `IMPL.MemopsRoot` element. The only important atribute of this element is the
`name` element which is the original name the file was saved under, it can vary from the name of the root xml file and 
the name of the project directory, the current name of the project is always the name of the project directory.

## Acceptable Characters in CCPN file names

Because of the way ccpn keys and guids are stored the only accaptable characters in a ccpn project and other files name are those that are 
in the set `a-zA-Z0-9`. Some additional characters are also allowed in the project name specifically the . character  in the .ccpn prefix.
Files outside the project root file are allowed some extra characters, specifically _ is used to escape spaces and as part of guids
and the + character is used in exo linked files but these are not allowed in the Root Files name (or maybe they are, **check**?)

## Exo Links

The root file contains a series of `exo-links` which are links to objects in other files in the project [exo linked files]. These links are stored in the
file as two parts. The first is a series of elements of the form `<MOLE.exo-Molecule>` which defines an exo link and we shall call an `exo-link`.  In this 
case the `rexo-link` link  is to a molecule [`Molecule`] stored in the MOLE package. These `exo-link` only occur once in the file and they point to a TopObject which is stored in an exo linked file.
The second part of the exo link which we shall call the `linked-location` are stored elsewhere in file and are identified by a `guid` attribute which contains an `instance-guid`.
The `instance-guid` is stored in the `exo-link` element in an `IMPL.GuidString` object (in this case `Sec5Part1_user_2022-02-23-15-20-24-415_00001`) as shown below:

```
<IMPL.MemopsRoot.currentMolecule>
    <MOLE.exo-Molecule>
      <IMPL.GuidString>Sec5Part1_user_2022-02-23-15-20-24-415_00001</IMPL.GuidString>
    </MOLE.exo-Molecule>
<I/MPL.MemopsRoot.currentMolecule>
```

The `instance-guid` can then be used to 
1. find the file that the exo link points to 
2. Find the exo link element in the project root file that the exo link points to

Lets first follow the `instance-guid` to the file that the exo link points to. The file that the exo link points to is 
identified by a package name guid and a key. The package name is stored as a short package name MOLE in the exo elements tag which defines the 
package  `ccp/molecule/Molecule` [`class-guid` www.ccpn.ac.uk_Fogh_2006-08-16-14:22:54_00038]. This then defines the directory the exo linked top object is saved in. The `instance-guid`
which is the guid leading to the exo linked file and appears in the name of the exo linked file 
is `Sec5Part1_user_2022-02-23-15-20-24-415_00001` and  this identifies a file in its package directory `ccp/molecule/Molecule`. The name of this file
is `Sec5+Sec5Part1_user_2022-02-23-15-20-24-415_00001.xml` it consists of the top objects keys separated by `+`s '. In this case the key is the name of the `Molecule`
which is `Sec5` the key is then followed by a `+` and the `instance-guid` of the object `Sec5Part1_user_2022-02-23-15-20-24-415_00001` followed by the suffix `.xml`.
More details of the exo linked files filename and escaping key and reference based keys are given below in the section *The TopObject Element Key*


Note that exolinked top objects can be stored in the project but can also refer to reference top objects which are not stored in the project directory,
these top object files are listed in the file `model-info/data_file_names.txt`

Now lets see where else this `instance-guid` appears in the root file. If we scan the root file we can find an element which has a 
`guid` attribute. In this case this is the element

```xml
<IMPL.MemopsRoot.molecules>
    <MOLE.Molecule _ID="1" _lastId="755" createdBy="user" guid="Sec5Part1_user_2022-02-23-15-20-24-415_00001" isFinalised="true">
      <MOLE.Molecule.name>
        <IMPL.Line>Sec5</IMPL.Line>
      </MOLE.Molecule.name>
    </MOLE.Molecule>
</IMPL.MemopsRoot.molecules>
```

This element is the `MOLE.Molecule` element that the exo link points to and is unique within the file . Other references 
to it within the root file will be via it _ID attribute [**check**] which is a unique identifier for the element within a file.

## The TopObject Element Key

Each exo linked element as well as having an `instance-guid` also has a key which is a series of values which are unique 
within the project. The key is stored in the link location as children which are identified by the metamodel. If we look at the
file `model-info/v_3_1_0_object_info.json` we can find the information derived from the metamodel file [****] that defines a
molecules key. In this case the key is the `name` of the object which is `Sec5` and is stored in the `MOLE.Molecule.name`element as
as an `IMPL.Line`.

```
 <IMPL.MemopsRoot.molecules>
    <MOLE.Molecule _ID="1" _lastId="755" createdBy="user" guid="Sec5Part1_user_2022-02-23-15-20-24-415_00001" isFinalised="true">
      <MOLE.Molecule.name>
        <IMPL.Line>Sec5</IMPL.Line>
      </MOLE.Molecule.name>
    </MOLE.Molecule>
  </IMPL.MemopsRoot.molecules>
```

If we look at the file name we can see that the key is stored in the file name as `Sec5+Sec5Part1_user_2022-02-23-15-20-24-415_00001.xml` 
where the key is `Sec5` and the guid is `Sec5Part1_user_2022-02-23-15-20-24-415_00001`. 

If there are multiple keys they appear in the filename separated by a `+` character, any spaces in the key are escaped as the `_` character.
Keys appear in the filename in the order they appear in the metamodel file, some keys may be missed out in which case they
are replaced by the default value which is stored in the metamodel file. An example of this is *** [does this introducte ambiguity???].
Finaly while this key is an atttribute keys it can also be links to other objects in the project. In this case the key is  built from 
the type of the linked object and its keys. An example of this is ... Note keys are also saved in the exo linked object in the exo linked filed as well.


## The TopObject Element File

Top objects are stored in files in the project in the same way as the root file. The structure of the file is the same as the
root file with a `_StorageUnit` element at the root of the file. The file is stored in a directory defined by the package name.
The file name is defined by the key and the guid of the top object. The key is stored in the exo linked file as values of the
object in the same ways as it is stored in the root object.






[^1]: this elemenet should be a descendant of `IMPL.MemopsRoot` if the file is the root project file or otherwise a
descendant of `IMPL.TopObject`