<%namespace name="wireless_form" file="/netinterfaces/_wireless_form.tpl"/>

<form class="wireless-settings">
    ${wireless_form.body()}
    <p class="buttons">
        <button type="submit">${_('Save')}</button>
    </p>
</form>

<ul class="network-interfaces">
    % for iface in interfaces:
        <% 
        if iface.type == 'wlan':
            iface_icon = 'wifi'
            # Translators, network interface type shown in network interface list
            iface_type = _('wireless')
        elif iface.type == 'bridge':
            iface_icon = 'network-bridge'
            # Translators, network interface type shown in network interaface list
            iface_type = _('bridge')
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
            % if iface.type == 'bridge':
                ## Translators, human-friendly label for bridge interface with
                ## administrator-specified name (e.g., br0) replacing the 
                ## {name} placeholder.
                ${_('Ethernet bridge ({name})').format(name=iface.name)}
            % else:
                ${name}
            % endif
        </span>
        <span class="network-interfaces-type network-interfaces-detail">${iface_type}</span>

        % if iface.ipv4addr:
            <span class="network-interfaces-addr network-interfaces-detail">
                ## Translators, network interface IP address
                <span class="network-interfaces-label">${_('IP address:')}</span>
                ${iface.ipv4addr}
            </span>
        % endif
        % if iface.ipv4gateway:
            <span class="network-interfaces-gateway network-interfaces-detail">
                ## Translators, network interface default gateway
                <span class="network-interfaces-label">${_('Default gateway:')}</span>
                ${iface.ipv4gateway}
            </span>
        % endif
        % if iface.ipv6addr:
            <span class="network-interfaces-addr network-interfaces-detail">
                ## Translators, network interface IP address (IPv6)
                <span class="network-interfaces-label">${_('IPv6 address:')}</span>
                ${iface.ipv6addr}
            </span>
        % endif
        <span class="network-interfaces-card network-interfaces-detail">
            ## Translators, network interface IP address
            <span class="network-interfaces-label">${_('Interface name:')}</span>
            ${iface.name}
        </span>
        </li>
    % endfor
</ul>
