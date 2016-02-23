import os

from bottle import request
from bottle_utils import form
from bottle_utils.i18n import lazy_gettext as _
from hostapdconf import parser, helpers

from . import consts


class WifiForm(form.Form):
    messages = {
        'no_password': _('Password must be specified when security is '
                         'enabled'),
        'invalid_channel': _('The selected channel is not legal in the '
                             'chosen country.'),
        'save_error': _('Wireless settings could not be applied'),
    }

    def __init__(self, *args, **kwargs):
        super(WifiForm, self).__init__(*args, **kwargs)
        self.show_driver = request.app.config['wireless.driver_selection']

    ssid = form.StringField(validators=[form.Required()])
    hide_ssid = form.BooleanField()
    channel = form.SelectField(choices=consts.CHANNELS)
    country = form.SelectField(choices=consts.COUNTRIES)
    security = form.SelectField(choices=consts.WPA_MODES)
    password = form.StringField()
    driver = form.SelectField(choices=consts.DRIVERS)

    def wpa_mode(self):
        """ Get config format of wpa mode """
        if self.security.processed_value == consts.WPA_COMPATIBLE:
            return helpers.WPA_BOTH
        else:
            return helpers.WPA2_ONLY

    def driver_type(self):
        """ Get config format of the driver setting """
        if self.driver.processed_value == consts.ALTERNATIVE:
            return helpers.REALTEK
        else:
            return helpers.STANDARD

    def validate(self):
        """ Perform form-level validation and set the configuration options """
        if self.security.processed_value and not self.password.processed_value:
            raise ValueError('no_password')
        conf = self.getconf()
        helpers.set_ssid(conf, self.ssid.processed_value)
        helpers.set_country(conf, self.country.processed_value)
        try:
            helpers.set_channel(conf, self.channel.processed_value)
        except helpers.ConfigurationError:
            raise ValueError('invalid_channel')
        if self.hide_ssid.processed_value:
            helpers.hide_ssid(conf)
        else:
            helpers.reveal_ssid(conf)
        if self.security.processed_value:
            helpers.enable_wpa(conf, self.password.processed_value,
                               self.wpa_mode())
        else:
            helpers.disable_wpa(conf)
        helpers.set_driver(conf, self.driver_type())
        try:
            helpers.write()
        except OSError:
            raise ValueError('save_error')
        ret = self.restart_ap()


    @staticmethod
    def restart_ap():
        restart_command = request.app.config['wireless.restart_command']
        return os.system(restart_command)

    @staticmethod
    def getconf():
        """
        Get configuration from file, and fall back on defaults if configuration
        file is not present on disk
        """
        conf_file_path = request.app.config['wireless.config']
        if os.path.exists(conf_file_path):
            conf = parser.HostapdConf(conf_file_path)
        else:
            conf = parser.HostapdConf()
            conf.path = conf_file_path
            conf.update(consts.WIRELESS_DEFAULTS)
        return conf

    @staticmethod
    def security_from_conf(conf):
        """ Get security field value from the configuration """
        # Determine the security mode
        if conf.get('wpa') in [None, helpers.WPA_NONE]:
            return consts.WPA_NONE
        elif conf.get('wpa') in [helpers.WPA_BOTH, helpers.WPA1_ONLY]:
            return consts.WPA_COMPATIBLE
        else:
            return consts.WPA_SECURE

    @staticmethod
    def driver_from_conf(conf):
        """ Get driver field value from the configuration """
        if conf.get('driver') == helpers.REALTEK:
            return consts.ALTERNATIVE
        else:
            return consts.STANDARD

    @staticmethod
    def hide_from_conf(conf):
        """ Get hide_ssid field value from configuration """
        return conf.get('ignore_broadcast_ssid') == '1'

    @classmethod
    def from_conf_file(cls):
        """
        Initialize the form using configuration file or default config
        """
        data = {}
        conf = cls.getconf()
        data['ssid'] = conf.get('ssid')
        data['hide_ssid'] = cls.hide_from_conf(conf)
        data['channel'] = conf.get('channel')
        data['country'] = conf.get('country_code')
        data['security'] = cls.security_from_conf(conf)
        data['password'] = conf.get('wpa_passphrase')
        data['driver'] = cls.driver_from_conf(conf)
        return cls(data=data)
