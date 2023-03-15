def config_l1_properties(dataplane, usd_speed):

    """
    This function used to configure L1 properties such as speed of the ports
    Sometimes enabling auto_negotiation would fail to bring the ports up
    So we are disabling auto_nagotiation when setting speed
    """

    ly = dataplane.configuration.layer1.layer1(name="ly")[-1]
    ly.port_names = [p.name for p in dataplane.configuration.ports]
    val = getattr(ly , usd_speed )
    setattr(ly , "speed", val)  
    ly.ieee_media_defaults = False
    ly.auto_negotiation.rs_fec = True
    ly.auto_negotiation.link_training = False
    ly.auto_negotiate = False

def check_flow_tx_rx_frames_stats(dataplane, flow_name):

    """
    This function used to check tx and rx packet values of a given flow
    This matches the tx and rx packet and if matches returns true
    """

    req = dataplane.api.metrics_request()
    req.flow.flow_names = [flow_name]
    flow_stats = dataplane.api.get_metrics(req)
    print("statistics : {}".format(flow_stats))
    frames_tx = sum([m.frames_tx for m in flow_stats.flow_metrics])
    frames_rx = sum([m.frames_rx for m in flow_stats.flow_metrics])
    return frames_tx == frames_rx

def check_port_tx_rx_frames_stats(dataplane, port_name):
    """
    This function used to check tx and rx packet values of a given port
    This matches the tx and rx packet and if matches returns true
    """

    req = dataplane.api.metrics_request()
    req.port.port_names = [port_name]
    req.port.column_names = [req.port.FRAMES_TX, req.port.FRAMES_RX]
    port_stats = dataplane.api.get_metrics(req)
    print("statistics : {}".format(port_stats))
    frames_tx = sum([m.frames_tx for m in port_stats.port_metrics])
    frames_rx = sum([m.frames_rx for m in port_stats.port_metrics])
    return frames_tx == frames_rx

def check_bgp_neighborship_established(dataplane):
    """
    This function used to verify BGP neighborships Established. 
    It Verifies all the configured BGP protocol sessions are up. 
    If any one of the BGP protocol session down, it returs false  
    """

    req =dataplane.api.metrics_request()
    req.bgpv4.column_names = ["session_state"]
    results = dataplane.api.get_metrics(req)
    ok = []
    for r in results.bgpv4_metrics:
        ok.append(r.session_state == "up")
    return all(ok)


def check_ping(dataplane, ip_obj_name, ip, addr_family="ipv4"):
    """
    This function will verify ping connectivity between TGEN and DUT
    Ping request would be sent from TGEN
    ip_obj_name is source ip stack name from where we wanted to send ping
    ip is DUT ip address which connectivity to be tested from TGEN
    """
    req = dataplane.api.ping_request()
    if addr_family == "ipv4":

        p1 = req.endpoints.ipv4()
    else:
        p1 = req.endpoints.ipv6()
    p1.src_name = ip_obj_name
    p1.dst_ip   = ip
    responses = dataplane.api.send_ping(req).responses
    for resp in responses :
        if resp.src_name == ip_obj_name and resp.dst_ip == ip:
            return True
    else:
        return False

def start_traffic(dataplane, flow_name=None):
    """ Start traffic flow(s) which are already configured.
    """
    ts = dataplane.api.transmit_state()
    ts.state = ts.START
    if flow_name != None:
        ts.flow_names = [flow_name]
    res = dataplane.api.set_transmit_state(ts)
    assert dataplane.api_results_ok(res), res
    

