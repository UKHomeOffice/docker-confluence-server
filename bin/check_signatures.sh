#!/usr/bin/env bash

# Atlassian's gen_cfg and our gen_cfg_no_chown should have the same signature
# Fail the build if that's not the case
# Note that we can't use Python's inspect module here to check the signature very easily because /entrypoint.py cannot be imported without starting the service
diff <(grep 'def gen_cfg' /entrypoint.py) <(grep 'def gen_cfg' /hardening.py | sed 's/gen_cfg_no_chown/gen_cfg/')
