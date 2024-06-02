#!/usr/bin/env python3

try:
    import os
    import json
    import argparse
    import copy
    import re
    import jinja2
    import typing
    import base64
    import yaml
    import yaml_include
    import jsonpath_ng.ext as jsonpath_ext
    import jsonpath_ng as jsonpath
    from utils.dash_p4 import DashP4SAIExtensions
    from utils.p4ir import P4IRTree, P4VarRefGraph
    from utils.sai_spec import SaiSpec
    from utils.sai_gen import SAIGenerator, SaiHeaderGenerator
except ImportError as ie:
    print("Import failed for " + ie.name)
    exit(1)


if __name__ == "__main__":
    # CLI
    parser = argparse.ArgumentParser(description="P4 SAI API generator")
    parser.add_argument("filepath", type=str, help="Path to P4 program RUNTIME JSON file")
    parser.add_argument("apiname", type=str, help="Name of the new SAI API")
    parser.add_argument("--ir", type=str, help="Path to P4 program IR JSON file")
    parser.add_argument("--print-sai-lib", type=bool)
    parser.add_argument("--ignore-tables", type=str, default="", help="Comma separated list of tables to ignore")
    parser.add_argument("--sai-spec-dir", type=str, required=True, help="Path to output SAI spec file")
    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    p4rt_file_path = os.path.realpath(args.filepath)
    if not os.path.isfile(p4rt_file_path):
        print("File " + p4rt_file_path + " does not exist")
        exit(1)

    p4ir = P4IRTree.from_file(args.ir)
    var_ref_graph = P4VarRefGraph(p4ir)

    # Parse SAI data from P4 runtime json file
    dash_sai_exts = DashP4SAIExtensions.from_p4rt_file(
        p4rt_file_path, args.ignore_tables.split(","), var_ref_graph
    )
    dash_sai_exts.post_parsing_process()

    if args.print_sai_lib:
        print("Dumping parsed SAI data:")
        print(json.dumps(dash_sai_exts, indent=2))

    # Initialize YAML loader and dumper
    sai_spec_dir = os.path.realpath(args.sai_spec_dir)
    yaml_inc_ctor = yaml_include.Constructor(base_dir=sai_spec_dir, autoload=True)
    yaml.add_constructor("!inc", yaml_inc_ctor)
    yaml_inc_rpr = yaml_include.Representer("inc")
    yaml.add_representer(yaml_include.Data, yaml_inc_rpr)

    # Ensure the current SAI spec can be loaded
    print("Loading SAI spec from " + sai_spec_dir)
    sai_spec = SaiSpec.deserialize(sai_spec_dir)

    # Output the new SAI spec
    print("Outputting new SAI spec to " + sai_spec_dir)
    yaml_inc_ctor.autoload = False
    new_sai_spec = dash_sai_exts.to_sai()
    new_sai_spec.finalize()
    sai_spec.merge(new_sai_spec)
    sai_spec.serialize(sai_spec_dir)

    # Generate and update all SAI files
    SAIGenerator(dash_sai_exts).generate()
    SaiHeaderGenerator(sai_spec).generate()
