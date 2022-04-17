---
description: Packet transforms
last update: 04/14/2022
---

# Packet transforms

- [VM to VM (in VNET) communication](#vm-to-vm-in-vnet-communication)
  - [Old image (VM to VM)](#old-image-vm-to-vm)
  - [New image (VM to VM)](#new-image-vm-to-vm)
- [Internal Load balancer (in VNET) communication](#internal-load-balancer-in-vnet-communication)
  - [Old image (VM to VM LB)](#old-image-vm-to-vm-lb)
  - [New image (VM to VM LB)](#new-image-vm-to-vm-lb)
- [Private Link](#private-link)
  - [Old image (PL)](#old-image-pl)
  - [New image (PL)](#new-image-pl)
- [Private Link Service](#private-link-service)
  - [Old image (PLS)](#old-image-pls)
  - [New image (PLS)](#new-image-pls)
- [Service Tunneling](#service-tunneling)
  - [Old image (ST)](#old-image-st)
  - [New image (ST)](#new-image-st)
- [Inbound from LB](#inbound-from-lb)
  - [Old image (IFLB)](#old-image-iflb)
  - [New image (IFLB)](#new-image-iflb)
- [Outbound NAT - L4](#outbound-nat---l4)
  - [Old image (outNAT)](#old-image-outnat)
  - [New image (outNAT)](#new-image-outnat)


## VM to VM (in VNET) communication

### Old image (VM to VM) 

<details>
  <summary>Click on the arrow to display or hide old image</summary>

![VMtoVM](../../images/sdn/vm_to_vm.png)

</details>

### New image (VM to VM) 

![VMtoVM](../../images/sdn/sdn-packet-transforms-vm-to-vm.svg)

## Internal Load balancer (in VNET) communication

### Old image (VM to VM LB) 

<details>
  <summary>Click on the arrow to display or hide old image</summary>
  
![VMtoVMloadBalancer](../../images/sdn/vm_to_ilb.png)

</details>

### New image (VM to VM LB) 

![VMtoVMloadBalancer](../../images/sdn/sdn-packet-transforms-vm-internal-load-balancer.svg)

## Private Link

### Old image (PL) 

<details>
  <summary>Click on the arrow to display or hide old image</summary>

![PL](../../images/sdn/private_link.png)

</details>

### New image (PL)

![PL](../../images/sdn/sdn-packet-transforms-private-link.svg)

## Private Link Service

### Old image (PLS)

<details>
  <summary>Click on the arrow to display or hide old image</summary>

![PLS](../../images/sdn/private_link_service.png)

</details>

### New image (PLS)

![PL](../../images/sdn/sdn-packet-transforms-private-link-service.svg)

## Service Tunneling

### Old image (ST)

<details>
  <summary>Click on the arrow to display or hide old image</summary>

![ST](../../images/sdn/service_tunneling.png)

</details>

### New image (ST)

![ST](../../images/sdn/sdn-packet-transforms-service-tunneling.svg)

## Inbound from LB

### Old image (IFLB)

<details>
  <summary>Click on the arrow to display or hide old image</summary>


![InbfromLB](../../images/sdn/inbound_frm_ilb.png)

</details>

### New image (IFLB)

![InbfromLB](../../images/sdn/sdn-packet-transforms-inbound-from-lb.svg)

## Outbound NAT - L4

### Old image (outNAT)

<details>
  <summary>Click on the arrow to display or hide old image</summary>


![OutNATL4](../../images/sdn/outbound_nat_l4.png)

(L3 works in same way except port re-write)

</details>

### New image (outNAT)

![OutNATL4](../../images/sdn/sdn-packet-transforms-outbound-nat-l4.svg)

> [!NOTE]
> L3 works in same way except port re-write