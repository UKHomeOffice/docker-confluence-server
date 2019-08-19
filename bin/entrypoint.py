#!/usr/bin/python3

import sys
import os
import shutil
import logging
import jinja2 as j2
# UKHOMEOFFICE: additional imports
import time


######################################################################
# Utils

logging.basicConfig(level=logging.DEBUG)

def set_perms(path, user, group, mode):
    shutil.chown(path, user=user, group=group)
    os.chmod(path, mode)

# Setup Jinja2 for templating
jenv = j2.Environment(
    loader=j2.FileSystemLoader('/opt/atlassian/etc/'),
    autoescape=j2.select_autoescape(['xml']))

def gen_cfg(tmpl, target, env, user='root', group='root', mode=0o644):
    logging.info(f"Generating {target} from template {tmpl}")
    cfg = jenv.get_template(tmpl).render(env)
    with open(target, 'w') as fd:
        fd.write(cfg)
    set_perms(target, user, group, mode)

# UKHOMEOFFICE: Get the logs symlinked to stdout
def symlink_log(log_file):
        if not os.path.islink(log_file):
                if os.path.exists(log_file):
                        os.rename(log_file, f"{log_file}.{time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime())}")
                os.symlink('/dev/stdout', log_file)


######################################################################
# Setup inputs and outputs

# Import all ATL_* and Dockerfile environment variables. We lower-case
# these for compatability with Ansible template convention. We also
# support CATALINA variables from older versions of the Docker images
# for backwards compatability, if the new version is not set.
env = {k.lower(): v
       for k, v in os.environ.items()
       if k.startswith(('ATL_', 'CONFLUENCE_', 'RUN_', 'CATALINA_'))}


######################################################################
# Generate all configuration files for Confluence

# UKHOMEOFFICE: use provided run user and run group
gen_cfg('server.xml.j2',
        f"{env['confluence_install_dir']}/conf/server.xml", env,
        user=env['run_user'], group=env['run_group'])

# UKHOMEOFFICE: use provided run user and run group
gen_cfg('seraph-config.xml.j2',
        f"{env['confluence_install_dir']}/confluence/WEB-INF/classes/seraph-config.xml", env,
        user=env['run_user'], group=env['run_group'])

# UKHOMEOFFICE: use provided run user and run group
gen_cfg('confluence-init.properties.j2',
        f"{env['confluence_install_dir']}/confluence/WEB-INF/classes/confluence-init.properties", env,
        user=env['run_user'], group=env['run_group'])

gen_cfg('confluence.cfg.xml.j2',
        f"{env['confluence_home']}/confluence.cfg.xml", env,
        user=env['run_user'], group=env['run_group'], mode=0o640)


######################################################################
# UKHOMEOFFICE: Get the Confluence logs out to stdout

logs_folder = f"{env['confluence_home']}/logs"
if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
symlink_log(f"{logs_folder}/atlassian-confluence.log")
symlink_log(f"{logs_folder}/atlassian-diagnostics.log")
symlink_log(f"{logs_folder}/atlassian-synchrony.log")


######################################################################
# Start Confluence as the correct user

start_cmd = f"{env['confluence_install_dir']}/bin/start-confluence.sh"
if os.getuid() == 0:
    logging.info(f"User is currently root. Will change directory ownership to {env['run_user']} then downgrade permissions")
    set_perms(env['confluence_home'], env['run_user'], env['run_group'], 0o700)

    cmd = '/bin/su'
    start_cmd = ' '.join([start_cmd] + sys.argv[1:])
    args = [cmd, env['run_user'], '-c', start_cmd]
else:
    cmd = start_cmd
    args = [start_cmd] + sys.argv[1:]

logging.info(f"Running Confluence with command '{cmd}', arguments {args}")
os.execv(cmd, args)
