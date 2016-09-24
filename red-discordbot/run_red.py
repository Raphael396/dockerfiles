#!/usr/bin/python

import socket
import os
import sys
import argparse
import traceback
from signal import SIGINT
from subprocess import Popen, TimeoutExpired
from time import time

DEFAULT_RED_ARGS = "--no-prompt"
STOP_WAIT = 30
DEFAULT_WATCHDOG_SECS = 90


class MissingConfiguration(Exception):
    pass


def stop_p(p):
    if p.poll() is None:
        try:
            print('Attempting to stop bot gracefully...')
            p.send_signal(SIGINT)
            return p.wait(STOP_WAIT)
        except TimeoutExpired:
            try:
                print('Graceful stop timed out, sending SIGTERM...')
                p.terminate()
                return p.wait(STOP_WAIT)
            except TimeoutExpired:
                print('SIGTERM stop failed, killing the bot...')
                p.kill()
                return p.wait()


def start(red_py, args):
    red_call = [sys.executable, red_py]
    red_call.extend(args.args.split())

    watchdog = args.watchdog or os.environ.get('RED_WATCHDOG', False) in [1, '1', True]

    if watchdog:
        sockname = os.path.join(os.getcwd(), 'red_discordbot.sock')
        os.environ['NOTIFY_SOCKET'] = sockname
        if os.path.exists(sockname):
            os.remove(sockname)

    try:
        error = False
        kbi = False
        p = Popen(red_call)
        if watchdog:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            sock.bind(sockname)
            sock.settimeout(5)

            last_pet = time()
            while (time() - last_pet) < args.timer and p.poll() is None:
                try:
                    data = sock.recv(1024).decode("utf-8")
                    data = [f.strip() for f in data.split('=')]
                    if data == ['WATCHDOG', '1']:
                        # print('INFO: Watchdog pet.')
                        last_pet = time()
                except socket.timeout:
                    pass
            else:
                if p.poll() is None:  # Still running
                    error = True
                    print('ERROR: Watchdog timout exceeded.')
        else:
            ret = p.wait()
            error = ret is not 0
    except KeyboardInterrupt:
        kbi = True
        pass
    except:
        error = True
        print(traceback.format_exc())
    finally:
        ret = stop_p(p)
        if (error or ret is not 0) and not kbi:
            exit(1)


def check_env(args):
    from cogs.utils.settings import Settings

    email = os.environ.get('RED_EMAIL', args.email)
    password = os.environ.get('RED_PASSWORD', args.password)
    token = os.environ.get('RED_TOKEN', args.token)

    if token and email:
        print("ERROR: You can only specify one of token or email")
        exit(1)
    elif token and ("@" in token or len(token) < 50):
        print("ERROR: Invalid token provided")
        exit(1)
    elif email and "@" not in email:
        print("ERROR: Invalid email provided")
        exit(1)
    elif email and not password:
        print("ERROR: Email authentication requires password")
        exit(1)

    s = Settings()

    # Set credentials if provided
    if token:
        if s.email not in [s.default_settings['EMAIL'], token]:
            print('WARNING: New token provided, overwriting old one')
        s.email = token
        s.login_type = 'token'
    elif email:
        if (s.email not in [s.default_settings['EMAIL'], email] or
                s.password not in [s.default_settings['PASSWORD'], password]):
            print('WARNING: New credentials provided, overwriting old ones')
        s.email = email
        s.password = password
        s.login_type = 'email'
    elif s.email == s.default_settings['EMAIL']:
        print("ERROR: No credentials set or provided.")
        exit(1)

    if s.prefixes == s.default_settings['PREFIXES']:
        default_prefix = os.environ.get('RED_PREFIX', args.prefix)
        if default_prefix:
            s.prefixes = [default_prefix]

    if s.bot_settings['default'] == s.default_settings['default']:
        admin = os.environ.get('RED_ADMIN', args.admin)
        mod = os.environ.get('RED_MOD', args.mod)
        if admin:
            s.default_admin = admin
        if mod:
            s.default_mod = mod


def main(args):
    check_env(args)
    start(args.redpy, args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Red-DiscordBot: A general-purpose bot by TwentySix26.')

    serv = parser.add_argument_group('Service options')
    serv.add_argument('--redpy', metavar='red.py', help="Path to alternate red.py (optional)",
                      default='red.py')
    serv.add_argument('-w', '--watchdog',
                      help='Emulate systemd watchdog to auto-restart Red',
                      action='store_true'
                      )
    serv.add_argument('-d', '--timer', help='Watchdog timer', metavar='SECS',
                      default=DEFAULT_WATCHDOG_SECS, type=int)
    serv.add_argument('--nop', help='NOP: Exit immediately. Used to make data containers.',
                      action='store_true')

    creds = parser.add_argument_group('Bot credentials', "Only specify one of token or email/pass. "
                                      "Command-line paramaters are overridden by the environment. "
                                      "NOTE: These options DO override the bot's config.")
    creds.add_argument('-t', '--token', help='Bot token')
    creds.add_argument('-e', '--email', help='Bot account email')
    creds.add_argument('-P', '--password', help='Bot account password')

    bot = parser.add_argument_group('Bot options', "Default bot parameters\n"
                                    "Command-line paramaters are overridden by environment. "
                                    "These options don't override the bot's config.")
    bot.add_argument('-p', '--prefix', help='Bot command prefix')
    bot.add_argument('-a', '--admin', help='Default admin role')
    bot.add_argument('-m', '--mod', help='Default mod role')
    bot.add_argument('--args', help='Arguments passed to Red',
                     default=DEFAULT_RED_ARGS)
    parsed_args = parser.parse_args()

    if parsed_args.nop:
        exit(0)
    elif not os.path.exists(parsed_args.redpy):
        print("ERROR: %s doesn't exist!" % parsed_args.redpy)
        exit(1)
    else:
        main(parsed_args)
