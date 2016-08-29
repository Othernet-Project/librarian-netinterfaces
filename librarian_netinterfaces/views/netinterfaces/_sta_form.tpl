<%namespace name="forms" file="/ui/forms.tpl"/>

${forms.field(form.ssid, label=_('Access point name'))}
${forms.field(form.password, label=_('Password'), autocomplete=False)}
${forms.field(form.remote_key, label=_('Remote Key'))}
