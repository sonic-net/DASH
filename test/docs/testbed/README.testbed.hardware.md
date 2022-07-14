
## Physical topology


![Datacenter network](../../images/dash-testbed-tests.svg)

Key components in the physical connection:
* DPU cards
* DPU host server (2+ PCI 4.0 16x slots)
* Hardware-based packet generator with minimum of 2 x 100G ports. 
    <br>Example:
    * Keysight XGS12-HSL Chassis
    * Keysight Novus 100G load module
    * Keysight CloudStorm load module (1x for up to 4.5M CPS or 2x for up to 9M CPS)
* 2x 100G switches that can do vlan to vxlan translation. Example: Cisco Nexus 3232C, Accton7816_64X
* Test Server to run the test case and host the test environment[^1]


## Testbed Server[^2] specs
- CPU: 16+ cores (Intel Xeon Scalable gen2+ or AMD EPYC gen2+)
- RAM: 64G+
- Storage: 2T NVMe drive

[^1]: test server and DPU host server can be one and the same
[^2]: it can also be a VM but nested virtualization will have to be enabled
