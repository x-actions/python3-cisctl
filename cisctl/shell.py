#  Copyright 2022 xiexianbin.cn
#  All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#         http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Command-line interface for Sync Container Images.
ref: https://github.com/openstack/python-novaclient/blob/master/novaclient/shell.py
"""

import argparse
import logging
import sys

import cisctl
from cisctl import exception
from cisctl import utils

logger = logging.getLogger(__name__)


class CISctlArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super(CISctlArgumentParser, self).__init__(*args, **kwargs)

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.
        """
        self.print_usage(sys.stderr)

    def _get_option_tuples(self, option_string):
        """returns (action, option, value) candidates for an option prefix
        """
        option_tuples = (super(CISctlArgumentParser, self)
                        ._get_option_tuples(option_string))
        if len(option_tuples) > 1:
            normalizeds = [option.replace('_', '-') for action, option, value in option_tuples]
            if len(set(normalizeds)) == 1:
                return option_tuples[:1]
        return option_tuples


class CISctlShell(object):

    def __init__(self):
        self.client_logger = None

    def get_base_parser(self, argv):
        parser = CISctlArgumentParser(
            prog='cisctl',
            description=__doc__.strip(),
            epilog='See "cisctl help COMMAND" '
                'for help on a specific command.',
            add_help=False,
            formatter_class=CISctlHelpFormatter,
        )

        # Global arguments
        parser.add_argument(
            '-h', '--help',
            action='store_true',
            help=argparse.SUPPRESS,
        )

        parser.add_argument('--version',
                            action='version',
                            version=cisctl.__version__)

        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help="Print debugging output.")

        parser.set_defaults(func=self.do_help)
        parser.set_defaults(command='')

        return parser

    def get_subcommand_parser(self, do_help=False, argv=None):
        parser = self.get_base_parser(argv)

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')

        v1shell = "cisctl.v1.shell"
        __import__(v1shell)
        actions_module = sys.modules[v1shell]

        self._find_actions(subparsers, actions_module, do_help)
        self._find_actions(subparsers, self, do_help)

        self._add_bash_completion_subparser(subparsers)

        return parser

    def _add_bash_completion_subparser(self, subparsers):
        subparser = subparsers.add_parser(
            'bash_completion',
            add_help=False,
            formatter_class=CISctlHelpFormatter
        )
        self.subcommands['bash_completion'] = subparser
        subparser.set_defaults(func=self.do_bash_completion)

    def _find_actions(self, subparsers, actions_module, do_help):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            # I prefer to be hyphen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''

            action_help = desc.strip()
            arguments = getattr(callback, 'arguments', [])
            groups = {}

            subparser = subparsers.add_parser(
                command,
                help=action_help,
                description=desc,
                add_help=False,
                formatter_class=CISctlHelpFormatter)
            subparser.add_argument(
                '-h', '--help',
                action='help',
                help=argparse.SUPPRESS,
            )
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                kwargs = kwargs.copy()
                group = kwargs.pop("group", None)
                if group:
                    if group not in groups:
                        groups[group] = (
                            subparser.add_mutually_exclusive_group()
                        )
                    kwargs['dest'] = kwargs.get('dest', group)
                    groups[group].add_argument(*args, **kwargs)
                else:
                    subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def setup_debugging(self, debug):
        if not debug:
            return

        streamformat = "%(levelname)s (%(module)s:%(lineno)d) %(message)s"
        # Set up the root logger to debug so that the submodules can
        # print debug messages
        logging.basicConfig(level=logging.DEBUG,
                            format=streamformat)
        logging.getLogger('iso8601').setLevel(logging.WARNING)

        self.client_logger = logging.getLogger(cisctl.__name__)
        ch = logging.StreamHandler()
        self.client_logger.setLevel(logging.DEBUG)
        self.client_logger.addHandler(ch)

    def main(self, argv):
        # Parse args once to find version and debug settings
        parser = self.get_base_parser(argv)
        (args, args_list) = parser.parse_known_args(argv)

        self.setup_debugging(args.debug)
        do_help = args.help or not args_list or args_list[0] == 'help'

        subcommand_parser = self.get_subcommand_parser(
            do_help=do_help, argv=argv)
        self.parser = subcommand_parser

        if args.help or not argv:
            subcommand_parser.print_help()
            return 0

        args = subcommand_parser.parse_args(argv)

        # Short-circuit and deal with help right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0
        elif args.func == self.do_bash_completion:
            self.do_bash_completion(args)
            return 0

        # TODO(xiexianbin): may be inject http client
        args.func(args)

    def do_bash_completion(self, _args):
        """
        Prints all of the commands and options to stdout so that the
        cisctl.bash_completion script doesn't have to hard code them.
        """
        commands = set()
        options = set()
        for sc_str, sc in self.subcommands.items():
            commands.add(sc_str)
            for option in sc._optionals._option_string_actions.keys():
                options.add(option)

        commands.remove('bash-completion')
        commands.remove('bash_completion')
        print(' '.join(commands | options))

    @utils.arg(
        'command',
        metavar='<subcommand>',
        nargs='?',
        help='Display help for <subcommand>.')
    def do_help(self, args):
        """
        Display help about this program or one of its subcommands.
        """
        if args.command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exception.CommandError(f"'{args.command}' is not a valid subcommand")
        else:
            self.parser.print_help()


class CISctlHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog, indent_increment=2, max_help_position=32,
            width=None):
        super(CISctlHelpFormatter, self).__init__(
            prog, indent_increment,  max_help_position, width)

    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(CISctlHelpFormatter, self).start_section(heading)


def main(argv=sys.argv[1:]):
    try:
        CISctlShell().main(argv)
    except Exception as exc:
        logger.debug(exc, exc_info=1)
        print(f'ERROR ({exc.__class__}): {exc.__str__()}', file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("... terminating cisctl", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
