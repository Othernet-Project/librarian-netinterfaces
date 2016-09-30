<%namespace name="forms" file="/ui/forms.tpl"/>
<%namespace name="wifi_form" file="_${context['form'].MODE.lower()}_form.tpl"/>

${forms.form_message(message) if message else ''}
${forms.form_errors([form.error]) if form.error else ''}

<form action="${i18n_url('netinterfaces:settings')}" method="GET" id="switch-form">
    ${forms.field(form.mode, label=_('Operating Mode'))}
    %if form.MODE == form.STA_MODE:
    ${forms.field(form.security, label=_('Security Protocol'))}
    %endif
    <button type="submit">${_('Switch')}</button>
</form>

<form action="${i18n_url('netinterfaces:settings')}" method="POST" id="wireless-form">
    ${h.HIDDEN('mode', form.MODE)}
    %if form.MODE == form.STA_MODE:
    ${h.HIDDEN('security', form.SECURITY)}
    %endif
    ${wifi_form.body()}
    <p class="buttons">
        <button type="submit">${_('Save and Reboot')}</button>
    </p>
</form>
