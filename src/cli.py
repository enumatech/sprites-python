import glob
import json
import os
import sys
from collections import defaultdict
from configparser import ConfigParser

import astor
import black

from .code_gen import make_python_contract, wrap_module

CONTRACTS_DIR = "src/contracts"


def cli():

    os.makedirs(CONTRACTS_DIR, exist_ok=True)
    cnfparser = ConfigParser()
    cnfparser.read(".flake8")
    line_length = int(cnfparser["flake8"]["max-line-length"])

    contract_fname = sys.argv[1]

    with open(contract_fname) as filehandle:
        contracts = json.load(filehandle)

    files = defaultdict(list)
    existing_paths = [
        path
        for path in glob.glob(os.path.join(CONTRACTS_DIR, "*.py"))
        if not path.endswith("__init__.py")
    ]
    new_paths = []

    for name, contract in contracts["contracts"].items():

        # exclude subdirs for now
        filename, contract_name = name.split(":")
        basename = os.path.basename(filename)

        py_fname = basename.replace(".sol", ".py")
        abi = json.loads(contract["abi"])
        class_def = make_python_contract(contract_name, abi)

        files[py_fname].append(class_def)

    for fname, class_defs in files.items():

        path = os.path.join(CONTRACTS_DIR, fname)
        new_paths.append(path)
        source_code = astor.to_source(wrap_module(class_defs))
        formatted_source_code = black.format_str(source_code, line_length)

        with open(path, "w") as filehandle:
            filehandle.write(formatted_source_code)

    to_remove = set(existing_paths) - set(new_paths)
    for filename in to_remove:
        os.remove(filename)
