#!/bin/bash
# Note the "cd" is because we have to invoke this from DASH top-level dir
# in order to provide visibility of parent git repo (DASH") to the SAI submodule repo
cd sirius-pipeline/SAI && ./sai_api_gen.py \
    /bmv2/sirius_pipeline.bmv2/sirius_pipeline_p4rt.json \
    --ignore-tables=appliance,eni_meter,slb_decap \
    --overwrite=true \
    dash