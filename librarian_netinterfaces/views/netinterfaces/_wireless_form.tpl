<%namespace name="forms" file="/ui/forms.tpl"/>
<%namespace name="wifi_form" file="_${context['form'].MODE.lower()}_form.tpl"/>

${forms.form_message(message) if message else ''}
${forms.form_errors([form.error]) if form.error else ''}

<form action="${i18n_url('netinterfaces:settings')}" method="GET" id="mode-form">
    ${forms.field(form.mode, label=_('Operating Mode'))}
    <button type="submit">${_('Switch')}</button>
</form>

<form action="${i18n_url('netinterfaces:settings')}" method="POST" id="wireless-form">
    ${h.HIDDEN('mode', form.MODE)}
    ${wifi_form.body()}
    <p class="buttons">
        <button type="submit">${_('Save and Reboot')}</button>
    </p>
</form>
