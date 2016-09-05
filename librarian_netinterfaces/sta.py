"""
Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging
import os
import subprocess

from librarian.core.exts import ext_container as exts


AP_PROFILE = "/etc/network/profiles.d/wlan0"
STA_PROFILE = "/etc/network/profiles.d/wlan0-client"
CURRENT_PROFILE = "/etc/network/interfaces.d/wlan0"
DNSMASQ_AP = "/etc/conf.d/dnsmasq/ap.conf"
DNSMASQ_STA = "/etc/conf.d/dnsmasq/sta.conf"
DNSMASQ_CONF = "/etc/dnsmasq.conf"
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


def get_wpa_network_config(ssid, password):
    """
    Generate 'network' section of 'wpa_supplicant.conf'.
    """
    return subprocess.check_output([WPA_PASSPHRASE, ssid, password])


def use_profile(profile):
    """
    Activate the specified profile for the wireless network interface.
    """
    os.remove(CURRENT_PROFILE)
    os.symlink(profile, CURRENT_PROFILE)


def reconfigure_dnsmasq(config):
    """
    Activate the configuration file for dnsmasq.
    """
    os.remove(DNSMASQ_CONF)
    os.symlink(config, DNSMASQ_CONF)


def restart_services(commands):
    """
    Execute the given sequence of commands that will restart the network
    stack, reinitializing it with the newly applied configuration.
    """
    for cmd in commands:
        logging.debug("Executing command: `%s`", cmd)
        os.system(cmd)


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
    # activate STA profile on wireless interface
    use_profile(STA_PROFILE)
    # apply dnsmasq configuration
    reconfigure_dnsmasq(DNSMASQ_STA)
    # restart services
    restart_services(exts.config['wireless.restart_commands'])


def teardown():
    """
    Turn off STA mode.
    """
    # activate AP profile on wireless interface
    use_profile(AP_PROFILE)
    # apply dnsmasq configuration
    reconfigure_dnsmasq(DNSMASQ_AP)
    # restart services
    restart_services(exts.config['wireless.restart_commands'])
