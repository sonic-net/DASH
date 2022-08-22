# VNET to VNET 

The SONiC-DASH testbed provides a common test platform to examine an extensive collection of test cases and allow ease of duplication and modification.  The directory structure is arranged for configuring a variety of test SKUs and to reduce testing design time.

The files found within this directory serve the following purpose:
1. Define a guide for expanding DASH test scenarios.
2. Generate two test outcomes using separate traffic generation tools and collecting results using one testing framework: PyTest.
3. Demonstrate testbed setup requires minimum configuration as the test platform provides tools and configuration out of the box.
4. Test one seeks to find the maximum capability of the device under test to measure the raw bandwidth by identifying the Packets Per Second.
5. Test two's goal is to discover the maximum number of functioning connections that can be established per second.


# test cases

| Test case                                      | Description                                               |
| ---------------------------------------------- | --------------------------------------------------------- |
| [vxlan_1vpc_1ip](README.vxlan_1vpc_1ip.md)     | performance numbers for best case scenario                |
