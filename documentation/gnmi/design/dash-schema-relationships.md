# DASH Schema Relationships
The [figure below](#schema_relationships) illustrates the various schema and their transformations into the various SONiC "domains," including:
* gNMI northbound API, which useds YANG to specify schema
* Redis APP_DB and DASH_APP_DB, which use [ABNF](https://github.com/Azure/SONiC/blob/master/doc/mgmt/Management%20Framework.md#12-design-overview) schema definition language
* [sonic-cfggen](https://github.com/Azure/sonic-buildimage/blob/master/src/sonic-config-engine/sonic-cfggen) JSON and YAML import/export formats
* [SAI](https://github.com/Azure/DASH/tree/main/SAI) table and attribute objects

All the schema formats are just different ways to represent the same "intent" and cater to the domain they're used in.

* The gNMI, sonic-cfggen and [DASH]_APP_DB schema are all equivalent and can be translated direclty from one to the other without having to change fundamental object structures or quantities.

* The ASIC-DB and SAI table/attribute objects are likewise "equivalent" and differ only in their representation.

* The `orchagent` and `dashorch` perform object transformations; for example, a single entry in the APP_DB can result in multiple ASIC_DB objects with specific relationships. It also performs necessary sequencing and other business logic.

# Canonical Test Data

### Figure - Schema Relationships

![Schema Relationships](images/dash-high-level-design-schema.svg)

# References
* https://github.com/Azure/SONiC/blob/master/doc/mgmt/Management%20Framework.md
* https://github.com/Azure/sonic-buildimage/blob/master/src/sonic-config-engine/sonic-cfggen
* https://github.com/Azure/DASH/tree/main/SAI