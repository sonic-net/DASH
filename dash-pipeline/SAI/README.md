# dash-pipeline/SAI directory description
## sai_api_gen.py
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
        ../dash-pipeline/bmv2/dash_pipeline.bmv2/dash_pipeline.json \
        --ignore-tables=appliance,eni_meter,slb_decap \
        --sai-git-url=https://github.com/marian-pritsak/SAI.git \
        --sai-git-branch=base \
        dash
```

In this example, the input is a dash_pipeline.json, which is a result of a P4 code compilation. The list of tables to ignore is provided to not generate API for them, because they are representing the underlay. A custom Git URL and branch can be provided. The last argument is a name of the API.

# requirements.txt
This is used for installing python modules, in particular for [snappi](https://github.com/open-traffic-generator/snappi) and [pytest](https://docs.pytest.org/en/7.1.x/index.html).

>**NOTE:** This file is a **hardlink** pointing to a single source of truth for test infrastructure. Take care accordingly. Modifying its contents will impact other collections of test scripts. It's a hardlink for convenience in order to pass the Docker context when building the `saithrift-client` images. We can't use a symlink because Docker cannot dereference symlinks in the context passed to it, see https://stackoverflow.com/questions/31881904/docker-follow-symlink-outside-context and https://medium.com/@307/hard-links-and-symbolic-links-a-comparison-7f2b56864cdd.
