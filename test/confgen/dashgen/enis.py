from dashgen.variables import *


def generate():
    print('    ' + os.path.basename(__file__))
    enis = []
    for eni_index in range(1, ENI_COUNT+1):
        local_mac = str(macaddress.MAC(int(MAC_L_START)+(eni_index - 1)*int(macaddress.MAC(ENI_MAC_STEP)))).replace('-', ':')

        acl_tables_in = []
        acl_tables_out = []

        for table_index in range(1, (ACL_TABLE_COUNT*2+1)):
            table_id = eni_index * 1000 + table_index

            stage = (table_index - 1) % 3 + 1
            if table_index < 4:
                acl_tables_in.append(
                    {
                        "acl-group-id": "acl-group-%d" % table_id,
                        "stage": stage
                    }
                )
            else:
                acl_tables_out.append(
                    {
                        "acl-group-id": "acl-group-%d" % table_id,
                        "stage": stage
                    }
                )

        enis.append(
            {
                'ENI:%d' % eni_index: {
                    'eni-id': 'eni-%d' % eni_index,
                    'mac': local_mac,
                    'vpcs': [
                        eni_index
                    ],
                    "acls-v4-in": acl_tables_in,
                    "acls-v4-out": acl_tables_out,
                    "route-table-v4": "route-table-%d" % eni_index
                },
            }
        )
    return {"enis": enis}
