import itertools
import json
import os

import astor
import pytest

from src import code_gen


@pytest.fixture
def abi():
    with open("out/contracts.json") as filehandle:
        contracts = json.load(filehandle)
    return json.loads(contracts["contracts"]["contracts/Foo.sol:Foo"]["abi"])


@pytest.fixture
def manually_converted():
    return astor.parse_file(os.path.join(os.path.dirname(__file__), "Foo.py"))


def test_code_gen(manually_converted, abi):

    generated = code_gen.wrap_module([code_gen.make_python_contract("Foo", abi)])

    original_lines = astor.to_source(manually_converted).split("\n")
    generated_lines = astor.to_source(generated).split("\n")

    for orig, gen in itertools.zip_longest(original_lines, generated_lines):
        assert orig == gen
