#!/bin/bash
# To be run inside saithrift-client container, assumes SAI repo portions exist under /SAI directory

SCRIPT=$(basename $0)
TARGET="bmv2"  # TODO: add no target by default and remove -H
TRAFFIC="bidir"
CONNECTION="tcp"
TEST_DIR="$(dirname $0)"
EXTRA_PARAMETERS=""
INTERFACES="veth1,veth3"
TIMEOUT=1800
TEST_PARAMS=""

function show_help_and_exit()
{
    echo "Usage ${SCRIPT} [options]"
    echo "    options with (*) must be provided"
    echo "    -h -?                   : get this help"
    echo "    -s <server ip>          : specify thrift server IP address (e.g. -s 192.168.1.1)"
    echo "    -p <port map file path> : specify path to port map file (e.g. -p /tests-dev/config/front-map.ini)"
    echo "    -c <port config path>   : specify path to port config file (e.g. -c /tests-dev/config/port-map.ini)"
    echo "    -U                      : specify to run PTF underlay test cases. (default: run PTF overlay test cases)"
    echo "    -I <interfaces>         : specify comma-separated DUT 2 interfaces names (default: veth1,veth3)"
    echo "    -H                      : specify if tests are run on real hardware"
    echo "    -T <target>             : specify any specific target platform (default: bmv2)"
    echo "    -b <traffic type>       : specify traffic type for verification: bidir|monodir|no (default: bidir)"
    echo "    -C <connection type>    : specify connection type protocol for traffic verification: tcp|udp|icmp"
    echo "    -e <parameters>         : specify extra parameter(s) (default: none)"
    echo -e "    -t <timeout>            : specify timeout for test case execution\n"

    exit $1
}

function validate_parameters()
{
    RET=0

    if [[ ${#iface_array[@]} < 2 ]] || [[ ${#iface_array[@]} > 2 ]]; then
        echo -e "\nTwo interfaces names must be specified (e.g. -I iface1, iface2)."
        echo -e "Instead received - ${#iface_array[@]}: $INTERFACES\n"
        RET=1
    fi

    if [[ ${RET} != 0 ]]; then
        show_help_and_exit ${RET}
    fi
}

while getopts "h?UHT:I:s:p:c:b:C:e:t:" opt; do
    case ${opt} in
        h|\? )
            show_help_and_exit 0
            ;;
        U )
            TEST_DIR="/SAI/ptf"
            ;;
        T )
            TARGET=${OPTARG}
            ;;
        H )
            TARGET=""
            ;;
        I )
            INTERFACES=${OPTARG}
            ;;
        s )
            TEST_PARAMS="${TEST_PARAMS}thrift_server='${OPTARG}';"
            ;;
        p )
            TEST_PARAMS="${TEST_PARAMS}port_map_file='${OPTARG}';"
            ;;
        c )
            TEST_PARAMS="${TEST_PARAMS}port_config_ini='${OPTARG}';"
            ;;
        b )
            TRAFFIC=${OPTARG}
            ;;
        C )
            CONNECTION=${OPTARG}
            ;;
        e )
            EXTRA_PARAMETERS="${EXTRA_PARAMETERS} ${OPTARG}"
            ;;
        t )
            TIMEOUT=${OPTARG}
    esac
done

IFS="," read -a iface_array <<< $INTERFACES

validate_parameters

set -x
ptf \
    --test-dir ${TEST_DIR}\
    --pypath /SAI/ptf \
    --interface 0@${iface_array[0]} \
    --interface 1@${iface_array[1]} \
    --test-case-timeout=${TIMEOUT} \
    --test-params="connection='${CONNECTION}';target='${TARGET}';traffic_check='${TRAFFIC}';${TEST_PARAMS}" \
    ${EXTRA_PARAMETERS}
