### P4 annotations for SAI code generation

SAI API generation now supports P4 annotations for documenting/providing neccessary metadata to keys and action parameters.

Use `@Sai["tag"="value", ...]` format for annotating attributes. Old mode, where `sai_api_gen.py` is guessing this information, is still supported.

Available tags are:
* type - SAI type
* isresourcetype - generates a corresponding SAI tag
* objects - space separated list of SAI obejct types this attribute accepts

More annotations may be added in the future. The infrastructure is extedable.
