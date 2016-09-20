"""
Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import subprocess


WPA_DEFAULTS = """
# wpa_supplicant configuration file
#
# This file is part of rxOS.
# rxOS is free software licensed under the
# GNU GPL version 3 or any later version.
#
# (c) 2016 Outernet Inc
# Some rights reserved.
ctrl_interface=/var/run/wpa_supplicant
update_config=1
fast_reauth=1
ap_scan=1
# -----> Place your configuration below this line <-----
"""
WPA_CONF = "/etc/wpa_supplicant.conf"
WPA_PASSPHRASE = "/usr/sbin/wpa_passphrase"
AP_MODE = 'AP'
STA_MODE = 'STA'
WIRELESS_MODE_FILE = "/etc/conf.d/wireless"


def get_wireless_mode():
    """
    Return currently active wireless mode indicated by the os generated file.
    """
    try:
        with open(WIRELESS_MODE_FILE, 'r') as wifi_mode_file:
            mode = wifi_mode_file.read().strip()
    except Exception:
        return None
    else:
        return mode if mode in (AP_MODE, STA_MODE) else None


def get_wpa_network_config(ssid, password):
    """
    Generate 'network' section of 'wpa_supplicant.conf'.
    """
    return subprocess.check_output([WPA_PASSPHRASE, ssid, password])


def setup(params):
    """
    Configure STA mode on wireless interface, based on the the passed in
    ``params``.
    """
    ssid = params['wireless.ssid']
    password = params['wireless.password']
    net_section = get_wpa_network_config(ssid, password)
    # reset wpa_supplicant.conf to it's initial state
    with open(WPA_CONF, 'w') as wpa_conf_file:
        wpa_conf_file.write(WPA_DEFAULTS)
        # add network section to wpa_supplicant.conf
        wpa_conf_file.write(net_section)
    # write wireless mode marker
    with open(WIRELESS_MODE_FILE, 'w') as wifi_mode_file:
        wifi_mode_file.write(STA_MODE)


def teardown():
    """
    Turn off STA mode.
    """
    # write wireless mode marker
    with open(WIRELESS_MODE_FILE, 'w') as wifi_mode_file:
        wifi_mode_file.write(AP_MODE)
