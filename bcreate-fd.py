#!/usr/bin/env python

# Importing standard python libraries
import sys
import os
import os.path
import random
import ConfigParser
import argparse
import glob

try:
    from jinja2 import Template, Environment, PackageLoader
except ImportError:
    print >>sys.stderr, 'Error: I require Jinja2 Templates. Please install using "sudo pip install jinja2"'
    sys.exit(1)

# Global Defaults
DEFAULT_CONFIG = './fd.conf'


def parse_schedules(bacula_dir):
    schedules = []
    try:
        for filename in glob.iglob(bacula_dir + 'conf.d/schedules.d/*.conf'):
            for line in open(filename, 'r'):
                if "Name" in line:
                    schedules.append(line.strip().replace('"', '').replace(' ', '').split("=")[-1])
    except:
        print sys.stderr, 'Error: %s/conf.d/schedules.d/*.conf does not exist. Please create one.' % bacula_dir
        sys.exit(1)

    return schedules


def parse_pools(bacula_dir):
    pools = []
    try:
        for filename in glob.iglob(bacula_dir + 'conf.d/pools.d/*.conf'):
            for line in open(filename, 'r'):
                if "Name" in line:
                    pools.append(line.strip().replace('"', '').replace(' ', '').split("=")[-1])
    except:
        print sys.stderr, 'Error: %s/conf.d/pools.d/*.conf does not exist. Please create one.' % bacula_dir
        sys.exit(1)

    return pools


def parse_storages(bacula_dir):
    storages = []
    try:
        for line in open(bacula_dir + "/conf.d/storages.conf", "r"):
            if "Name" in line:
                storages.append(line.strip().replace('"', '').replace(' ', '').split("=")[-1])
    except:
        print sys.stderr, 'Error: %s/conf.d/storages.conf does not exist. Please create one.' % bacula_dir
        sys.exit(1)

    return storages


def parse_filesets(bacula_dir):
    filesets = []
    try:
        for filename in glob.iglob(bacula_dir + 'conf.d/filesets.d/*.conf'):
            for line in open(filename, 'r'):
                if "Name" in line:
                    filesets.append(line.strip().replace('"', '').replace(' ', '').split("=")[-1])
    except:
        print sys.stderr, 'Error: %s/conf.d/filesets.d/*.conf does not exist. Please create one.' % bacula_dir
        sys.exit(1)

    return filesets


def read_in_args_and_conf():

    conf_parser = argparse.ArgumentParser(
        add_help = False
    )

    conf_parser.add_argument(
        "-c", "--config-file",
        dest="configfile",
        help="Use a different config file other than %s" % DEFAULT_CONFIG
    )

    args, remaining_argv = conf_parser.parse_known_args()

    if args.configfile:
        configfile = args.configfile
    else:
        configfile = DEFAULT_CONFIG

    # Testing if the config file defined exists
    if not os.path.isfile(configfile):
        print >>sys.stderr, 'ERROR: %s is not a file' % configfile

    config = ConfigParser.SafeConfigParser()
    try:
        config.read([configfile])
    except:
        print >>sys.stderr, 'ERROR: There is an error in the config file, %s' % configfile

    defaults = dict(config.items("default"))

    bacula_dir = defaults["bacula_dir"]
    client_conf_dir = defaults["client_conf_dir"]

    schedule_choices = parse_schedules(bacula_dir)
    schedule_default = defaults["schedule"]

    domain_default = defaults["domain"]

    storage_node_choices = parse_storages(bacula_dir)
    storage_node_default = defaults["storage_node"]

    pool_choices = parse_pools(bacula_dir)
    pool_default = defaults["pool"]

    fileset_choices = parse_filesets(bacula_dir)
    fileset_default = defaults["fileset"]

    password_length = defaults["password_length"]

    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents = [conf_parser],
        description = __doc__,
        formatter_class = argparse.RawDescriptionHelpFormatter,
        add_help = True,
        usage = '%(prog)s [options]'
    )

    parser.set_defaults(**defaults)

    parser.add_argument(
        '-H', '--hostname',
        help = 'Short hostname of fd client',
        required = True
    )

    parser.add_argument(
        '-d', '--domain',
        default = domain_default,
        help = 'Domain (ie: example.com) that the fd client is in'
    )

    parser.add_argument(
        '-pl', '--password-length',
        default = password_length,
        help = 'Lenght of password (default: %s).'  % password_length
    )

    parser.add_argument(
        '-s', '--schedule',
        default = schedule_default,
        choices = schedule_choices,
        help = 'Set a backup schedule for the client'
    )

    parser.add_argument(
        '-p', '--pool',
        default = pool_default,
        choices = pool_choices,
        help = 'Set a backup pool for the client'
    )

    parser.add_argument(
        '-f', '--fileset',
        default = fileset_default,
        choices = fileset_choices,
        help = 'Set a fileset for the client'
    )

    parser.add_argument(
        '-n', '--storage-node',
        default = storage_node_default,
        choices = storage_node_choices,
        help = 'Bacula storage node'
    )

    parser.add_argument(
        '--client-conf-dir',
        default = client_conf_dir,
        help = 'Override the default client configuration directory'
    )

    parser.add_argument(
        '--bacula-dir',
        default = bacula_dir,
        help = 'Override the default bacula configuration directory'
    )

    # capture args
    args = parser.parse_args(remaining_argv)

    # make args into a dictionary
    d = args.__dict__

    return d


def generate_password(length):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    upperalphabet = alphabet.upper()
    pw_len = int(length)
    pwlist = []

    for i in range(pw_len//3):
        pwlist.append(alphabet[random.randrange(len(alphabet))])
        pwlist.append(upperalphabet[random.randrange(len(upperalphabet))])
        pwlist.append(str(random.randrange(10)))
    for i in range(pw_len-len(pwlist)):
        pwlist.append(alphabet[random.randrange(len(alphabet))])

    random.shuffle(pwlist)
    pwstring = "".join(pwlist)

    return pwstring


def write_client_conf(hostname, schedule, fqdn, pool, fileset, storage_node, passhash, client_dir):

    env = Environment(loader=PackageLoader('bcreate-fd', 'templates'))
    template = env.get_template('client.tpl')

    f = open(client_dir + "/" + hostname + ".conf", "w")
    f.write( template.render(schedule=schedule, fqdn=fqdn, pool=pool, fileset=fileset, storage_node=storage_node, passhash=passhash) )
    f.close()


def print_fd_conf(fqdn, passhash):

    env = Environment(loader=PackageLoader('bcreate-fd', 'templates'))
    template = env.get_template('fd.tpl')

    print template.render(fqdn=fqdn, passhash=passhash)


def main():

    args = read_in_args_and_conf()

    bacula_dir = args["bacula_dir"]
    fd_hostname = args["hostname"] + "." + args["domain"]
    fd_domain = args["domain"]
    fd_pool = args["pool"]
    fd_schedule = args["schedule"]
    fd_fileset = args['fileset']
    fd_fqdn = fd_hostname
    fd_storage_node = args["storage_node"]
    fd_client_dir = args["client_conf_dir"]
    fd_password_len = args["password_length"]
    fd_password = generate_password(fd_password_len)

    print "Adding host: %s" % fd_hostname

    print """
      hostname:   %s
      domain:     %s
      schedule:   %s
      fileset:    %s
      pool:       %s
      fqdn:       %s
      storage:    %s
      client.d:   %s
      password:   %s


      """ % (fd_hostname, fd_domain, fd_schedule, fd_fileset, fd_pool, fd_fqdn, fd_storage_node, fd_client_dir, fd_password)

    write_client_conf(fd_hostname, fd_schedule, fd_fqdn, fd_pool, fd_fileset, fd_storage_node, fd_password, fd_client_dir)

    print_fd_conf(fd_fqdn, fd_password)

    sys.exit(0)

if __name__ == '__main__':
    main()
