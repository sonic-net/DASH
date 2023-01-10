#!/bin/bash
# To be run inside saithrift-client container, assumes SAI repo portions exist under /SAI directory

ptf \
    --test-dir functional/ptf \
    --pypath /SAI/ptf \
    --interface 0@veth1 --interface 1@veth3 \
    --test-case-timeout=1800 \
    --test-params="bmv2=True" \
    $@
