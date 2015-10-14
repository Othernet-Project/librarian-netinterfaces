<ul class="network-interfaces">
    % for iface in interfaces:
        <% 
        if iface.is_wireless:
            iface_icon = 'wifi'
            # Translators, network interface type shown in network interface list
            iface_type = _('wireless')
        else:
            iface_icon = 'ethernet'
            # Translators, network interface type shown in network interface list
            iface_type = _('wired')

        connected = iface.ipv4 is not None
        conn_class = 'connected' if connected else 'disconnected'
        %>
        <li>
        <span class="network-interfaces-icon icon icon-${iface_icon} network-interfaces-${conn_class}"></span>
        <span class="network-interfaces-name network-interfaces-detail">
            ${iface.name}
        </span>
        <span class="network-interfaces-type network-interfaces-detail">${iface_type}</span>
        <span class="network-interfaces-addr network-interfaces-detail">
            ## Translators, network interface IP address
            <span class="network-interfaces-label">${_('IP address:')}</span>
            ## Translators, shown when network interface is disconnected
            ${iface.ipv4 or _('disconnected')}
        </span>
        <span class="network-interfaces-addr network-interfaces-detail">
            ## Translators, network interface IP address (IPv6)
            <span class="network-interfaces-label">${_('IPv6 address:')}</span>
            ## Translators, shown when network interface is disconnected
            ${iface.ipv6 or _('disconnected')}
        </span>
        </li>
    % endfor
</ul>
