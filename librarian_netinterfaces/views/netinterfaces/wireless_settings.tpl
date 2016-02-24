<%inherit file="/narrow_base.tpl"/>
<%namespace name="wireless_form" file="_wireless_form.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Access point settings')}
</%block>

<h2>
    <span class="icon icon-wifi"></span>
    ## Translators, used as page heading
    <span>${_('Access point settings')}</span>
</h2>

<form action="${i18n_url('netinterfaces:settings')}" method="POST" id="wireless-form">
    ${wireless_form.body()}
</form>

