import os
import logging

from bottle_utils.i18n import lazy_gettext as _, i18n_url
from streamline import XHRPartialFormRoute

from librarian.core.exts import ext_container as exts
from librarian.core.contrib.templates.renderer import template

from .forms import WifiForm


def restart_services(restart_cmd):
    """ Restart network services """
    logging.info('Restarting network services')
    ret = os.system(restart_cmd)
    if ret:
        logging.debug('"{}" returned {}'.format(restart_cmd, ret))


class NetSettings(XHRPartialFormRoute):
    name = 'netinterfaces:settings'
    path = '/netinterfaces/settings/'
    template_func = template
    template_name = 'netinterfaces/wireless_settings'
    partial_template_name = 'netinterfaces/_wireless_form'
    form_factory = WifiForm

    def get_form_factory(self):
        mode = self.request.params.get('mode')
        return self.form_factory.get_form_class(mode=mode)

    def get_unbound_form(self):
        form_factory = self.get_form_factory()
        return form_factory.from_conf_file()

    def form_valid(self):
        restart_cmd = self.config['wireless.restart_command']
        exts.tasks.schedule(restart_services, args=(restart_cmd,), delay=5)
        return dict(message=_('Network settings have been saved. The device'
                              'is going to reboot now.'),
                    redirect_url=i18n_url('dashboard:main'))

    def form_invalid(self):
        return dict(message=None)
