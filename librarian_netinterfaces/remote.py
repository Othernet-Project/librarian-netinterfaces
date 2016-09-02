"""
Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from librarian.core.exts import ext_container as exts


REMOTE_TEMPLATE = '''
SSID="{ssid}"
PASSCODE="{password}"
KEY="{key}"
'''


def setup(params):
    """
    Save remote configuration based on the passed in ``params``.
    """
    ssid = params['wireless.ssid']
    password = params['wireless.password']
    key = params['wireless.remote_key']
    data = REMOTE_TEMPLATE.format(ssid=ssid, password=password, key=key)
    with open(exts.config['remote.file'], 'w') as remote_file:
        remote_file.write(data)


def teardown():
    """
    Turn off remote mode.
    """
    remote_file = exts.config['remote.file']
    if os.path.exists(remote_file):
        os.rename(remote_file, exts.config['remote.disabled'])
