import logging
import os

from bottle import request
from bottle_utils import form
from bottle_utils.i18n import lazy_gettext as _
from hostapdconf import parser, helpers

from librarian.core.exts import ext_container as exts
from . import consts, sta


SECURITY_MAP = {
    consts.WPA_NONE: helpers.WPA_NONE,
    consts.WPA_COMPATIBLE: helpers.WPA_BOTH,
    consts.WPA_SECURE: helpers.WPA2_ONLY,
}


class WifiForm(form.Form):
    #: Available operating modes, aliased for use in templates
    AP_MODE = consts.AP_MODE
    STA_MODE = consts.STA_MODE
    #: List of all available modes
    VALID_MODES = dict(consts.MODES).keys()
    #: Use this mode if no valid mode was chosen
    DEFAULT_MODE = consts.AP_MODE
    #: Attribute to store discovered subclasses
    _subclasses = ()

    mode = form.SelectField(choices=consts.MODES)

    @classmethod
    def subclasses(cls, source=None):
        """
        Return all the subclasses of ``cls``.
        """
        source = source or cls
        result = source.__subclasses__()
        for child in result:
            result.extend(cls.subclasses(source=child))
        return result

    @classmethod
    def get_form_class(cls, mode=None, security=None):
        """
        Return the matching form for the passed in ``mode``. If no ``mode``
        was specified, use the already stored one in librarian's setup data,
        falling back to :py:attr:`~WifiForm.DEFAULT_MODE`.
        """
        if mode not in cls.VALID_MODES:
            default = exts.config.get('wireless.mode', cls.DEFAULT_MODE)
            mode = sta.get_wireless_mode() or default
        # cache detected subclasses for subsequent accesses
        cls._subclasses = cls._subclasses or cls.subclasses()
        filtered = [sc for sc in cls._subclasses if sc.MODE == mode]
        subcls = filtered[-1]
        if mode == consts.AP_MODE:
            # in AP mode there's only one form, return it
            return subcls
        # in station mode get the form for the requested security protocol
        return subcls.for_security_protocol(security)

    @classmethod
    def from_conf_file(cls):
        """
        Initialize the form using configuration file or default config
        """
        raise NotImplementedError()


class WifiAPForm(WifiForm):
    #: Used to differentiate between the AP / STA forms in templates
    MODE = consts.AP_MODE
    #: Validation error messages
    messages = {
        'invalid_channel': _('The selected channel is not legal in the '
                             'chosen country.'),
        'save_error': _('Wireless settings could not be applied'),
    }

    def __init__(self, *args, **kwargs):
        super(WifiAPForm, self).__init__(*args, **kwargs)
        self.show_driver = request.app.config['wireless.driver_selection']

    ssid = form.StringField(validators=[form.Required()])
    hide_ssid = form.BooleanField(value='hide_ssid')
    channel = form.SelectField(choices=consts.CHANNELS)
    country = form.SelectField(choices=consts.COUNTRIES)
    security = form.SelectField(choices=consts.WPA_MODES)
    password = form.StringField(
        validators=[form.LengthValidator(min_len=8, max_len=63)],
        messages={
            'min_len': _('Password must be at least {len} characters long.'),
            'max_len': _('Password cannot be longer than {len} characters.'),
            'no_password': _('Password must be specified when security is '
                             'enabled'),
        })
    driver = form.SelectField(choices=consts.DRIVERS)

    def wpa_mode(self):
        """ Get config format of wpa mode """
        return SECURITY_MAP.get(self.security.processed_value,
                                helpers.WPA2_ONLY)

    def driver_type(self):
        """ Get config format of the driver setting """
        if self.driver.processed_value == consts.ALTERNATIVE:
            return helpers.REALTEK
        else:
            return helpers.STANDARD

    def integer_value(self, value):
        if value is None:
            return
        return int(value)

    postprocess_channel = integer_value
    postprocess_security = integer_value

    def preprocess_country(self, value):
        return value.upper() if value else None

    def validate(self):
        """ Perform form-level validation and set the configuration options """
        if self.security.processed_value and not self.password.processed_value:
            self._add_error(self.password,
                            self.ValidationError('no_password'))
        conf = self.getconf()
        helpers.set_ssid(conf, self.ssid.processed_value)
        helpers.set_country(conf, self.country.processed_value)
        try:
            helpers.set_channel(conf, self.channel.processed_value)
        except helpers.ConfigurationError:
            raise self.ValidationError('invalid_channel')
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
            conf.write(header=consts.HEADER)
            sta.teardown()
        except OSError:
            logging.exception("Wireless AP settings saving failed.")
            raise self.ValidationError('save_error')
        else:
            exts.setup.append({'wireless.mode': self.MODE})

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
        if conf.get('wpa') in [None, str(helpers.WPA_NONE)]:
            return consts.WPA_NONE
        elif conf.get('wpa') in [str(helpers.WPA_BOTH),
                                 str(helpers.WPA1_ONLY)]:
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
        data['mode'] = cls.MODE
        data['ssid'] = conf.get('ssid')
        data['hide_ssid'] = cls.hide_from_conf(conf)
        data['channel'] = conf.get('channel')
        data['country'] = conf.get('country_code')
        data['security'] = cls.security_from_conf(conf)
        data['password'] = conf.get('wpa_passphrase')
        data['driver'] = cls.driver_from_conf(conf)
        return cls(data=data)


class WifiSTAForm(WifiForm):
    #: Used to differentiate between the AP / STA forms in templates
    MODE = consts.STA_MODE
    #: Protocol aliases
    NO_SECURITY = consts.NO_SECURITY
    WPA_PROTOCOL = consts.WPA
    WEP_PROTOCOL = consts.WEP
    #: List of supported security protocols
    VALID_SECURITY_PROTOCOLS = dict(consts.SECURITY_PROTOCOLS).keys()
    #: Use this security protocol if no valid one was chosen
    DEFAULT_SECURITY = WPA_PROTOCOL
    #: Validation error messages
    messages = {
        'save_error': _('Wireless settings could not be applied'),
    }

    ssid = form.StringField(validators=[form.Required()])
    security = form.SelectField(choices=consts.SECURITY_PROTOCOLS)

    def validate(self):
        """
        Perform form-level validation and set the configuration options.
        """
        params = dict(('wireless.{}'.format(key), value)
                      for (key, value) in self.processed_data.items())
        try:
            sta.setup(params)
        except Exception:
            logging.exception("Wireless STA settings saving failed.")
            sta.teardown()
            raise self.ValidationError('save_error')
        else:
            # on successful setup, store persistent config
            exts.setup.append(params)

    @classmethod
    def for_security_protocol(cls, security):
        if security not in cls.VALID_SECURITY_PROTOCOLS:
            security = exts.config.get('wireless.security',
                                       cls.DEFAULT_SECURITY)
        cls._subclasses = cls._subclasses or cls.subclasses()
        (form_cls,) = [sc for sc in cls._subclasses
                       if getattr(sc, 'SECURITY', None) == security]
        return form_cls


class WifiOpenForm(WifiSTAForm):
    #: Which security protocol is supported by the form
    SECURITY = consts.NO_SECURITY

    @classmethod
    def from_conf_file(cls):
        """
        Initialize the form using configuration file or default config
        """
        ssid = exts.config.get('wireless.ssid', '')
        return cls(data=dict(mode=cls.MODE,
                             security=cls.SECURITY,
                             ssid=ssid))


class WifiWPAForm(WifiSTAForm):
    #: Which security protocol is supported by the form
    SECURITY = consts.WPA

    password = form.StringField()

    @classmethod
    def from_conf_file(cls):
        """
        Initialize the form using configuration file or default config
        """
        ssid = exts.config.get('wireless.ssid', '')
        password = exts.config.get('wireless.password', '')
        return cls(data=dict(mode=cls.MODE,
                             security=cls.SECURITY,
                             ssid=ssid,
                             password=password))


class WifiWEPForm(WifiSTAForm):
    #: Which security protocol is supported by the form
    SECURITY = consts.WEP
    #: WEP supports up to 4 keys to be specified, but only 1 can be active
    KEY_INDEXES = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
    )
    #: Validation error messages
    messages = {
        'missing_key': _('The selected key index has no key specified'),
    }

    key0 = form.StringField()
    key1 = form.StringField()
    key2 = form.StringField()
    key3 = form.StringField()
    key_index = form.SelectField(choices=KEY_INDEXES)

    @classmethod
    def from_conf_file(cls):
        """
        Initialize the form using configuration file or default config
        """
        ssid = exts.config.get('wireless.ssid', '')
        key0 = exts.config.get('wireless.key0', '')
        key1 = exts.config.get('wireless.key1', '')
        key2 = exts.config.get('wireless.key2', '')
        key3 = exts.config.get('wireless.key3', '')
        key_index = exts.config.get('wireless.key_index', '')
        return cls(data=dict(mode=cls.MODE,
                             security=cls.SECURITY,
                             ssid=ssid,
                             key0=key0,
                             key1=key1,
                             key2=key2,
                             key3=key3,
                             key_index=key_index))

    def validate(self):
        key_index = self.processed_data['key_index']
        key = self.processed_data['key{}'.format(key_index)]
        if not key:
            raise self.ValidationError('missing_key')
        # call superclass so saving is executed
        super(WifiWEPForm, self).validate()
