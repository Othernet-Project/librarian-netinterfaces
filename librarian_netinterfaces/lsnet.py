"""
lsnet.py: Tool for retrieving all network interfaces

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from hwd.udev import devices_by_subsystem
from hwd.network import NetIface


def get_network_interfaces():
    netdevs = (NetIface(d) for d in devices_by_subsystem('net'))
    for d in netdevs:
        if d.type != 'loop':
            yield d

