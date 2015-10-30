<ul class="network-interfaces">
    % for iface in interfaces:
        <% 
        if iface.type == 'wlan':
            iface_icon = 'wifi'
            # Translators, network interface type shown in network interface list
            iface_type = _('wireless')
        else:
            iface_icon = 'ethernet'
            # Translators, network interface type shown in network interface list
            iface_type = _('wired')

        connected = iface.is_connected and iface.ipv4addr
        conn_class = 'connected' if connected else 'disconnected'
        if iface.vendor or iface.model:
            name = iface.vendor + ' ' + iface.model
        else:
            name = iface.name
        %>
        <li>
        <span class="network-interfaces-icon icon icon-${iface_icon} network-interfaces-${conn_class}"></span>
        <span class="network-interfaces-name network-interfaces-detail">
            ${name}
        </span>
        <span class="network-interfaces-type network-interfaces-detail">${iface_type}</span>
        % if connected:
            <span class="network-interfaces-addr network-interfaces-detail">
                ## Translators, network interface IP address
                <span class="network-interfaces-label">${_('IP address:')}</span>
                ${iface.ipv4addr}
            </span>
            <span class="network-interfaces-gateway network-interfaces-detail">
                ## Translators, network interface default gateway
                <span class="network-interfaces-label">${_('Default gateway:')}</span>
                ${iface.ipv4gateway}
            </span>
            <span class="network-interfaces-addr network-interfaces-detail">
                ## Translators, network interface IP address (IPv6)
                <span class="network-interfaces-label">${_('IPv6 address:')}</span>
                ${iface.ipv6addr}
            </span>
            <span class="network-interfaces-card network-interfaces-detail">
                ## Translators, network interface IP address
                <span class="network-interfaces-label">${_('Interface name:')}</span>
                ${iface.name}
            </span>
        % endif
        </li>
    % endfor
</ul>
