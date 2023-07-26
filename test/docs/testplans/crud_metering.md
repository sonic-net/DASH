# Table of content

1. [Objectives](#objectives)
2. [Requirements](#requirements)
3. [Automation](#automation)
4. [Test Suites](#test-suites)
    - [Basic functional tests](#basic-functional-tests)
    - [Negative](#negative)
    - [Scale](#scale)
    - [Bulk api](#bulk-api)

---

# Objectives

Verify proper CRUD API operations and scaling for Metering - mechanism of byte counting for billing purposes.

Metering bucket - object that consists of 2 byte counters, 1 inbound (Rx) and 1 outbound (Tx) from an ENI perspective.

Metering policy - set of metering rules associated to Route tables.

Metering rules - rule that used for byte counting. Consists of an IP prefix mapped to meter-class-id and priority

# Requirements

| Item            | Expected value                                                                                                                                                                                                                                                                                                                                                             |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Metering Buckets per ENI   | 4000      |


# Automation

Test cases to automate:
1. Functional - using SAI PTF test framework.
1. Scale - to clarify
1. Negative - using SAI PTF test framework.
1. Bulk operations

# Test suites

## Basic functional tests

Positive test cases. All test cases must verify SAI-STATUS

|  #  | Test case purpose                                              | Test Class.Method                                        | Test description                                                                                                    |
|:---:|:---------------------------------------------------------------|:---------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------|
|  1  | Create DASH Metering bucket  | `CreateDeleteMeteringTest.createMeteringBucketTest` | Create DASH Metering bucket|
|  2  | Create DASH Metering policy   | `CreateDeleteMeteringTest.createMeteringPolicyTest` | Create DASH Metering policy|
|  3  | Create DASH Metering rule   | `CreateDeleteMeteringTest.createMeteringRuleTest` | Create DASH Metering rule|
|  4  | Verify DASH Metering bucket attributes getting/setting        | `SetGetMeteringTest.setGetMeteringBucketTest`                                                  | Check set/get status of Metering bucket attribute |
|  5  | Verify DASH Metering policy attributes getting/setting   | `SetGetMeteringTest.setGetMeteringPolicyTest` | Check set/get status of Metering policy attribute|
|  6  | Verify DASH Metering rule attributes getting/setting    | `SetGetMeteringTest.setGetMeteringRuleTest` | Check set/get status of Metering rule attribute |
|  7  | Verify  deletion of DASH Metering bucket  | `CreateDeleteMeteringTest.deleteMeteringBucketTest` | Delete DASH Metering bucket|
|  8  | Verify  deletion of DASH Metering policy  | `CreateDeleteMeteringTest.deleteMeteringPolicyTest` | Delete DASH Metering policy|
|  9  | Verify  deletion of DASH Metering rule  | `CreateDeleteMeteringTest.deleteMeteringRuleTest` | Delete DASH Metering rule|
|  10  | Verify  deletion of DASH Metering objects after ENI delete  | `CreateDeleteMeteringTest.deleteEniTest` | Delete DASH ENI and verify Metering Bucket, Metering Policy and Metering Rule deletion|

## Negative
Verify SAI-STATUS for creation Metering bucket, Metering policy and Metering rule with invalid data.
|  #  | Test case purpose                                              | Test Class.Method                                        | Test description                                                                                                    |
|:---:|:---------------------------------------------------------------|:---------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------|
|  1  | Create Metering bucket with invalid data | `InvalidDataMeteringTest.invalidCreateMeteringBucketTest` |  Create Metering bucket with invalid data |
|  2  | Create Metering policy with invalid data | `InvalidDataMeteringTest.invalidCreateMeteringPolicyTest` |  Create Metering policy with invalid data |
|  3  | Create Metering rule with invalid data | `InvalidDataMeteringTest.invalidCreateMeteringRuleTest` |  Create Metering rule with invalid data |


## Scale

Verifies basic scale, create/remove/recreate maximum number Metering elements per ENIs.
Should be covered in hero test.

To clarify Max number of metering policies and metering rules

| #   | Test case                                                        | Test Class.Method           |
|-----|------------------------------------------------------------------|-----------------------------|
| 1   | Create/remove a max number of DASH Metering buckets                       | - |
| 2   | Create/remove a max number of DASH Metering policies                        | - |
| 3   | Create/remove a max number of DASH Metering rules                        | - |


## Bulk api

Bulk api tests should be covered in eni_bulk.md test plan.