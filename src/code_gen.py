from ast import (
    arg,
    arguments,
    Assign,
    Attribute,
    Call,
    ClassDef,
    FunctionDef,
    Return,
    Name,
    Module,
)


def make_function(name, args):
    my_args = arguments(
        args=[arg(arg="self", annotation=None)]
        + [
            # XXX for arrays the name is '' (empty string)
            # which would end up being nothing in the generated
            # source file.
            arg(arg=my_arg or "arg", annotation=None)
            for my_arg in args
        ],
        defaults=[],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
    )
    my_body = [
        Return(
            value=Call(
                func=Attribute(
                    value=Attribute(
                        value=Attribute(value=Name(id="self"), attr="_contract"),
                        attr="functions",
                    ),
                    attr=name,
                ),
                args=[Name(id=my_arg or "arg") for my_arg in args],
                keywords=[],
            )
        )
    ]

    return FunctionDef(name=name, args=my_args, body=my_body, decorator_list=[])


def make_init():
    name = "__init__"
    args = arguments(
        args=[arg(arg="self", annotation=None), arg(arg="contract", annotation=None)],
        defaults=[],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
    )
    body = [
        Assign(
            targets=[Attribute(value=Name(id="self"), attr="_contract")],
            value=Name(id="contract"),
        )
    ]
    return FunctionDef(name=name, args=args, body=body, decorator_list=[])


def wrap_module(class_defs):
    return Module(body=class_defs)


def make_python_contract(contract_name, abi):

    functions = {}
    # events = {}  # XXX todo

    for item in abi:
        _type = item["type"]
        if _type == "function":
            # XXX doesn't work with overloaded functions for now
            # we take the one with highest arity as it's potentially
            # more useful.
            name = item["name"]
            if name not in functions:
                functions[name] = item
            else:
                if len(item["inputs"]) > len(functions[name]["inputs"]):
                    functions[name] = item

    init_def = make_init()
    function_defs = [
        make_function(name, [arg["name"] for arg in item["inputs"]])
        for name, item in sorted(functions.items())
    ]

    body = [init_def] + function_defs

    class_def = ClassDef(bases=[], name=contract_name, body=body, decorator_list=[])

    return class_def
