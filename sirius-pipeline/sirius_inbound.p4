#ifndef _SIRIUS_INBOUND_P4_
#define _SIRIUS_INBOUND_P4_

#include "sirius_headers.p4"
#include "sirius_service_tunnel.p4"
#include "sirius_vxlan.p4"
#include "sirius_acl.p4"

control inbound(inout headers_t hdr,
                inout metadata_t meta,
                inout standard_metadata_t standard_metadata)
{
    action set_eni(bit<16> eni) {
        meta.eni = eni;
    }

    table eni_lookup_to_vm {
        key = {
            hdr.ethernet.dst_addr : exact @name("hdr.ethernet.dst_addr:dmac");
        }

        actions = {
            set_eni;
        }
    }

    action set_vm_attributes(EthernetAddress underlay_dmac,
                             IPv4Address underlay_dip,
                             bit<24> vni) {
        meta.encap_data.underlay_dmac = underlay_dmac;
        meta.encap_data.underlay_dip = underlay_dip;
        meta.encap_data.vni = vni;
    }

    action set_vm_id(bit<16> vm_id) {
        meta.vm_id = vm_id;
    }

    table eni_to_vm {
        key = {
            meta.eni: exact @name("meta.eni:eni");
        }

        actions = {
            set_vm_id;
        }
    }

    table vm {
        key = {
            meta.vm_id: exact @name("meta.vm_id:vm_id");
        }

        actions = {
            set_vm_attributes;
        }
    }

    apply {
        eni_lookup_to_vm.apply();

        eni_to_vm.apply();

        vm.apply();

        /* Check if PA is valid */

#ifdef STATEFUL_P4
            ConntrackIn.apply(0);
#endif /* STATEFUL_P4 */

        /* ACL */
        if (meta.conntrack_data.allow_in) {
            acl.apply(hdr, meta, standard_metadata);
        }

#ifdef STATEFUL_P4
            ConntrackOut.apply(1);
#endif /* STATEFUL_P4 */

        vxlan_encap(hdr,
                    meta.encap_data.underlay_dmac,
                    meta.encap_data.underlay_smac,
                    meta.encap_data.underlay_dip,
                    meta.encap_data.underlay_sip,
                    hdr.ethernet.dst_addr,
                    meta.encap_data.vni);
    }
}

#endif /* _SIRIUS_INBOUND_P4_ */
