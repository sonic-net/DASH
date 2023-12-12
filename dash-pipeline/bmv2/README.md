# DASH Pipeline BM

This directory contains the P4/BMv2-based behavior model implementation of the DASH Pipeline.

At a high level, the DASH pipeline BM serves 2 purposes:

1. It provides a behavior model for DASH pipeline, which can be used for testing in a simulated environment.
2. It provides a generated P4 runtime definition, which can be used to generate the SAI API and SAI adapter code to the behavior model.

## Writing P4/BMv2 code

The workflow of developing the DASH pipeline BM is described in the [DASH workflows doc](../README-dash-workflows.md).

The DASH pipeline BM is written in P4<sub>16</sub> with BMv2 v1model. For specs, please find the referenced docs here:

- P4<sub>16</sub>, P4Runtime, PNA specs: <https://p4.org/specs/>
- V1Model: <https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4>

### P4 annotations for SAI code generation

Currently, some of the SAI generation behavior is either controlled by using the `@name` attribute with a non-formalized format, or simplifying guessing in the `sai_api_gen.py`. This is hard to maintain and extend and highly not recommended.

To deprecate the complicated `@name` attribute, we are moving towards using structured annotations in P4. This annotation can apply on keys, action parameters and tables to document and provide necessary metadata for SAI API generation.

The old mode is still supported, but no more new features will be added to it and it will be deprecated in the future.

#### `@SaiVal`: Keys and action parameters

Use `@SaiVal["tag"="value", ...]` format for annotating keys and action parameters.

Available tags are:

- `type`: Specify which SAI object type should be used in generation, e.g. `sai_uint32_t`.
- `isresourcetype`: When set to "true", we generate a corresponding SAI tag in SAI APIs: `@isresourcetype true`.
- `objects`: Space separated list of SAI object type this value accepts. When set, we force this value to be a SAI object id, and generate a corresponding SAI tag in SAI APIs: `@objects <list>`.
- `isreadonly`: When set to "true", we generate force this value to be read-only in SAI API using: `@flags READ_ONLY`, otherwise, we generate `@flags CREATE_AND_SET`.
- `skipattr`: When set to "true", we skip this attribute in SAI API generation.

#### `@SaiTable`: Tables

Use `@SaiTable["tag"="value", ...]` format for annotating tables.

Available tags are:

- `name`: Specify the preferred table name in SAI API generation, e.g. `dash_acl_rule`.
- `api`: Specify which SAI API should be used in generation, e.g. `dash_acl`.
- `stage`: Specify which stage this table represents for the matching stage type, e.g. `acl.stage1`.
- `isobject`: When set to "true", a top level objects in SAI that attached to switch will be generated. Otherwise, a new type of entry will be generated, if nothing else helps us to determine this table is an object table.
- `ignoretable`: When set to "true", we skip this table in SAI API generation.

For more details, please check the SAI API generation script: [sai_api_gen.py](../SAI/sai_api_gen.py).