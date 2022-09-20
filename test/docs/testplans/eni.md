# Table of content

1. [Objectives](#objectives)
2. [Requirements](#requirements)
3. [Automation](#automation)
4. [Test Suites](#test-suites)
    - [ENI creation](#eni-creation)
    - [ENI removal](#eni-removal)
    - [ENI scale](#eni-scale)

---

# Objectives

Verify proper CRUD API operations and scaling for Elastic Network Interface (ENI).

# Requirements

| Item            | Expected value                                                                                                                                                                                                                                                                                                                                                             |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ENI per card    | 64                                                                                                                                                                                                                                                                                                                                                                         |
| Bulk operations | Yes                                                                                                                                                                                                                                                                                                                                                                        |
| Admin state     | When the ENI is admin-state down, the packets destined to this ENI shall be dropped.                                                                                                                                                                                                                                                                                       |
| Remove          | - During ENI delete, implementation must support ability to delete all mappings or routes in a single API call.<br>- Deleting an object that doesn't exists shall not return an error and shall not perform any force-deletions or delete dependencies implicitly. Sonic implementation shall validate the entire API as pre-checks before applying and return accordingly |
| Memory          | Flexible memory allocation for ENI and not reserve max scale during initial create. (To allow oversubscription)                                                                                                                                                                                                                                                            |
| Error handling  | Implementation must not have silent failures for APIs.                                                                                                                                                                                                                                                                                                                     |

# Automation

Test cases are automated using SAI PTF test framework.

# Test suites

## ENI creation

Verifies create operations, an association with VNI, MAC.

| #   | Test case                                                     | Test Class.Method                                                                                 |
|-----|---------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| 1   | create inbound/outbound DASH ACL groups entries               | `CreateDeleteEniTest.createInOutAclGroupsTest`                                                    |
| 2   | create VNET entry                                             | `CreateDeleteEniTest.createVnetTest`                                                              |
| 3   | create Direction lookup entry                                 | `CreateDeleteEniTest.createDirectionLookupTest`                                                   |
| 4   | create ENI entry                                              | `CreateDeleteEniTest.createEniTest`                                                               |
| 5   | create ENI Ether address map entry                            | `CreateDeleteEniTest.createEniEtherAddressMapTest`                                                |
| 6   | create Inbound routing entry                                  | `CreateDeleteEniTest.createInboundRoutingEntryTest`                                               |
| 7   | create PA validation entry                                    | `CreateDeleteEniTest.createPaValidationTest`                                                      |
| 8   | create Outbound routing entry                                 | `CreateDeleteEniTest.createOutboundRoutingEntryTest`                                              |
| 9   | create Outbound CA to PA entry                                | `CreateDeleteEniTest.createCa2PaEntryTest`                                                        |
| 10  | verify DASH ACL Group entry attributes getting/setting        | `CreateDeleteEniTest.dashAclGroupAttributesTest`                                                  |
| 11  | verify VNET entry attributes getting/setting                  | `CreateDeleteEniTest.vnetAttributesTest`                                                          |
| 12  | verify Direction lookup entry attributes getting/setting      | `CreateDeleteEniTest.directionLookupAttributesTest`                                               |
| 13  | verify Inbound routing entry attributes getting/setting       | `CreateDeleteEniTest.inboundRoutingEntryAttributesTest`                                           |
| 14  | verify ENI attributes getting/setting                         | `CreateDeleteEniTest.eniGetAttributesTest`<br/>  `CreateDeleteEniTest.eniSetAndGetAttributesTest` |
| 15  | verify ENI Ether address map entry attributes getting/setting | `CreateDeleteEniTest.eniEtherAddressMapAttributesTest`                                            |
| 16  | verify PA validation entry attributes getting/setting         | `CreateDeleteEniTest.paValidationEntryAttributesTest`                                             |
| 17  | verify Outbound routing entry attributes getting/setting      | `CreateDeleteEniTest.outboundRoutingEntryAttributesTest`                                          |
| 18  | verify Outbound CA to PA entry attributes getting/setting     | `CreateDeleteEniTest.outboundCa2PaEntryAttributesTest`                                            |
    
## ENI removal

Verifies remove operations.

| #   | Test case                                                                                                                                                           | Test Class.Method                                       |
|-----|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|
| 1   | normal delete:<br>verify deletion of: inbound/outbound DASH ACL groups, VNET, ENI, ENI Ether address map entry, PA validation entry, inbound/outbound routing entry | Is a part of `CreateDeleteEniTest.destroy_teardown_obj` |
| 2   | error if mapped rules exist:<br>verify VNET cannot be deleted when map exist                                                                                        | `CreateDeleteEniTest.deleteVnetWhenMapExistTest`        |
| 3   | duplicated deletion<br>no errors expected                                                                                                                           | Is a part of `CreateDeleteEniTest.destroy_teardown_obj` |
| 4   | ENI deletion when map exists: no errors, related entries also deleted(To clarify: list of entries that must be deleted)                                             | `CreateDeleteEniTest.deleteEniWhenMapExistTest`         |
| 5   | normal bulk delete                                                                                                                                                  | -                                                       |
| 6   | bulk delete does not remove any if there is a mapping for some ENI                                                                                                  | -                                                       |

## ENI scale. 

Verifies basic ENI scale, create/remove/recreate maximum number of ENIs .

| #   | Test case                                                        | Test Class.Method           |
|-----|------------------------------------------------------------------|-----------------------------|
| 1   | Create/remove a max number of ENI entries                        | `EniScaleTest.eniScaleTest` |
| 2   | Recreate (repeated creation/removal a max number of ENI entries) | `EniScaleTest.eniScaleTest` |

## ENI negative

|  #  | Test case purpose                                              | Test Class.Method                                        | Test description                                                                                                    |
|:---:|:---------------------------------------------------------------|:---------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------|
|  1  | Verifies failure in case of creation the same ENIs in one VNET | `CreateTwoSameEnisNegativeTest`.<br/> `enisCreationTest` | Create two same ENIs in the single VNET and verify creation failure.<br/> **To clarify:** exact step to expect failure |
