import os
import yaml
import yaml_include
from typing import List
from .sai_enum import SaiEnum
from .sai_api_group import SaiApiGroup
from .sai_api_extension import SaiApiExtension
from .sai_struct_entry import SaiStructEntry
from . import sai_spec_utils


class SaiSpec:
    """
    Top class of the SAI API, which holds all the SAI API groups and any top level objects.
    """

    def __init__(self):
        self.api_types: List[str] = []
        self.object_types: List[str] = []
        self.object_entries: List[SaiStructEntry] = []
        self.enums: List[SaiEnum] = []
        self.port_extenstion: SaiApiExtension = SaiApiExtension()
        self.api_groups: List[SaiApiGroup] = []

    def finalize(self):
        _ = [object_entry.finalize() for object_entry in self.object_entries]
        _ = [enum.finalize() for enum in self.enums]
        _ = [api_group.finalize() for api_group in self.api_groups]
        self.port_extenstion.finalize()

    def serialize(self, spec_dir: str):
        yaml_inc_files = []
        for api_group in self.api_groups:
            sai_api_group_spec_file_path = os.path.join(
                spec_dir, api_group.name + ".yaml"
            )

            with open(sai_api_group_spec_file_path, "w") as f:
                f.write(yaml.dump(api_group, indent=2, sort_keys=False))

            yaml_inc_files.append(
                yaml_include.Data(urlpath=sai_api_group_spec_file_path)
            )

        api_groups = self.api_groups
        self.api_groups = yaml_inc_files

        sai_spec_file_path = os.path.join(spec_dir, "sai_spec.yaml")
        with open(sai_spec_file_path, "w") as f:
            f.write(yaml.dump(self, indent=2, sort_keys=False))

        self.api_groups = api_groups

    def deserialize(spec_dir: str):
        with open(os.path.join(spec_dir, "sai_spec.yaml")) as f:
            return yaml.unsafe_load(f)

    def merge(self, other: "SaiSpec"):
        sai_spec_utils.merge_sai_value_lists(
            self.api_types, other.api_types, lambda x: x
        )
        sai_spec_utils.merge_sai_value_lists(
            self.object_types, other.object_types, lambda x: x
        )
        sai_spec_utils.merge_sai_common_lists(self.object_entries, other.object_entries)

        # Althoug the order of enum value doesn't matter, but we still merge it in the same way
        # other SAI values, because:
        # - P4 compiler is not maintaining the order of enum values, so the definitions in SAI
        #   spec can move around and make code review harder.
        # - Removing enum can break existing code.
        sai_spec_utils.merge_sai_value_lists(
            self.enums, other.enums, lambda x: x.name,
            on_conflict = lambda x, y: x.__dict__.update(y.__dict__),
        )

        self.port_extenstion.merge(other.port_extenstion)
        sai_spec_utils.merge_sai_common_lists(self.api_groups, other.api_groups)
