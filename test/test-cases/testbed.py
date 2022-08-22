TESTBED = {
    'stateless': [
        {
            'server': [
                {'addr': '10.36.77.101', 'rest': 443}
            ],
            'tgen':    [
                {
                    'type': 'keysight',
                            'interfaces': [['10.36.77.102', 1, 1],    ['10.36.77.102', 1, 2]]
                }
            ],
            'dpu':     [
                {'type': 'sku',
                 'interfaces': [['10.36.77.103', 1],    ['10.36.77.103', 1]]}
            ],
        }
    ],
    'stateful': [
        {
            'server': [{'addr': '10.36.77.107', 'rest': 10010}],
            'tgen':    [
                {
                    'type': 'keysight',
                            'interfaces': [['10.36.77.102', 2, 1],    ['10.36.77.102', 3, 2]]
                }
            ],
            'vxlan': [{
                'tgen': [['10.36.77.105', 'Ethernet1'],    ['10.36.77.106', 'Ethernet1']],
                'dpu':[['10.36.77.105', 'Ethernet2'],    ['10.36.77.106', 'Ethernet2']],
            }],
            'dpu':     [
                {'type': 'sku',
                 'interfaces': [['10.36.77.104', 1],    ['10.36.77.104', 2]]}
            ],
        }
    ],
}
