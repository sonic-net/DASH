dflt_params = {
    'SCHEMA_VER':                       '0.0.1',
    'ACL_TABLE_MAC_STEP':               '00:00:00:04:00:00',
    'ACL_POLICY_MAC_STEP':              '00:00:00:00:01:00',
    'ACL_RULES_NSG':                    1000,
    'ACL_TABLE_COUNT':                  3,
    'ENI_COUNT':                        8,
    'ENI_MAC_STEP':                     '00:00:00:18:00:00',
    'ENI_STEP':                         1,
    'ENI_L2R_STEP':                     100,
    'IP_PER_ACL_RULE':                  255,
    'IP_MAPPED_PER_ACL_RULE':           40,
    'IP_ROUTE_DIVIDER_PER_ACL_RULE':    8,       # must be 2^N

    # Params requiring cooking before use:
    'IP_STEP1':                         '0.0.0.1',
    'IP_STEP2':                         '0.0.1.0',
    'IP_STEP3':                         '0.1.0.0',
    'IP_STEP4':                         '1.0.0.0',
    'IP_STEPE':                         '0.0.0.2',
    'IP_L_START':                       '1.1.0.1',
    'IP_R_START':                       '1.128.0.1',
    'MAC_L_START':                      '00:1A:C5:00:00:01',
    'MAC_R_START':                      '00:1B:6E:00:00:01',
    'PAL':                              '221.0.1.0',
    'PAR':                              '221.0.2.100'

}
