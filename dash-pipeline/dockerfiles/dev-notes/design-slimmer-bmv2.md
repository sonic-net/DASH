```
CONTAINER ID   IMAGE                                    COMMAND                  CREATED             STATUS             PORTS     NAMES
d54a52f82826   chrissommers/dash-bmv2:pr127-220623      "bash"                   10 minutes ago      Up 10 minutes                hardcore_aryabhata
03fce865ba39   ixiacom/ixia-c-traffic-engine:1.4.1.26   "./entrypoint.sh"        24 minutes ago      Up 24 minutes                deployment_traffic_engine_1_1
375d0e198bbf   ixiacom/ixia-c-traffic-engine:1.4.1.26   "./entrypoint.sh"        24 minutes ago      Up 24 minutes                deployment_traffic_engine_2_1
417048602fc4   ixiacom/ixia-c-controller:0.0.1-2934     "./bin/controller --…"   24 minutes ago      Up 24 minutes                deployment_controller_1
1d8369a30db8   p4lang/behavioral-model:no-pi            "bash"                   40 minutes ago      Up 40 minutes                pensive_snyder
41bfeaba74dd   p4lang/third-party                       "bash"                   58 minutes ago      Up 58 minutes                dazzling_brahmagupta
0ec7e02af6f1   p4lang/p4c:stable                        "bash"                   About an hour ago   Up About an hour             eager_ritchie
97acd178acec   p4lang/pi                                "bash"                   About an hour ago   Up About an hour             keen_tu
c1925458bdf3   p4lang/behavioral-model:stable           "/bin/bash"              About an hour ago   Up About an hour             gracious_herschel
2982812c1ef1   p4lang/behavioral-model:latest           "bash"                   5 seconds ago   Up 4 seconds             naughty_panini
```


```
DOCKER_BMV2_RUN_IMG ?=p4lang/behavioral-model:stable
#DOCKER_BMV2_RUN_IMG ?=chrissommers/dash-bmv2:pr127-220623

.PHONY:run-switch
run-switch:
	$(DOCKER_RUN) \
	    --name simple_switch-$(USER) \
		-u root \
	    -v $(PWD)/bmv2/dash_pipeline.bmv2/dash_pipeline.json:/etc/dash/dash_pipeline.json \
	    -v $(PWD)/bmv2/dash_pipeline.bmv2/dash_pipeline_p4rt.txt:/etc/dash/dash_pipeline_p4rt.txt \
	    $(DOCKER_BMV2_RUN_IMG) \
	    env LD_LIBRARY_PATH=/usr/local/lib \
	    simple_switch_grpc \
	    --interface 0@veth0 \
	    --interface 1@veth2 \
	    --log-console \
	    --no-p4

chris@chris-z4:~/chris-DASH/DASH/dash-pipeline$ make run-all-tests
```
# Ensure P4Runtime server is listening
```
...
docker exec -w /tests/vnet_out simple_switch-chris ./vnet_out
./vnet_out: symbol lookup error: /SAI/lib/libsai.so: undefined symbol: _ZTVN2p42v19P4Runtime4Stub5asyncE
make: *** [Makefile:171: run-sai-test] Error 127
```

Find which lib has missing symbol in "good" (fat) bmv2 image:
```
chris@chris-z4:~/chris-DASH/DASH/dash-pipeline$ docker run -it --rm chrissommers/dash-bmv2:pr127-220623 bash
chris@acd579889e3e:/usr/local/lib$ grep -l _ZTVN2p42v19P4Runtime4Stub5asyncE *.so
libpiprotogrpc.so
```
