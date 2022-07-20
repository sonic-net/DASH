# DASH saithrift server

**TODO**

# Debugging Server with GDB
`gdb` is built into the saithrift server image for easy debugging. Server code is compiled with the `-g` flag to include debug symbols. The saithrift server source code is available from withint the running DOcker container via volume mounts. Below is shown some a typical workflow:

## Run Interactive sai-thrift-server container
This starts the container and opens a bash session instead of running the server like normal. The working directory `/SAI/rpc/usr/sbin` contains the saiserver.
```
$ make run-sai-thrift-server-bash 
docker run --rm -it --net=host --name dash-saithrift-server-chris -v /home/chris/chris-DASH/DASH/dash-pipeline/bmv2/dash_pipeline.bmv2/dash_pipeline.json:/etc/dash/dash_pipeline.json -v /home/chris/chris-DASH/DASH/dash-pipeline/bmv2/dash_pipeline.bmv2/dash_pipeline_p4rt.txt:/etc/dash/dash_pipeline_p4rt.txt -v /home/chris/chris-DASH/DASH/dash-pipeline/SAI:/SAI -w /SAI/rpc/usr/sbin -v /home/chris/chris-DASH/DASH/dash-pipeline/SAI/SAI/meta:/meta -e LD_LIBRARY_PATH=/SAI/lib:/usr/local/lib chrissommers/dash-saithrift-bldr:220719 \
/bin/bash
chris@chris-z4:/SAI/rpc/usr/sbin$
```
Start gdb on the saiserver process:
```
chris@chris-z4:/SAI/rpc/usr/sbin$ gdb saiserver 
GNU gdb (Ubuntu 9.2-0ubuntu1~20.04.1) 9.2
Copyright (C) 2020 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.
--Type <RET> for more, q to quit, c to continue without paging--c

For help, type "help".
Type "apropos word" to search for commands related to "word"...
Reading symbols from saiserver...
```
Point gdb to the mounted source directory which which must be build locally via `make sai-thrift-server`:
```
(gdb) dir /meta
Source directories searched: /meta:$cdir:$cwd
```
Set some breakpoints.
```
(gdb) b sai_api_query
Breakpoint 1 at 0x76d90
(gdb) b create_outbound_eni_to_vni_entry
Function "create_outbound_eni_to_vni_entry" not defined.
Make breakpoint pending on future shared library load? (y or [n]) y
Breakpoint 2 (create_outbound_eni_to_vni_entry) pending.
```
Run the process:
```
(gdb) r
Starting program: /SAI/rpc/usr/sbin/saiserver 
warning: Error disabling address space randomization: Operation not permitted
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
[New Thread 0x7f2b50e25700 (LWP 15)]
[New Thread 0x7f2b48624700 (LWP 16)]
[New Thread 0x7f2b4bfff700 (LWP 17)]
GRPC call SetForwardingPipelineConfig 0.0.0.0:9559 => /etc/dash/dash_pipeline.json, /etc/dash/dash_pipeline_p4rt.txt
```
First breakoint is reached, it's a startup behavior. Enter `c` to resume:
```
Thread 1 "saiserver" hit Breakpoint 1, sai_api_query (api=SAI_API_UNSPECIFIED, api_method_table=0x558bad22dd30 <test_services>) at utils.cpp:217
217	        _Out_ void **api_method_table) {
(gdb) c
Continuing.
Starting SAI RPC server on port 9092
[New Thread 0x7f2b4b7fe700 (LWP 18)]
[New Thread 0x7f2b4affd700 (LWP 19)]
```