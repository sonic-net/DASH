#ifndef _SIRIUS_INBOUND_P4_
#define _SIRIUS_INBOUND_P4_

#include "dash_headers.p4"
#include "dash_service_tunnel.p4"
#include "dash_vxlan.p4"
#include "dash_acl.p4"
#include "dash_conntrack.p4"

control inbound(inout headers_t hdr,
                inout metadata_t meta,
                inout standard_metadata_t standard_metadata)
{
    action set_vm_attributes(EthernetAddress underlay_dmac,
                             IPv4Address underlay_dip,
                             bit<24> vni) {
        meta.encap_data.underlay_dmac = underlay_dmac;
        meta.encap_data.underlay_dip = underlay_dip;
        meta.encap_data.vni = vni;
    }

    action set_vm_id(bit<16> inbound_vm_id) {
        meta.inbound_vm_id = inbound_vm_id;
    }

    @name("eni_to_vm|dash_vnet")
    table eni_to_vm {
        key = {
            meta.eni_id: exact @name("meta.eni_id:eni_id");
        }

        actions = {
            set_vm_id;
        }
    }

    @name("vm|dash_vnet")
    table vm {
        key = {
            meta.inbound_vm_id: exact @name("meta.inbound_vm_id:inbound_vm_id");
        }

        actions = {
            set_vm_attributes;
        }
    }

    apply {
        eni_to_vm.apply();

        vm.apply();

        /* Check if PA is valid */

#ifdef STATEFUL_P4
            ConntrackIn.apply(0);
#endif /* STATEFUL_P4 */
#ifdef PNA_CONNTRACK
        ConntrackIn.apply(hdr, meta);
#endif // PNA_CONNTRACK

        /* ACL */
        if (!meta.conntrack_data.allow_in) {
            acl.apply(hdr, meta, standard_metadata);
        }

#ifdef STATEFUL_P4
            ConntrackOut.apply(1);
#endif /* STATEFUL_P4 */
#ifdef PNA_CONNTRACK
        ConntrackOut.apply(hdr, meta);
#endif //PNA_CONNTRACK

    }
}

#endif /* _SIRIUS_INBOUND_P4_ */
