import os
import logging

from bottle_utils.i18n import lazy_gettext as _, i18n_url
from streamline import XHRPartialFormRoute

from librarian.core.exts import ext_container as exts
from librarian.core.contrib.templates.renderer import template

from .forms import WifiForm


def restart_ap(restart_command):
    """ Restart hostapd """
    logging.info('Restarting wireless access point')
    ret = os.system(restart_command)
    if ret:
        logging.debug('"{}" returned {}'.format(restart_command, ret))


class NetSettings(XHRPartialFormRoute):
    name = 'netinterfaces:settings'
    path = '/netinterfaces/settings/'
    template_func = template
    template_name = 'netinterfaces/wireless_settings'
    partial_template_name = 'netinterfaces/_wireless_form'
    form_factory = WifiForm

    def get_unbound_form(self):
        form_factory = self.get_form_factory()
        return form_factory.from_conf_file()

    def form_valid(self):
        restart_cmd = self.config['wireless.restart_command']
        exts.tasks.schedule(restart_ap, args=(restart_cmd,), delay=5)
        return dict(message=_('Access point settings have been saved. Please '
                              'reconnect your devices.'),
                    redirect_url=i18n_url('dashboard:main'))

    def form_invalid(self):
        return dict(message=None)
