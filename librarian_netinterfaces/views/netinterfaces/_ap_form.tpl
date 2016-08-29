<%namespace name="forms" file="/ui/forms.tpl"/>

${forms.field(form.ssid, label=_('Access point name'))}
## Translators, label for a checkbox that enables hidden access point
${forms.field(form.hide_ssid, label=_('Do not show in scan lists'))}
${forms.field(form.country, label=_('Country'),
    ## Translators, WiFi has country-specific frequency regulations
    help=_("Meet regional Wi-Fi frequency requirements"),
    ## Translators, value used in country list for WiFi access point
    empty_value=_("No country"))}
${forms.field(form.channel, label=_('Channel'))}
${forms.field(form.security, label=_('Security'))}
${forms.field(form.password, label=_('Password'), autocomplete=False)}
% if form.show_driver:
    ## Translators, wireless device type, shown next to access point driver
    ## selection drop-down
    ${forms.field(form.driver, label=_('Device type'))}
% else:
    ${h.HIDDEN('driver', '1')}
% endif

