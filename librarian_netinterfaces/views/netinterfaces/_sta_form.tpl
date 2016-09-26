<%namespace name="forms" file="/ui/forms.tpl"/>

${forms.field(form.ssid, label=_('Access point name'))}

%if form.SECURITY == form.WPA_PROTOCOL:
${forms.field(form.password, label=_('Password'), autocomplete=False)}
%elif form.SECURITY == form.WEP_PROTOCOL:
${forms.field(form.key0, label=_('Key 0'), autocomplete=False)}
${forms.field(form.key1, label=_('Key 1'), autocomplete=False)}
${forms.field(form.key2, label=_('Key 2'), autocomplete=False)}
${forms.field(form.key3, label=_('Key 3'), autocomplete=False)}
${forms.field(form.key_index, label=_('Key Index'), autocomplete=False)}
%endif
