
all: copysrc
	./sai_api_gen.py \
		/bmv2/dash_pipeline.bmv2/dash_pipeline_p4rt.json \
		--ignore-tables=appliance,eni_meter,slb_decap \
		dash

copysrc:
	install -CDv src/Makefile src/*h src/*cpp lib/

.PHONY: clean
clean:
	rm -f lib/*
