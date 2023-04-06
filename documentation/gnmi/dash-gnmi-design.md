# GNMI Interface for DASH

## Overview

SONiC should provide a gNMI server interface for DASH project.
Below diagram shows the architecture of the DASH project, the host server and DPU card are connected through PCIE, and together they form a smart switch.

![dash-arch](./images/gnmi-arch.svg)

Both host server and DPU card are running SONiC image. GNMI server is on host server, orchagent and redis are on DPU card, GNMI server will use ZMQ over TCP to communicate with orchagent and redis.

### Requirements

* Set and get RPCs must be supported. Customers will use get RPC to retrieve DASH configurations and use set PRC to apply new DASH configurations.
* Need to configure huge DASH table entries to APPL_DB, with high speed.
* Minimal redis table scaling requirements:

|Item |Expected value |
|--|--|
|VNETs|1024|
|ENI|64 per card|
|Outbound Routes per ENI|100K|
|Inbound Routes per ENI|10K|
|NSGs per ENI|10|
|ACL rules per NSG|1000|
|ACL prefixed per ENI|10*100K|
|Max prefixed per rule|8K|
|ACL ports per ENI|10*10K SRC/DST ports|
|CA-PA mapping|10M per card|

### Design considerations

* For set RPC, GNMI calls the ZMQ interface, and ZMQ updates redis asynchronously.
* For get RPC, GNMI reads from redis db directly.
* The DASH table of APPL_DB would be encoded as protobuf to save memory consumption, and then GNMI needs to support protobuf encoding for DASH table.

> 127.0.0.1:6379> hgetall "DASH_VNET_TABLE:vnet1"<br>
> 1\) "pb"<br>
> 2\) "\n\x010\x12$b6d54023-5d24-47de-ae94-8afe693dd1fc…"

And proto message for DASH_VNET_TABLE is:

> message Vnet {<br>
> &ensp;string vni = 1;<br>
> &ensp;string guid = 2;<br>
> &ensp;repeated types.IpPrefix address_space = 3;<br>
> &ensp;repeated string peer_list = 4;<br>
> }

Protobuf encoding message would be: "\n\x010\x12$b6d54023-5d24-47de-ae94-8afe693dd1fc…"
IETF JSON encoding message would be: "{'vni':'1000', 'guid':'b6d54023-5d24-47de-ae94-8afe693dd1fc'}"

* GNMI would not run Yang validation for protobuf encoding data.
  * GNMI server can check ENI and VNET if necessary.

# Design
## Set RPC
### Work flow
![gnmi-set-flow](./images/gnmi-set-flow.svg)

GNMI server would not run Yang validation, and it would invoke ZMQ interface to update.
ZMQ would update APPL_DB asynchronously, so client needs to wait for a few seconds to get latest update from APPL_DB.
### Message schema
Below table shows message example for SetRequest, including delete operation, replace operation and update operation:
SetRequest Message:
> delete {<br>
> &ensp;path {<br>
> &ensp;&ensp;origin: "sonic_db"<br>
> &ensp;&ensp;elem {name: “APPL_DB”} elem {name: “DASH_VNET_TABLE”} elem {name: “vnet1”}<br>
> &ensp;}<br>
> }<br>
> replace {<br>
> &ensp;path {<br>
> &ensp;&ensp;origin: "sonic_db"<br>
> &ensp;&ensp;elem {name: “APPL_DB”} elem {name: “DASH_VNET_TABLE”} elem {name: “vnet2”}<br>
> &ensp;}<br>
> }<br>
> replace {<br>
> &ensp;path {<br>
> &ensp;&ensp;origin: “sonic_db"<br>
> &ensp;&ensp;elem {name: “APPL_DB”} elem {name: “DASH_VNET_TABLE”} elem {name: “vnet3”}<br>
> &ensp;}<br>
> &ensp;val {<br>
> &ensp;&ensp;proto_bytes: “\n\x010\x12$b6d54023-5d24-47de-ae94-8afe693dd1fc…”<br>
> &ensp;}<br>
> }<br>
> update {<br>
> &ensp;path {<br>
> &ensp;&ensp;origin: "sonic_db"<br>
> &ensp;&ensp;elem {name: “APPL_DB”} elem {name: “DASH_VNET_TABLE”} elem {name: “vnet4”}<br>
> &ensp;}<br>
> &ensp;val {<br>
> &ensp;&ensp;proto_bytes: “\n\x010\x12$b6d54023-5d24-47de-ae94-8afe693dd1fc…”<br>
> &ensp;}<br>
> }

GNMI message has below constraints for DASH table:
* Path origin must be “sonic_db”.
* Path length must be 3, the first element must be “APPL_DB”, the second element must be DASH table name like “DASH_VNET_TABLE”, the third element must be DASH table key. And GNMI does not support wildcards for SetRequest.
* Value must use protobuf encoding.

## Get RPC
### Work flow
![gnmi-get-flow](./images/gnmi-get-flow.svg)

GNMI reads from APPL_DB directly.
### Message schema

> ++++++++ Sending get request: ++++++++<br>
> path {<br>
> &ensp;origin: "sonic_db"<br>
> &ensp;elem {name: "APPL_DB"} elem {name: "DASH_VNET_TABLE"} elem {name: "vnet1"}<br>
> }<br>
> encoding: PROTO<br>
> ++++++++ Recevied get response: ++++++++<br>
> notification {<br>
> &ensp;update {<br>
> &ensp;&ensp;path {<br>
> &ensp;&ensp;&ensp;origin: "sonic_db"<br>
> &ensp;&ensp;&ensp;elem {name: "APPL_DB"} elem {name: "DASH_VNET_TABLE"} elem {name: "vnet1"}<br>
> &ensp;&ensp;}<br>
> &ensp;&ensp;val {<br>
> &ensp;&ensp;&ensp;proto_bytes: "\n\x010\x12$b6d54023-5d24-47de-ae94-8afe693dd1fc…"<br>
> &ensp;&ensp;}<br>
> &ensp;}<br>
> }<br>


# References

- [SONiC GNMI Server Interface Design](https://github.com/sonic-net/SONiC/blob/master/doc/mgmt/gnmi/SONiC_GNMI_Server_Interface_Design.md)
- [SONiC-DASH HLD](https://github.com/sonic-net/DASH/blob/main/documentation/general/dash-sonic-hld.md)
- [Proto for DASH table](https://github.com/Pterosaur/DASH-benchmark/tree/master/memory/proto)



