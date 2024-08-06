from utils.sai_spec import SaiSpec, SaiApiGroup
from .sai_template_renderer import SAITemplateRenderer


class SaiHeaderGenerator:
    def __init__(self, sai_spec: SaiSpec):
        self.sai_spec: SaiSpec = sai_spec

    def generate(self) -> None:
        print("\nGenerating all SAI header files ...")

        for api_group in self.sai_spec.api_groups:
            if api_group.api_type == "underlay":
                continue
            
            self._generate_sai_api_group(api_group)
    
    def _generate_sai_api_group(self, api_group: SaiApiGroup) -> None:
        print(f"Generating SAI API definitions for API group: {api_group.name} ...")

        # SAI header file
        sai_header_file_name = f"saiexperimental{api_group.name.replace('_', '')}.h"
        SAITemplateRenderer("templates/headers/sai_api_group.h.j2").render_to_file(
            f"SAI/experimental/{sai_header_file_name}", api_group = api_group
        )