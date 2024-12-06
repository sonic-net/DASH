from utils.sai_spec import SaiSpec, SaiApiGroup
from .sai_template_renderer import SAITemplateRenderer


class SaiImplGenerator:
    def __init__(self, sai_spec: SaiSpec):
        self.sai_spec: SaiSpec = sai_spec

    def generate(self) -> None:
        print("\nGenerating SAI API implementation for all APIs ...")

        for api_group in self.sai_spec.api_groups:
            self._generate_sai_api_group(api_group)

    def _generate_sai_api_group(self, api_group: SaiApiGroup) -> None:
        print(f"Generating SAI API implementation for API group: {api_group.name} ...")

        # SAI implementation file
        sai_impl_file_name = f"sai{api_group.name.replace('_', '')}.cpp"
        SAITemplateRenderer("templates/impls/sai_api_group.cpp.j2").render_to_file(
            f"lib/{sai_impl_file_name}", api_group = api_group
        )
