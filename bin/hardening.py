#!/usr/bin/python3

import logging
import os
import time
import jinja2 as j2


env = {k.lower(): v
       for k, v in os.environ.items()}

# Setup Jinja2 for templating
jenv = j2.Environment(
    loader=j2.FileSystemLoader('/opt/atlassian/etc/'),
    autoescape=j2.select_autoescape(['xml']))

# Get the logs symlinked to stdout
def symlink_log(log_file):
        if not os.path.islink(log_file):
                if os.path.exists(log_file):
                        os.rename(log_file, f"{log_file}.{time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime())}")
                os.symlink('/dev/stdout', log_file)

# generate config file, ignoring any requests to change ownership as we are already running as a non-privileged user
def gen_cfg_no_chown(tmpl, target, user='root', group='root', mode=0o644, overwrite=True):
    if not overwrite and os.path.exists(target):
        logging.info(f"{target} exists; skipping.")
        return

    logging.info(f"Generating {target} from template {tmpl}")
    cfg = jenv.get_template(tmpl).render(env)
    try:
        with open(target, 'w') as fd:
            fd.write(cfg)
    except (OSError, PermissionError):
        logging.warning(f"Container not started as root. Bootstrapping skipped for '{target}'")
    # don't change the perms as running as non-privileged user already
    # else:
    #     set_perms(target, user, group, mode)

# Get the Confluence logs out to stdout
def all_logs_to_stdout():
    logging.info(f"Generating symlinks to stdout for logs")
    logs_folder = f"{os.environ['CONFLUENCE_HOME']}/logs"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
    symlink_log(f"{logs_folder}/atlassian-confluence.log")
    symlink_log(f"{logs_folder}/atlassian-diagnostics.log")
    symlink_log(f"{logs_folder}/atlassian-synchrony.log")

# Generate the config files even we are not root
def gen_configs(env):
    logging.info(f"Generating configs for server.xml, seraph-config.xml and confluence-init.properties (regardless of run-as user)")
    gen_cfg_no_chown('server.xml.j2',
                    f"{env['confluence_install_dir']}/conf/server.xml", env)

    gen_cfg_no_chown('seraph-config.xml.j2',
                    f"{env['confluence_install_dir']}/confluence/WEB-INF/classes/seraph-config.xml", env)

    gen_cfg_no_chown('confluence-init.properties.j2',
                    f"{env['confluence_install_dir']}/confluence/WEB-INF/classes/confluence-init.properties", env)