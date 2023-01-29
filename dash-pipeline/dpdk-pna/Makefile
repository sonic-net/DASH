DSTDIR=out

# These command line options can be added if/when p4c-dpdk is enhanced
# to support the code that is #ifdef'd out when these symbols are not
# defined.  Search for these symbols in dash_pipeline.p4 for more
# details.

# -DDPDK_PNA_SEND_TO_PORT_FIX_MERGED
# -DDPDK_SUPPORTS_DIRECT_COUNTER_ON_WILDCARD_KEY_TABLE

dpdk-pna:
	mkdir -p $(DSTDIR)
	p4c-dpdk -DPNA_CONNTRACK --dump ./$(DSTDIR) --pp ./$(DSTDIR)/dash_pipeline.pp.p4 -o ./$(DSTDIR)/dash_pipeline.spec --arch pna --bf-rt-schema ./$(DSTDIR)/dash_pipeline.p4.bfrt.json --p4runtime-files ./$(DSTDIR)/dash_pipeline.p4.p4info.txt dash_pipeline.p4
