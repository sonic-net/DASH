```
usage: sai_api_gen.py [-h] [--print-sai-lib PRINT_SAI_LIB]
                      [--sai-git-url SAI_GIT_URL]
                      [--ignore-tables IGNORE_TABLES]
                      [--sai-git-branch SAI_GIT_BRANCH]
                      filepath apiname

P4 SAI API generator

positional arguments:
  filepath              Path to P4 program BMV2 JSON file
  apiname               Name of the new SAI API

optional arguments:
  -h, --help            show this help message and exit
  --print-sai-lib PRINT_SAI_LIB
  --sai-git-url SAI_GIT_URL
  --ignore-tables IGNORE_TABLES
                        Coma separated list of tables to ignore
  --sai-git-branch SAI_GIT_BRANCH
```

Example:
```
./sai_api_gen.py \
        ../sirius-pipeline/bmv2/sirius_pipeline.bmv2/sirius_pipeline.json \
        --ignore-tables=appliance,eni_meter,slb_decap \
        --sai-git-url=https://github.com/marian-pritsak/SAI.git \
        --sai-git-branch=base \
        dash
```

In this example, the input is a sirius_pipeline.json, which is a result of a P4 code compilation. The list of tables to ignore is provided to not generate API for them, because they are representing the underlay. A custom Git URL and branch can be provided. The last argument is a name of the API.
