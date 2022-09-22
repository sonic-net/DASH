
# Overview

This document is a placeholder for the HA protocol proposal.  
The purpose is to generate discussion that will lead to an actual design doc.


# HA Requirements

See the [High Availability and Scale](high-availability-and-scale.md) document for the requirements.

# Proposal

Our thoughts and proposals for the HA protocol follows below.


## Channels

We propose that the HA protocol defines a control channel and a data channel.  
The control channel is used to exchange control messages after two cards are paired.  
Control messages can include an exchange of capabilities, commands to start and stop active syncing, start and stop perfect syncing etc.  
Control messages would determine which Mode and attributes are used for the data channel. The control channel uses TCP for transport.  
The data channel is used to exchange the flow update messages.  


The channels are shown in this functional model of the HA synchronization mechanisms:

![ha-functional-diagram.svg](images/ha-functional-diag.svg)


## Modes

Some examples of possible modes for syncing active flows are:

- Mirror
   - Each customer packet that changes the flow state (SYN, FIN, etc) is truncated and encapsulated and sent to the peer. There is one message per HA packet.
- Batch
   - Each HA packet contains one or more messages, up to as many messages as will fit in an MTU-size packet. Each message contains the flow keys.
- Compressed
   - Some method of reducing bandwidth of HA messages.

We propose that Batched mode is the base mode.  
Mirror mode can be considered to be just Batch mode with a maximum of one message per HA packet.  
We assume that a card that can only mirror a packet is still flexible enough to massage the contents to look like a Batch packet.  
Other modes (e.g. Compressed mode) are not defined at this time.


## Active Flow Sync Algorithm

We expect that normally a peer will send an HA message to insert a flow and then later will send an HA message to remove the flow.  
We assume that the communication path between paired cards is highly reliable but not 100% reliable.  
It is possible that the peer occasionally does not or cannot send an HA flow message. (e.g. the peer dies just as the flow ages out, the network drops the message).   
In addition, we believe that using a reliable transport like TCP would have too much overhead for the flow messages.  

The card/DPU must not rely solely on unreliable messages to remove the passive flows.   
For example, say the network drops on average one packet out of a million.  
If the card is processing 5M connections per second, then it is sending 5M insert and 5M remove messages per second.   
This means that on average 5 remove messages are lost every second. Each creates a zombie passive flow entry that will not be removed.   
Zombie flows would eventually fill the flow table.   

We propose that cards have the ability to age out passive flows.  
Below we use the terms "local card" and "peer card" to refer to the two paired cards.  
An active flow is one that was learned due to a customer packet arriving on the local card; a passive flow is one installed by a message from the peer.  

- In the flow table, each passive flow has an HA timer
- There is a global HA timeout that is chosen by the HA protocol, and is separate from the active flow timeout
- Flow messages are sent over UDP transport
- The flow key includes a mac address and IP 5-tuple
- When the peer card learns a new active flow,
   - It sends to the local card a message (Insert) containing the flow key and the active timeout
   - The local card creates the passive flow entry and writes the active timeout
   - The local card also sets the HA timeout for the flow entry
- When the peer card removes active flow (due to flow termination or age out),
   - It sends to the local card a message (Remove) containing the flow key and a 0 active timeout
   - The local card removes the passive flow entry immediately (or very quickly)
   - This is the normal way that passive flows are removed

- The peer card periodically scans its active flow entries.
   - It sends an Update message to the local card containing the flow key and the current active timeout.
   - The local card creates a passive flow entry if not already there, stores the active timeout in the flow entry, and sets its HA timer to the HA timeout value
      - This helps address the case of a lost Insert message (there are multiple attempts to install a flow entry)
   - Note that the active timeout value in passive flow entries may be stale if the active timeout < HA timeout. 
      - This is because the peer card can update the active timer for the flow more frequently than the Update messages are sent (but this is ok).
- The local card periodically scans its passive flow entries.
  - If the card is still receiving updates from the peer card (normal operation)
      - If the HA timer has expired, then remove the flow.
      - This addresses the case of a lost Remove message
  - If the card is no longer receiving updates from the peer card (failover occurred):
      - Packets should be flowing (now or very soon) to the local card instead of the peer card. 
      - A packet can turn the passive flow entry into an active flow entry.
      - If the HA timer has expired, then:
         - If the active timeout < HA timeout, then remove the flow
         - If the active timeout > HA timeout, *and* the active timeout has expired, then remove the flow
  - The "no longer receiving updates" state could be triggered by an Unpair API call, a loss of keepalive between paired cards on the control channel, etc.

- The interval at which a card sends update messages is a tradeoff between:
  - The amount of extra PPS/bps for HA messages (smaller interval means more data to send)
  - The number of missing flow entries at failover (smaller interval means fewer missing entries)
  - The number of zombie flows in the flow table (smaller interval means fewer zombie flows)
- We propose:
  - Send the first update message 10 seconds after sending the Insert message for a new flow
      - This narrows the window where a flow is not replicated due to a lost Insert message.
      - We assume most flows are short-lived
      - A significant percentage of flows would terminate before 10 seconds and not need an Update message
      - The PPS/bps overhead for this first Update message should be moderate due to this
  - Send the subsequent update messages at 60 second intervals
      - We expect a relatively small number of flows will be active for more than this time
      - PPS/bps overhead will be low even if there are a moderate number of long-lived flows due to the large interval.
      - A larger interval means more zombie flows in the flow table,
but we can tolerate thousands of zombie entries because the flow table capacity is 50 million flows.
   - The HA timeout is 181 seconds
     - This allows three Update messages to be lost before an active flow would be erroneously removed.
     - Even if a flow entry is erroneously removed, a subsequent Update message can add it back.
   - These parameters (defaulting to 60/181/10 seconds) could also be configured through an API.

- Flows replicated upon initial pairing through the perfect sync algorithm would be treated similar to the passive flows above.
   - The peer card sends Update messages for all flow entries, both active and passive, to the local card
   - The local card inserts passive flow entries into its flow table
   - Update messages can be lost during perfect sync, just like any HA message
   - When the perfect sync completes, the local card advertises its VIP.  Packets start to flow to this card shortly afterward.
   - Packets arriving on the local card can turn passive flow entries into an active flow entries.
   - Ideally the flow table scan of passive entries does not begin until the perfect sync completes
     - You don't want to start aging entries that were passive on the peer until traffic can flow to the local card;
     you want to give them time to become active here.
     - We could also produce this behavior by setting an initial HA timeout that is extra-long for flows created during the perfect sync.

We have thoughts on additional details (control messages, data message format, etc) but thought that we should get agreement on the basics first.


# Additional Considerations

Comments on the initial version of this document are captured below:

1. gRPC could be used for the control channel. It's the favored messaging protocol these days and would make it easy to write production as well as test applications. It can actually be quite performant, especially if streaming connections are used.

1. We need to think about a "management" interface to the HA subsystem, to configure operating parameters (e.g. timeouts), perform resets, query states and statistics, etc. This then begs the question, "will there be a SAI API to the HA controller?"

1. Presumably a behavioral model could be built which allows the algorithm to be evaluated and simulated at scale, without requiring actual HW targets. (Extra credit: this could even be plugged into e.g. NS3 simulations).

1. We need to think about test & performance criteria, even test techniques. If we pose some requirements, we need to ensure they're testable. This might require extra observability features (streaming internal state & stats updates, above and beyond the presumed management API).

1. We need to think about continuous observability, including a high-fidelity mode (e.g. streaming high-speed updates of the internal states) to be able to judge performance of the HA system in a lab or even live environment.

