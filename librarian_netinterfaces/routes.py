import os
import logging

from bottle_utils.i18n import lazy_gettext as _, i18n_url
from streamline import XHRPartialFormRoute

from librarian.core.exts import ext_container as exts
from librarian.core.contrib.templates.renderer import template

from .forms import WifiForm


def restart_services(commands):
    """
    Execute the given sequence of commands that will restart the network
    stack, reinitializing it with the newly applied configuration.
    """
    logging.info('Restarting network services')
    for cmd in commands:
        logging.debug('Executing command: "%s"', cmd)
        ret = os.system(cmd)
        if ret:
            logging.debug('"%s" returned %s', cmd, ret)


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
        commands = self.config['wireless.restart_commands']
        exts.tasks.schedule(restart_services, args=(commands,), delay=5)
        return dict(message=_('Network settings have been saved. The device'
                              'is going to reboot now.'),
                    redirect_url=i18n_url('dashboard:main'))

    def form_invalid(self):
        return dict(message=None)
