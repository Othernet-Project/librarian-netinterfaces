<%namespace name="forms" file="/ui/forms.tpl"/>

${forms.field(form.ssid, label=_('Access point name'))}
${forms.field(form.hide_ssid, label=_('Hide in scan lists'))}
${forms.field(form.country, label=_('Country'), help=_('Meet country-specific frequency requirements'))}
${forms.field(form.channel, label=_('Channel'))}
${forms.field(form.security, label=_('Security'))}
${forms.field(form.password, label=_('Password'))}
% if form.show_driver:
    ${forms.field(form.driver, label=_('Device type'))}
% else:
    ${h.HIDDEN('driver', '0')}
% endif
