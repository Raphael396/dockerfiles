#!/usr/bin/python

import argparse
from copy import deepcopy
import os
from signal import SIGINT
import socket
from subprocess import Popen, TimeoutExpired
import sys
from time import time, sleep
import traceback
from cogs.utils.settings import Settings


DEFAULT_RED_ARGS = "--no-prompt"
STOP_WAIT = 30
DEFAULT_WATCHDOG_SECS = 90
DEFAULT_POLL_INTERVAL = 1


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
    return 0  # Default


def start(red_py, args):
    red_call = [sys.executable, red_py]
    red_call.extend(args.args.split())

    watchdog = args.watchdog or os.environ.get('RED_WATCHDOG') == "1"

    if watchdog:
        sockname = os.path.join(os.getcwd(), 'red_discordbot.sock')
        os.environ['NOTIFY_SOCKET'] = sockname
        if os.path.exists(sockname):
            os.remove(sockname)
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.bind(sockname)
        sock.settimeout(args.poll)

    try:
        error = False
        kbi = False
        p = Popen(red_call)
        if watchdog:
            last_pet = time()

            # Watchdog loop
            while (time() - last_pet) < args.timer and p.poll() is None and \
                    not (args.maint and os.path.exists(args.maint)):
                try:
                    data = sock.recv(64).decode("utf-8")
                    data = [f.strip() for f in data.split('=')]
                    if data == ['WATCHDOG', '1']:
                        last_pet = time()
                except socket.timeout:
                    pass
            # Loop until maintainence file is removed, then exit
            else:
                if args.maint and os.path.exists(args.maint):
                    print('INFO: Entering maintainence mode.')
                    ret = stop_p(p)
                    while os.path.exists(args.maint):
                        sleep(args.poll)
                elif p.poll() is None:  # Still running
                    error = True
                    print('ERROR: Watchdog timout exceeded.')
        else:
            # Regular poll loop
            while not (args.maint and os.path.exists(args.maint)):
                try:
                    ret = p.wait(timeout=args.poll)
                    error = ret is not 0
                    break  # Should break on non-timeout
                except TimeoutExpired:
                    pass
            if args.maint and os.path.exists(args.maint):
                print('INFO: Entering maintainence mode.')
                ret = stop_p(p)
                while os.path.exists(args.maint):
                    sleep(args.poll)

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


def check_env(args, s):
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

    # Set credentials if provided
    if (token and s.email) or (email and s.token) or \
            (email and (s.password != password)):
        print('WARNING: New credentials provided, overwriting old ones')
    if token:
        s.token = token
    elif email:
        s.email = email
        s.password = password
    elif not s.login_credentials:
        print("ERROR: No credentials set or provided. Use arguments, env "
              " or --setup to provide them.")
        exit(1)

    defaults = s.default_settings['default']

    prefix = os.environ.get('RED_PREFIX', args.prefix)
    if prefix:
        if s.prefixes and (len(s.prefixes) != 1 or prefix != s.prefixes[0]):
            print('WARNING: New prefix provided, overwriting old one (%s)'
                  % s.prefixes)
        s.prefixes = [prefix]
    elif not s.prefixes:
        print("ERROR: No default prefix set or provided. Use arguments, env "
              "or --setup to provide one.")
        exit(1)

    admin = os.environ.get('RED_ADMIN', args.admin)
    if admin:
        default_admin = defaults['ADMIN_ROLE']
        if default_admin != s.default_admin and s.default_admin != admin:
            print('WARNING: New admin role provided, overwriting old one (%s)'
                  % s.default_admin)
        s.default_admin = admin

    mod = os.environ.get('RED_MOD', args.mod)
    if mod:
        default_mod = defaults['MOD_ROLE']
        if default_mod != s.default_mod and s.default_mod != mod:
            print('WARNING: New mod role provided, overwriting old one (%s)'
                  % s.default_mod)
        s.default_mod = mod
    s.save_settings()


def get_answer(prompt=">"):
    choices = ("yes", "y", "no", "n")
    c = ""
    while c not in choices:
        c = input(prompt).lower()
    if c.startswith("y"):
        return True
    else:
        return False


def check_path():
    userpath = os.path.expanduser('~')
    userbin = os.path.join(userpath, '.local/bin')
    currentpath = os.environ['PATH'].split(':')
    if userbin not in currentpath:
        currentpath.append(userbin)
        os.environ['PATH'] = ':'.join(currentpath)


def main(args):
    settings = Settings(parse_args=False)
    if args.setup:
        if not sys.stdin.isatty():
            print('ERROR: Console is not a TTY; cannot run interactive setup.')
            exit(1)
        from red import interactive_setup
        if (settings.bot_settings != settings.default_settings and
                get_answer(prompt='Reset settings before setup? [y/n]: ')
            ):
            settings.bot_settings = deepcopy(settings.default_settings)
        interactive_setup(settings)
        settings.save_settings()
        print('Setup complete. Run without --setup to start the bot.')
        exit(0)
    check_env(args, settings)
    check_path()
    start(args.redpy, args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Red-DiscordBot: A general-purpose bot by TwentySix26. '
                    '[E] options are overridden by environment variables. '
                    'NOTE: These options OVERWRITE the bot\'s config if '
                    'specified.')

    serv = parser.add_argument_group('Service options')
    serv.add_argument('--redpy', metavar='red.py', help="[E] Path to alternate red.py (optional)",
                      default='red.py')
    serv.add_argument('-w', '--watchdog',
                      help='[E] Emulate systemd watchdog to auto-restart Red',
                      action='store_true')
    serv.add_argument('-d', '--timer', help='Watchdog timer', metavar='SECS',
                      default=DEFAULT_WATCHDOG_SECS, type=int)
    serv.add_argument('--maint', metavar='file', help="Path to maintainence indicator",
                      default='data/red/red.down')
    serv.add_argument('-o', '--poll', help='Bot and maintainence poll interval',
                      metavar='SECS', default=DEFAULT_POLL_INTERVAL, type=int)
    serv.add_argument('--nop', help='NOP: Exit immediately. Used to make data containers.',
                      action='store_true')
    serv.add_argument('--setup', help='Enter credentials and other information via the console.',
                      action='store_true')

    creds = parser.add_argument_group('Bot credentials', "Only specify one of token or email/pass.")
    creds.add_argument('-t', '--token', help='[E] Bot token')
    creds.add_argument('-e', '--email', help='[E] Bot account email')
    creds.add_argument('-P', '--password', help='[E] Bot account password')

    bot = parser.add_argument_group('Bot options', "Default bot parameters")
    bot.add_argument('-p', '--prefix', help='[E] Bot command prefix')
    bot.add_argument('-a', '--admin', help='[E] Default admin role')
    bot.add_argument('-m', '--mod', help='[E] Default mod role')
    bot.add_argument('--args', help='Arguments passed to Red',
                     default=DEFAULT_RED_ARGS)
    parsed_args = parser.parse_args()

    redpy = os.environ.get('RED_PY')
    if redpy:
        parsed_args.redpy = redpy

    if parsed_args.nop:
        exit(0)
    elif not os.path.exists(parsed_args.redpy):
        print("ERROR: %s doesn't exist!" % parsed_args.redpy)
        exit(1)
    else:
        main(parsed_args)
