# DASH High Availability (HA) proposal preview

By John Carney, Xsight Labs

There has been disagreement among members of the DASH community about the HA
requirements, tradeoffs, and proposed protocols/approaches. Each vendor has
unique architectures and constraints. There are many tradeoffs, including the
fidelity of HA/fault tolerance as well as the bandwidth/processing costs.

##  Desirable HA properties and goals

The following are desirable HA properties/goals (there are probably more). Due
to differences in architectures, constraints, and deployment use cases, I
propose that these remain qualitative not be quantified as strict requirements
of DASH. A DASH buyer may quantify any of these properties as strict
requirements for their particular deployment.

- Minimize or eliminate the possibility of established connections breaking
after a failover. If the endpoints of a connection have gotten into the
established state prior to a failover, then the connection should not be black
holed after a failover.

- Minimize the time to remove closed connections to avoid filling the connection
table with zombie connections. If a connection is closed/removed on one DPU,
then the connection should be quickly removed on the peer DPU. Zombie
connections will eventually age out. There should be some tolerance for a small
or bounded number of zombie connections in the connection table, especially
after a failover.

- Minimize the necessity for the endpoints to retransmit packets in order to
"replay" packets that cause state changes and are dropped due to HA transport or
processing constraints.

- Minimize link bandwidth and DPU processing overhead for HA state
synchronization.

Some of the above may represent conflicting goals for a particular HA approach.
For example, one HA approach may be able to minimize/eliminate the possibility
of breaking established connections by consuming more bandwidth for HA. Such
tradeoffs are appropriate in different use cases.

We are now working on a proposal for an HA protocol definition that will provide
HA interoperability while also enabling flexibility for each vendor to achieve
the above properties, given their own architecture, constraints and chosen
tradeoffs. Each vendor can individually quantify and be tested on the merits of
the HA properties described above. DASH should neither resort to a "least common
denominator" approach nor force complexity and HA modes that are too costly or
unimplementable for some vendors. The buyer of a DASH solution can test the
vendor's compliance with the defined HA protocol and decide if the vendor's
tradeoffs and adherence to the desired HA properties meets the requirements for
their use case.

We can publish the proposal with much more detail at a later date; in the
meantime, a **preview is shown below**.

## Proposal preview

For state synchronization there are state **sender** and a state **receiver**
roles. Each DPU implements both roles. There are two types of HA messages:
"state update" and "packet update". These will be defined in more detail in the
proposal.

The receiver must be able to parse and process both types of messages. The
sender may choose to coalesce multiple synchronization messages into a single
state synchronization packet, however the receiver will advertise the maximum
number of coalesced messages supported. The sender must honor this. A receiver
can specify this to be 1. The receiver's processing of HA packets/messages is
defined to be **simple and stateless**.

The sender of HA state synchronization updates has the full flexibility to be
stateless or stateful. The sender will specify with each state synchronization
packet whether a reply (completion) is requested and a hint of whether the reply
may be truncated. The reply is simply the original HA state synchronization
packet with a reply flag set and is possibly truncated (it is allowed, but not
bandwidth optimized, for the receiver to not truncate the reply when requested).
The sender may optionally include opaque information with each individual
message in the synchronization packet and/or for the synchronization packet at a
whole. When the reply is returned to the sender, the opaque information can be
used in an implementation specific manner to accomplish stateless or stateful
synchronization operations.

![ha-sync-operations](images/ha-sync-operations.svg)

Here are some examples of different HA approaches that are possible with this
simple protocol. A vendor may select among these (or other possible) approaches.
A vendor may limit their HA implementation to only the approach(es) that are
possible, feasible, or best for their architecture. The definition of the
receiver behavior is simple and remains independent of, but interoperable with,
any sender approach.

1. The sender may send packets that causes state updates to the receiver and
    have it returned back for transmission to the endpoint. Drops due to
    transport unreliability or exceeding DPU processing limits are retransmitted
    by the endpoints.
2. The sender may send a state update message with each state change event to
    the receiver without requesting replies. The sender may periodically resend
    the entire connection state without requesting replies.
3. With each packet that causes a state change, the sender may buffer/hold the
    packet and then send a state change message with an opaque value to the
    receiver, requesting a reply. When the opaque value is returned with the
    reply, it is associated with the held packet that is then transmitted to the
    endpoint. If the reply is not returned in a timely manner, the sender may
    drop the held packet and free the buffer, relying on the endpoints to
    retransmit dropped packets. Alternatively, the sender may choose to resend
    the synchronization message to the receiver, effectively creating a reliable
    transport without imposing any impact on the endpoints.

In addition to the above, there are many other possible tradeoffs that a sender
may make. The sender may choose to not send certain state change events for a
connection. This may save bandwidth at the expense of some fault tolerance. The
sender may only choose to buffer/hold certain packets and not others. For
example, there may be less value in buffering/holding syn packets. If the peer
does not learn of the syn and there is a failover. The syn-ack will be dropped
by the peer and the syn will be retransmitted by the endpoint. Anyone may
contribute a full definition and analysis any of the sender approaches above, or
other possible approaches/optimizations, as an optional "standardized" DASH HA
sender modes. These modes only affect the sender behavior. All sender modes use
the same protocol definition and the receiver behavior will always remain
simple, stateless and interoperable with all sender modes.

![ha-state-sync-packet-format](images/ha-state-sync-packet-format.svg)

We can produce the proposal with more detail, including the full packet/message
formats. We are happy to get early feedback and discussion before formalizing
the proposal. I wanted to get this out to you so that you can think about it,
and possibly respond, before the next meeting.
