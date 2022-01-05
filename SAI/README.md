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
