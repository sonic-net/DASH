# DASH saithrift pytests
## Production - Launch container, run tests in one shot
```
make run-saithrift-client-tests
```

**TODO:** - pass params to the container to select tests etc.
# Developer: Run Tests Inside saithrift-client container
Enter the container, this will place you in the `/saithrift` directory of the continer which corresponds to the contents of the `DASH/dash-pipline/SAI/saithrift` directory when the container *image* was built.
```
make run-saithrift-client-bash 
root@chris-z4:/saithrift-host# 
```
The runing container is also mounted via `-v $(PWD)/SAI/saithrift:/saithrift-host`  which mounts the current developer workspace into the running container. You can thereby create and edit new tests "live" from a text editor and see the effect inside the container in real-time.

## Select Directory - Container pre-built directory, or mounted from host

* `cd /saithrift/pytest` - Enter directory which was prebuilt into container image; tests are not modifiable "live" from the host. This is good for canned tests.
* `cd /saithrift/pytest` - Enter directory which is mounted to `.../saithrift` from the host allowing live editing in the host and running in the container. This is a convenient developer workflow.

# Markers
## View markers for tests
Markers can be used to select different tests, e.g. only bmv2 tests, only vnet tests, etc.
Custom markers are defined in `pytest.ini` and shown at the top of the list below:

```
python -m pytest --markers

@pytest.mark.bmv2:      test DASH bmv2 model

@pytest.mark.saithrift: test DASH using saithrift API

@pytest.mark.vnet:      test DASH vnet scenarios

<...SKIP built-in markers...>
```
## Using Merkers
### Run all pytests
```
python -m pytest -s
### Run vnet pytests
```
python -m pytest -s

### Run select pytests
In this example we'll run *only* tests marked with `vnet`*
```
python -m pytest -m vnet
```
### Run pytests *except* selected
In this example we'll run all tests *except* tests marked with `vnet`*
```
python -m pytest -m "not vnet"
```

### Run pytests - complex selection
In this example we'll run all tests marked with `bmv2`  *except* tests marked with `vnet`*
```
python -m pytest -m "bmv2 and not vnet"
```
# Debugging
## View thrift protocol using tcpdump
```
$ sudo tcpdump -i lo tcp port 9092
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on lo, link-type EN10MB (Ethernet), capture size 262144 bytes
17:40:10.712015 IP localhost.32840 > localhost.9092: Flags [S], seq 3380176803, win 65495, options [mss 65495,sackOK,TS val 2177042493 ecr 0,nop,wscale 7], length 0
17:40:10.712031 IP localhost.9092 > localhost.32840: Flags [S.], seq 1354327198, ack 3380176804, win 65483, options [mss 65495,sackOK,TS val 2177042493 ecr 2177042493,nop,wscale 7], length 0
17:40:10.712042 IP localhost.32840 > localhost.9092: Flags [.], ack 1, win 512, options [nop,nop,TS val 2177042493 ecr 2177042493], length 0
17:40:10.731751 IP localhost.32840 > localhost.9092: Flags [F.], seq 1, ack 1, win 512, options [nop,nop,TS val 2177042512 ecr 2177042493], length 0
17:40:10.731963 IP localhost.9092 > localhost.32840: Flags [F.], seq 1, ack 2, win 512, options [nop,nop,TS val 2177042512 ecr 2177042512], length 0
17:40:10.731992 IP localhost.32840 > localhost.9092: Flags [.], ack 2, win 512, options [nop,nop,TS val 2177042513 ecr 2177042512], length 0
```
## VIew thrift protocol using Wireshark
**TODO:** There's rumor of a dissector, yet to be located.

* Launch Wireshark
  
* Enter the following filter: `tcp.dstport==9092`