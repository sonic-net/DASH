#!/bin/bash

./sai_api_gen.py \
    /bmv2/sirius_pipeline.bmv2/sirius_pipeline_p4rt.json \
    --ignore-tables=appliance,eni_meter,slb_decap \
    --overwrite=true \
    dash
