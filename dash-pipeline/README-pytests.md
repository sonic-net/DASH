
* [README-dash-workflows.md](README-dash-workflows.md) for build workflows and Make targets.
* [README-saithrift](README-saithrift.md) for saithrift client/server and test workflows.
* [README-ptftests](README-ptftests.md) for saithrift PTF test-case development and usage.

**Table of Contents**
- [Pytests](#pytests)
	- [Markers](#markers)
		- [View markers for tests](#view-markers-for-tests)
		- [Using Markers](#using-markers)
			- [Run all pytests](#run-all-pytests)
			- [Run select pytests](#run-select-pytests)
			- [Run pytests *except* selected](#run-pytests-except-selected)
		- [Run pytests - complex selection](#run-pytests---complex-selection)
- [Debugging](#debugging)
	- [View thrift protocol using tcpdump](#view-thrift-protocol-using-tcpdump)
	- [View thrift protocol using Wireshark](#view-thrift-protocol-using-wireshark)
# Pytests
## Markers
### View markers for tests
Markers can be used to select different tests, e.g. only bmv2 tests, only vnet tests, etc.
Custom markers are defined in `pytest.ini` and shown at the top of the list below:

```
python -m pytest --markers

@pytest.mark.bmv2:      test DASH bmv2 model

@pytest.mark.saithrift: test DASH using saithrift API

@pytest.mark.vnet:      test DASH vnet scenarios

<...SKIP built-in markers...>
```
### Using Markers
#### Run all pytests
```
python -m pytest -s
### Run vnet pytests
```
python -m pytest -s

#### Run select pytests
In this example we'll run *only* tests marked with `vnet`*
```
python -m pytest -m vnet
```
#### Run pytests *except* selected
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
Run tcpdump on local loopback port `9092` and select options to dump Hex and ASCII. You can see thrift RPC calls by name. Below is an example of calling `saithrift_get_switch_attribute()`.

Look at the 4th packet (request) and 6th packet (response):

```
$ sudo tcpdump -enXi lo tcp port 9092
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on lo, link-type EN10MB (Ethernet), capture size 262144 bytes
14:06:02.443857 00:00:00:00:00:00 > 00:00:00:00:00:00, ethertype IPv4 (0x0800), length 74: 127.0.0.1.40960 > 127.0.0.1.9092: Flags [S], seq 4281156243, win 65495, options [mss 65495,sackOK,TS val 2250594224 ecr 0,nop,wscale 7], length 0
	0x0000:  4500 003c 1669 4000 4006 2651 7f00 0001  E..<.i@.@.&Q....
	0x0010:  7f00 0001 a000 2384 ff2d 4293 0000 0000  ......#..-B.....
	0x0020:  a002 ffd7 fe30 0000 0204 ffd7 0402 080a  .....0..........
	0x0030:  8625 57b0 0000 0000 0103 0307            .%W.........
14:06:02.443875 00:00:00:00:00:00 > 00:00:00:00:00:00, ethertype IPv4 (0x0800), length 74: 127.0.0.1.9092 > 127.0.0.1.40960: Flags [S.], seq 1458900721, ack 4281156244, win 65483, options [mss 65495,sackOK,TS val 2250594224 ecr 2250594224,nop,wscale 7], length 0
	0x0000:  4500 003c 0000 4000 4006 3cba 7f00 0001  E..<..@.@.<.....
	0x0010:  7f00 0001 2384 a000 56f5 0ef1 ff2d 4294  ....#...V....-B.
	0x0020:  a012 ffcb fe30 0000 0204 ffd7 0402 080a  .....0..........
	0x0030:  8625 57b0 8625 57b0 0103 0307            .%W..%W.....
14:06:02.443889 00:00:00:00:00:00 > 00:00:00:00:00:00, ethertype IPv4 (0x0800), length 66: 127.0.0.1.40960 > 127.0.0.1.9092: Flags [.], ack 1, win 512, options [nop,nop,TS val 2250594224 ecr 2250594224], length 0
	0x0000:  4500 0034 166a 4000 4006 2658 7f00 0001  E..4.j@.@.&X....
	0x0010:  7f00 0001 a000 2384 ff2d 4294 56f5 0ef2  ......#..-B.V...
	0x0020:  8010 0200 fe28 0000 0101 080a 8625 57b0  .....(.......%W.
	0x0030:  8625 57b0                                .%W.
14:06:02.444303 00:00:00:00:00:00 > 00:00:00:00:00:00, ethertype IPv4 (0x0800), length 130: 127.0.0.1.40960 > 127.0.0.1.9092: Flags [P.], seq 1:65, ack 1, win 512, options [nop,nop,TS val 2250594225 ecr 2250594224], length 64
	0x0000:  4500 0074 166b 4000 4006 2617 7f00 0001  E..t.k@.@.&.....
	0x0010:  7f00 0001 a000 2384 ff2d 4294 56f5 0ef2  ......#..-B.V...
	0x0020:  8018 0200 fe68 0000 0101 080a 8625 57b1  .....h.......%W.
	0x0030:  8625 57b0 8001 0001 0000 001f 7361 695f  .%W.........sai_
	0x0040:  7468 7269 6674 5f67 6574 5f73 7769 7463  thrift_get_switc
	0x0050:  685f 6174 7472 6962 7574 6500 0000 000c  h_attribute.....
	0x0060:  0001 0f00 010c 0000 0001 0800 0100 0000  ................
	0x0070:  0000 0000                                ....
14:06:02.444322 00:00:00:00:00:00 > 00:00:00:00:00:00, ethertype IPv4 (0x0800), length 66: 127.0.0.1.9092 > 127.0.0.1.40960: Flags [.], ack 65, win 512, options [nop,nop,TS val 2250594225 ecr 2250594225], length 0
	0x0000:  4500 0034 8b50 4000 4006 b171 7f00 0001  E..4.P@.@..q....
	0x0010:  7f00 0001 2384 a000 56f5 0ef2 ff2d 42d4  ....#...V....-B.
	0x0020:  8010 0200 fe28 0000 0101 080a 8625 57b1  .....(.......%W.
	0x0030:  8625 57b1                                .%W.
14:06:02.444602 00:00:00:00:00:00 > 00:00:00:00:00:00, ethertype IPv4 (0x0800), length 121: 127.0.0.1.9092 > 127.0.0.1.40960: Flags [P.], seq 1:56, ack 65, win 512, options [nop,nop,TS val 2250594225 ecr 2250594225], length 55
	0x0000:  4500 006b 8b51 4000 4006 b139 7f00 0001  E..k.Q@.@..9....
	0x0010:  7f00 0001 2384 a000 56f5 0ef2 ff2d 42d4  ....#...V....-B.
	0x0020:  8018 0200 fe5f 0000 0101 080a 8625 57b1  ....._.......%W.
	0x0030:  8625 57b1 8001 0002 0000 001f 7361 695f  .%W.........sai_
	0x0040:  7468 7269 6674 5f67 6574 5f73 7769 7463  thrift_get_switc
	0x0050:  685f 6174 7472 6962 7574 6500 0000 000c  h_attribute.....
	0x0060:  0001 0800 01ff ffff f100 00              ...........
14:06:02.444621 00:00:00:00:00:00 > 00:00:00:00:00:00, ethertype IPv4 (0x0800), length 66: 127.0.0.1.40960 > 127.0.0.1.9092: Flags [.], ack 56, win 512, options [nop,nop,TS val 2250594225 ecr 2250594225], length 0
	0x0000:  4500 0034 166c 4000 4006 2656 7f00 0001  E..4.l@.@.&V....
	0x0010:  7f00 0001 a000 2384 ff2d 42d4 56f5 0f29  ......#..-B.V..)
	0x0020:  8010 0200 fe28 0000 0101 080a 8625 57b1  .....(.......%W.
	0x0030:  8625 57b1                                .%W.
14:06:02.492966 00:00:00:00:00:00 > 00:00:00:00:00:00, ethertype IPv4 (0x0800), length 66: 127.0.0.1.40960 > 127.0.0.1.9092: Flags [F.], seq 65, ack 56, win 512, options [nop,nop,TS val 2250594273 ecr 2250594225], length 0
	0x0000:  4500 0034 166d 4000 4006 2655 7f00 0001  E..4.m@.@.&U....
	0x0010:  7f00 0001 a000 2384 ff2d 42d4 56f5 0f29  ......#..-B.V..)
	0x0020:  8011 0200 fe28 0000 0101 080a 8625 57e1  .....(.......%W.
	0x0030:  8625 57b1                                .%W.
14:06:02.493072 00:00:00:00:00:00 > 00:00:00:00:00:00, ethertype IPv4 (0x0800), length 66: 127.0.0.1.9092 > 127.0.0.1.40960: Flags [F.], seq 56, ack 66, win 512, options [nop,nop,TS val 2250594274 ecr 2250594273], length 0
	0x0000:  4500 0034 8b52 4000 4006 b16f 7f00 0001  E..4.R@.@..o....
	0x0010:  7f00 0001 2384 a000 56f5 0f29 ff2d 42d5  ....#...V..).-B.
	0x0020:  8011 0200 fe28 0000 0101 080a 8625 57e2  .....(.......%W.
	0x0030:  8625 57e1                                .%W.
14:06:02.493088 00:00:00:00:00:00 > 00:00:00:00:00:00, ethertype IPv4 (0x0800), length 66: 127.0.0.1.40960 > 127.0.0.1.9092: Flags [.], ack 57, win 512, options [nop,nop,TS val 2250594274 ecr 2250594274], length 0
	0x0000:  4500 0034 166e 4000 4006 2654 7f00 0001  E..4.n@.@.&T....
	0x0010:  7f00 0001 a000 2384 ff2d 42d5 56f5 0f2a  ......#..-B.V..*
	0x0020:  8010 0200 fe28 0000 0101 080a 8625 57e2  .....(.......%W.
	0x0030:  8625 57e2                                .%W.

```
## View thrift protocol using Wireshark
**TODO:** There's rumor of a dissector, yet to be located.

* Launch Wireshark
* Enter the following filter: `tcp.dstport==9092`
* You can see RPC calls being made in the packet data view, the ASCII string names of methods are displayed