from ipaddress import IPv6Address, ip_address, IPv4Address

def create_ip_list(value, count, mask=32, incr=1):
    '''
        Create a list of ips based on the count provided
        Parameters:
            value: start value of the list
            count: number of ips required
            mask: subnet mask for the ips to be created
            incr: increment value of the ip
    '''
    ip_list = [value]
    for i in range(1, count):
        if ip_address(str(value)).version == 4:
            incr1 = pow(2, (32-int(mask))) * incr
            value = (IPv4Address(str(value)) + incr1).compressed
        elif ip_address(str(value)).version == 6:
            if mask == 32:
                mask = 64
            incr1 = pow(2, (128-int(mask))) + incr
            value = (IPv6Address(str(value)) + incr1).compressed
        ip_list.append(value)

    return ip_list