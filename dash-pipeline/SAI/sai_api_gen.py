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
    import jsonpath_ng.ext as jsonpath_ext
    import jsonpath_ng as jsonpath
    from utils.dash_p4 import DashP4SAIExtensions
    from utils.p4ir import P4IRTree, P4VarRefGraph
    from utils.sai_gen import SAIGenerator
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
    args = parser.parse_args()

    p4rt_file_path = os.path.realpath(args.filepath)
    if not os.path.isfile(p4rt_file_path):
        print("File " + p4rt_file_path + " does not exist")
        exit(1)

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

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

    # Generate and update all SAI files
    SAIGenerator(dash_sai_exts).generate()
