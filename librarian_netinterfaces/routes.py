import os
import logging

from bottle import request
from bottle_utils.ajax import roca_view
from bottle_utils.i18n import lazy_gettext as _, i18n_url

from librarian_core.contrib.templates.renderer import template, view

from .forms import WifiForm


def restart_ap(restart_command):
    """ Restart hostapd """
    logging.info('Restarting wireless access point')
    ret = os.system(restart_command)
    if ret:
        logging.debug('"{}" returned {}'.format(restart_command, ret))


@roca_view('netinterfaces/wireless_settings', 'netinterfaces/_wireless_form',
           template_func=template)
def show_settings():
    return dict(form=WifiForm.from_conf_file())


@roca_view('netinterfaces/wireless_settings', 'netinterfaces/_wireless_form',
           template_func=template)
def set_settings():
    form = WifiForm(request.forms)
    if not form.is_valid():
        return dict(form=form, message=None)
    request.app.supervisor.exts.tasks.schedule(
        restart_ap, args=(request.app.config['wireless.restart_command'],),
        delay=5)
    return dict(form=form,
                message=_('Access point settings have been saved. Please '
                          'wait until the access point is restarted.'),
                redirect_url=i18n_url('dashboard:main'))


def routes(config):
    return (
        ('netinterfaces:settings', show_settings,
         'GET', '/netinterfaces/settings/', dict()),
        ('netinterfaces:settings', set_settings,
         'POST', '/netinterfaces/settings/', dict()),
    )
