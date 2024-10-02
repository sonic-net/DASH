
all: copysrc
	./sai_api_gen.py \
		/bmv2/dash_pipeline.bmv2/dash_pipeline_p4rt.json \
		--ir /bmv2/dash_pipeline.bmv2/dash_pipeline_ir.json \
		--ignore-tables=underlay_mac,eni_meter,slb_decap \
		--sai-spec-dir=/SAI/specs \
		dash

copysrc:
	install -CDv src/Makefile src/*h src/*cpp lib/

.PHONY: clean
clean:
	rm -f lib/*
