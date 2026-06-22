import argparse
import collections
import itertools
import json
import sys
import textwrap

# From https://stackoverflow.com/questions/12670395/json-encoding-very-long-iterators
# Other articles to consider:
# https://stackoverflow.com/questions/21663800/python-make-a-list-generator-json-serializable/31517812#31517812
# https://stackoverflow.com/questions/1871685/in-python-is-there-a-way-to-check-if-a-function-is-a-generator-function-before
# https://stackoverflow.com/questions/6416538/how-to-check-if-an-object-is-a-generator-object-in-python
# https://pypi.org/project/json-stream/
# https://pythonspeed.com/articles/json-memory-streaming/


class IterEncoder(json.JSONEncoder):
    """
    JSON Encoder that encodes iterators as well.
    Write directly to file to use minimal memory
    """
    class FakeListIterator(list):
        def __init__(self, iterable):
            self.iterable = iter(iterable)
            try:
                self.firstitem = next(self.iterable)
                self.truthy = True
            except StopIteration:
                self.truthy = False

        def __iter__(self):
            if not self.truthy:
                return iter([])
            return itertools.chain([self.firstitem], self.iterable)

        def __len__(self):
            raise NotImplementedError("Fakelist has no length")

        def __getitem__(self, i):
            raise NotImplementedError("Fakelist has no getitem")

        def __setitem__(self, i):
            raise NotImplementedError("Fakelist has no setitem")

        def __bool__(self):
            return self.truthy

    def default(self, o):
        if isinstance(o, collections.abc.Iterable):
            return type(self).FakeListIterator(o)
        return super().default(o)


def writeListFileIter(config, format, filename='<stdout>'):
    if filename == '<stdout>':
        writeListFpIter(config, format, sys.stdout)
    else:
        with open(filename, "wt") as file:
            writeListFpIter(config, format, fp)


def writeListFpIter(config, format, fp):
    if format == 'json':
        json.dump(config, fp, cls=IterEncoder, indent=2, separators=(',', ': '))
    else:
        raise NotImplementedError('ERROR: unsupported format %s' % format)
# TODO - consider generic recursive approach


def writeDictFileIter(config, format, filename='<stdout>'):
    def _writeDictFileIter(config, fp):
        fp.write('{\n')
        first = True
        for key, list in config.items():
            if not first:
                fp.write(',\n')
            fp.write('  "%s":\n' % key)
            json.dump(list, fp, cls=IterEncoder, indent=2, separators=(',', ': '))
            first = False
        fp.write('\n}\n')

    if format == 'json':
        print('Writing the %s config to %s...' % (format, filename), file=sys.stderr)
        if filename == '<stdout>':
            fp = sys.stdout
            _writeDictFileIter(config, fp)
        else:
            with open(filename, 'wt') as fp:
                _writeDictFileIter(config, fp)
    else:
        raise NotImplementedError('ERROR: unsupported format %s' % format)


def commonArgParser():
    parser = argparse.ArgumentParser(description='Generate DASH Configs',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=textwrap.dedent('''
Usage:
=========
./generate.d.py                - generate output to stdout using uber-generator
./generate.d.py -o tmp.json    - generate output to file tmp.json
./generate.d.py -o /dev/null   - generate output to nowhere (good for testing)
./generate.d.py -c list        - generate just the list items w/o parent dictionary
dashgen/aclgroups.py [options] - run one sub-generator, e.g. acls, routetables, etc.
                               - many different subgenerators available, support same options as uber-generator

Passing parameters. Provided as Python dict, see dflt_params.py for available items
Can use defaults; override from file; override again from cmdline (all 3 sources merged).
================
./generate.d.py -d                          - display default parameters and quit
./generate.d.py -d -P PARAMS                - use given parameters, display and quit; see dflt_params.py for template
./generate.d.py -d -p PARAM_FILE            - override with parameters from file; display only
./generate.d.py -d -p PARAM_FILE -P PARAMS  - override with params from file and cmdline; display only
./generate.d.py -p PARAM_FILE -P PARAMS     - override with params from file and cmdline; generate output

Examples:
./generate.d.py -d -p params_small.py -P "{'ENI_COUNT': 16}"  - use params_small.py but override ENI_COUNT; display params
./generate.d.py -p params_hero.py -o tmp.json                 - generate full "hero test" scale config as json file
dashgen/vpcmappingtypes.py -m -M "Kewl Config!"               - generate dict of vpcmappingtypes, include meta with message            



            '''))

    # parser.add_argument('-f', '--format', choices=['json', 'yaml'], default='json',
    parser.add_argument('-f', '--format', choices=['json'], default='json',
                        help='Config output format.')

    parser.add_argument('-c', '--content', choices=['dict', 'list'], default='dict',
                        help='Emit dictionary (with inner lists), or list items only')

    parser.add_argument('-d', '--dump-params', action='store_true',
                        help='Just dump paramters (defaults with user-defined merged in')

    parser.add_argument('-m', '--meta', action='store_true',
                        help='Include metadata in output (only if "-c dict" used)')

    parser.add_argument('-M', '--msg', default='', metavar='"MSG"',
                        help='Put MSG in metadata (only if "-m" used)')

    parser.add_argument('-P', '--set-params', metavar='"{PARAMS}"',
                        help='use parameter dict from cmdline, partial is OK; overrides defaults & from file')

    parser.add_argument('-p', '--param-file', metavar='PARAM_FILE',
                        help='use parameter dict from file, partial is OK; overrides defaults')

    parser.add_argument(
        '-o', '--output', default='<stdout>', metavar='OFILE',
        help="Output file (default: standard output)")

    return parser


def common_parse_args(self):
    parser = commonArgParser()
    self.args = parser.parse_args()

    # Prams from file override defaults; params from cmd-line override all
    params = {}
    if self.args.param_file:
        with open(self.args.param_file, 'r') as fp:
            params = eval(fp.read())
    if self.args.set_params:
        params.update(eval(self.args.set_params))
    self.mergeParams(params)

    if self.args.dump_params:
        print(self.params_dict)
        exit()


def common_output(self):
    if self.args.content == 'dict':
        d = self.toDict()
        if (self.args.meta):
            d.update(self.getMeta(self.args.msg))
        # streaming dict output:
        writeDictFileIter(d, self.args.format, self.args.output)

    elif self.args.content == 'list':
        # streaming list output:
        writeListFileIter(self.items(), self.args.format, self.args.output)
    else:
        raise Exception("Unknown content specifier: '%s'" % self.args.content)


def common_main(self):
    common_parse_args(self)
    common_output(self)
