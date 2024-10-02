import re
import copy
from typing import List
from utils.dash_p4 import *
from .sai_template_renderer import SAITemplateRenderer
from .sai_file_updater import SAIFileUpdater


class SAIGenerator:
    def __init__(self, dash_sai_ext: DashP4SAIExtensions):
        self.dash_sai_ext: DashP4SAIExtensions = dash_sai_ext
        self.dash_p4_names: List[str] = []
        self.generated_sai_api_extension_lines: List[str] = []
        self.generated_sai_type_extension_lines: List[str] = []
        self.generated_sai_port_attibute_extension_lines: List[str] = []
        self.generated_sai_object_entry_extension_lines: List[str] = []
        self.generated_header_file_names: List[str] = []
        self.generated_impl_file_names: List[str] = []

    def generate(self) -> None:
        print("\nGenerating all SAI APIs ...")

        for table_group in self.dash_sai_ext.table_groups:
            self.generate_sai_api_extensions(table_group)

        self.generate_sai_global_extensions()
        self.generate_sai_type_extensions()
        self.generate_sai_port_extensions()
        self.generate_sai_object_extensions()
        self.generate_sai_enum_extensions()
        self.generate_sai_fixed_api_files()

    def generate_sai_api_extensions(self, sai_api: DashP4TableGroup) -> None:
        print(
            "\nGenerating DASH SAI API definitions and implementation for API: "
            + sai_api.app_name
            + " ..."
        )

        self.dash_p4_names.append(sai_api.app_name)

        # For new DASH APIs, we need to generate SAI API headers.
        unique_sai_api = self.__get_uniq_sai_api(sai_api)
        if sai_api.api_type != "underlay":
            self.generate_dash_sai_definitions_for_api(unique_sai_api)

        # Generate SAI API implementation for all APIs.
        self.generate_sai_impl_file_for_api(sai_api)

    def generate_dash_sai_definitions_for_api(self, sai_api: DashP4TableGroup) -> None:
        # SAI header file
        sai_header_file_name = (
            "saiexperimental" + sai_api.app_name.replace("_", "") + ".h"
        )
        self.generated_header_file_names.append(sai_header_file_name)

        # Gather SAI API extension name and object types
        self.generated_sai_api_extension_lines.append(
            "    SAI_API_" + sai_api.app_name.upper() + ",\n"
        )

        for table in sai_api.tables:
            self.generated_sai_type_extension_lines.append(
                "    SAI_OBJECT_TYPE_" + table.name.upper() + ",\n"
            )

            if table.is_object == "false":
                self.generated_sai_object_entry_extension_lines.append(
                    "    /** @validonly object_type == SAI_OBJECT_TYPE_"
                    + table.name.upper()
                    + " */"
                )
                self.generated_sai_object_entry_extension_lines.append(
                    "    sai_" + table.name + "_t " + table.name + ";\n"
                )

        return

    def generate_sai_impl_file_for_api(self, sai_api: DashP4TableGroup) -> None:
        sai_impl_file_name = "sai" + sai_api.app_name.replace("_", "") + ".cpp"
        header_prefix = "experimental" if sai_api.api_type != "underlay" else ""
        SAITemplateRenderer("templates/saiapi.cpp.j2").render_to_file(
            "lib/" + sai_impl_file_name,
            tables=sai_api.tables,
            app_name=sai_api.app_name,
            header_prefix=header_prefix,
        )
        self.generated_impl_file_names.append(sai_impl_file_name)

    def generate_sai_global_extensions(self) -> None:
        print("\nGenerating SAI global extensions with API names and includes ...")
        with SAIFileUpdater("SAI/experimental/saiextensions.h") as f:
            f.insert_before(
                "Add new experimental APIs above this line",
                self.generated_sai_api_extension_lines,
                new_line_only=True,
            )
            f.insert_after(
                "new experimental object type includes",
                ['#include "{}"'.format(f) for f in self.generated_header_file_names],
                new_line_only=True,
            )

    def generate_sai_type_extensions(self) -> None:
        print("\nGenerating SAI type extensions with object types ...")
        with SAIFileUpdater("SAI/experimental/saitypesextensions.h") as f:
            f.insert_before(
                "Add new experimental object types above this line",
                self.generated_sai_type_extension_lines,
                new_line_only=True,
            )

    def generate_sai_port_extensions(self) -> None:
        print("\nGenerating SAI port extensions with port attributes ...")

        # If any counter doesn't have any table assigned, they should be added as port attributes and track globally.
        new_port_counters: List[DashP4Counter] = []
        new_port_stats: List[DashP4Counter] = []
        is_first_attr = False
        is_first_stat = False
        with open("SAI/experimental/saiportextensions.h", "r") as f:
            content = f.read()

            all_port_attrs = re.findall(r"SAI_PORT_ATTR_\w+", content)
            is_first_attr = len(all_port_attrs) == 3

            all_port_stats = re.findall(r"SAI_PORT_STAT_\w+", content)
            is_first_stat = len(all_port_stats) == 3

            for counter in self.dash_sai_ext.counters:
                if len(counter.param_actions) == 0:
                    if counter.attr_type != "stats":
                        sai_counter_port_attr_name = (
                            f"SAI_PORT_ATTR_{counter.name.upper()}"
                        )
                        if sai_counter_port_attr_name not in all_port_attrs:
                            new_port_counters.append(counter)
                    else:
                        sai_counter_port_stat_name = (
                            f"SAI_PORT_STAT_{counter.name.upper()}"
                        )
                        if sai_counter_port_stat_name not in all_port_stats:
                            new_port_stats.append(counter)

        sai_counters_str = SAITemplateRenderer("templates/saicounter.j2").render(
            table_name="port",
            sai_counters=new_port_counters,
            is_first_attr=is_first_attr,
        )
        sai_counters_lines = [s.rstrip(" \n") for s in sai_counters_str.split("\n")]
        sai_counters_lines = sai_counters_lines[
            :-1
        ]  # Remove the last empty line, so we won't add extra empty line to the file.

        sai_stats_str = SAITemplateRenderer(
            "templates/headers/sai_stats_extensions.j2"
        ).render(
            table_name="port", sai_stats=new_port_stats, is_first_attr=is_first_stat
        )
        sai_stats_lines = [s.rstrip(" \n") for s in sai_stats_str.split("\n")]
        sai_stats_lines = sai_stats_lines[
            :-1
        ]  # Remove the last empty line, so we won't add extra empty line to the file.

        with SAIFileUpdater("SAI/experimental/saiportextensions.h") as f:
            f.insert_before(
                "Add new experimental port attributes above this line",
                sai_counters_lines,
            )
            f.insert_before(
                "Add new experimental port stats above this line", sai_stats_lines
            )

    def generate_sai_object_extensions(self) -> None:
        print("\nGenerating SAI object entry extensions ...")
        with SAIFileUpdater("SAI/inc/saiobject.h") as f:
            f.insert_before(
                "Add new experimental entries above this line",
                self.generated_sai_object_entry_extension_lines,
                new_line_only=True,
            )
            f.insert_after(
                "new experimental object type includes",
                ["#include <{}>".format(f) for f in self.generated_header_file_names],
                new_line_only=True,
            )

        return

    def generate_sai_enum_extensions(self) -> None:
        print("\nGenerating SAI enum extensions ...")
        new_sai_enums: List[DashP4Enum] = []
        with open("SAI/experimental/saitypesextensions.h", "r") as f:
            content = f.read()
            for enum in self.dash_sai_ext.enums:
                if enum.name not in content:
                    new_sai_enums.append(enum)

        sai_enums_str = SAITemplateRenderer("templates/saienums.j2").render(
            sai_enums=new_sai_enums
        )
        sai_enums_lines = [s.rstrip(" \n") for s in sai_enums_str.split("\n")]
        sai_enums_lines = sai_enums_lines[
            :-1
        ]  # Remove the last empty line, so we won't add extra empty line to the file.

        with SAIFileUpdater("SAI/experimental/saitypesextensions.h") as f:
            f.insert_before("/* __SAITYPESEXTENSIONS_H_ */", sai_enums_lines)

    def generate_sai_fixed_api_files(self) -> None:
        print("\nGenerating SAI fixed APIs ...")
        for filename in ["saifixedapis.cpp", "saiimpl.h"]:
            SAITemplateRenderer("templates/%s.j2" % filename).render_to_file(
                "lib/%s" % filename, api_names=self.dash_p4_names
            )

    def __get_uniq_sai_api(self, sai_api: DashP4TableGroup) -> None:
        """Only keep one table per group(with same table name)"""
        groups = set()
        sai_api = copy.deepcopy(sai_api)
        tables = []
        for table in sai_api.tables:
            if table.name in groups:
                continue
            tables.append(table)
            groups.add(table.name)
        sai_api.tables = tables
        return sai_api
