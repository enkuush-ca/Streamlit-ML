# -*- coding: future_fstrings -*-

# Copyright 2018 Streamlit Inc. All rights reserved.

"""Loads the configuration data."""

# Python 2/3 compatibility
from __future__ import print_function, division, unicode_literals, absolute_import
from streamlit.compatibility import setup_2_3_shims
setup_2_3_shims(globals())

# Package Imports
import ast
import os
import platform
import toml
import urllib

# Streamlit imports
from streamlit.ConfigOption import ConfigOption
from streamlit import util

from streamlit.logger import get_logger
LOGGER = get_logger()

### Config System Global State ###

# Descriptions of each of the possible config sections.
_config_sections = dict(
    _test = 'Special test section just used for unit tests.',
)

# Stores the config options as key value pairs in a flat dict.
_config_options = dict()

def _create_section(section, description):
    """Create a config section and store it globally in this module."""
    assert section not in _config_sections, (
        'Cannot define section "%s" twice.' % section)
    _config_sections[section] = description

def _create_option(key, description=None, default_val=None):
    """Create a ConfigOption and stores it globally in this module.

    Exactly follows ConfigOption arguments.
    """
    option = ConfigOption(key, description=description, default_val=default_val)
    assert option.section in _config_sections, (
        'Section "%s" must be one of %s.' %
        (option.section, ', '.join(_config_sections.keys())))
    assert key not in _config_options, (
        'Cannot define option "%s" twice.' % key)
    _config_options[key] = option
    return option


### Config Section: Global ###

_create_section('global', 'Global options that apply across all of Streamlit.')

@_create_option('global.developmentMode')
def _global_development_mode():
    """Are we in development mode? (Only for developers of Streamlit.)

    This option defaults to True if and only if Streamlit wasn't installed
    normally.
    """
    return ('site-packages' not in __file__)

@_create_option('global.logLevel')
def _global_log_level():
    """What level of logging, 'error', 'warning', 'info', or 'debug'?

    By default, this is 'debug' in development mode, and 'info' otherwise.
    """
    if get_option('global.developmentMode'):
        return 'debug'
    else:
        return 'info'



### Config Section: Local ###

_create_section('local', 'Settings for users to connect to Streamlit.')

_create_option('local.waitForProxySecs',
    description = 'How long to wait for the proxy server to start up.',
    default_val = 3.0)

_create_option('local.throttleSecs',
    description = 'How long to wait between draining the local queue.',
    default_val= 0.01)



### Config Section: Proxy ###

_create_section('proxy', 'Configuration of the proxy server.')

_create_option('proxy.server',
    description = 'Internet address of the proxy server.',
    default_val = 'localhost')

_create_option('proxy.port',
    description = 'Port for the proxy server.',
    default_val = 8501)

_create_option('proxy.autoCloseDelaySecs',
    description = (
        'How long the proxy should stay open when there are '
        'no connections. Can be set to .inf for "infinity". '
        'This delay only starts counting after the '
        'reportExpirationSecs delay transpires.'),
    default_val = 0)

# TODO: In new config system, allow us to specify ranges
# for numeric values, so anything outside that range is
# considered invalid.
_create_option('proxy.reportExpirationSecs',
    description = (
        'How long reports should be stored in memory for when '
        'script is done and there are no viewers. '
        'For best results make sure this is >= 3.'),
    default_val = 10.1)

@_create_option('proxy.useNode')
def _proxy_use_node():
    """Whether to use the node server. (Only for developers of Streamlit.)"""
    return get_option('global.developmentMode')

@_create_option('proxy.isRemote')
@util.memoize
def _proxy_is_remote():
    """Is the proxy running remotely.

    By default, this option is False unless we are on a headless Linux box.
    """
    is_linux = (platform.system() == 'Linux')
    is_headless = (not os.getenv('DISPLAY'))
    return is_linux and is_headless

_create_option('proxy.saveOnExit',
    description = """
        Should we save this report to S3 after the script copletes.

        DEPRECATION WARNING: I think we should get rid of this, and fold a
        single option that makes sense for the Flotilla use case.
        """,
    default_val = False)

_create_option('proxy.watchFileSystem',
    description = 'Watch for filesystem changes and rerun reports.',
    default_val = True)

_create_option('proxy.externalIP',
    description = """
        An address for the proxy which can be accessed on the public Internet.

        NOTE: We should make this a computed option by bringing
        Proxy._get_external_ip into this function.
        """,
    default_val = None)


### Config Section: S3 ###

_create_section('s3', 'Configuration for report saving.')

@_create_option('s3.sharingEnabled')
def _s3_sharing_enabled():
    """Whether Streamlit is allowed tosave reports to s3.

    Defaults to True so long as 's3.bucket' is defined, either by the user or
    using the default Stremalit credentials.
    """
    # Sharing is enabled if the user overrode 's3.bucket'.
    using_default_bucket = (_config_options['s3.bucket'].where_defined ==
            ConfigOption.DEFAULT_DEFINITION)
    if not using_default_bucket:
        return True

    # Sharing is also enabled if successfully parse default credentials.
    return _get_default_credentials() is not None

@_create_option('s3.bucket')
def _s3_bucket():
    """Name of the AWS S3 bucket to save reports.

    Disabled if s3.sharingEnabled is False. Otherwise, defaults to
    share.streamlit.io.
    """
    if not get_option('s3.sharingEnabled'):
        return None
    return _get_default_credentials()['bucket']

@_create_option('s3.url')
def _s3_url():
    """URL root for external view of Streamlit reports.

    Disabled if s3.bucket is None. Otherwise uses default credentials.
    """
    if not get_option('s3.sharingEnabled'):
        return None
    return _get_default_credentials()['url']

@_create_option('s3.accessKeyId')
def _s3_access_key_id():
    """Access key to write to the S3 bucket.

    Disabled if s3.bucket is None. Otherwise uses default credentials.
    """
    if not get_option('s3.sharingEnabled'):
        return None
    return _get_default_credentials()['accessKeyId']

@_create_option('s3.secretAccessKey')
def _s3_secret_access_key():
    """Secret access key to write to the S3 bucket.

    Disabled if s3.bucket is None. Otherwise uses default credentials.
    """
    if not get_option('s3.sharingEnabled'):
        return None
    return _get_default_credentials()['secretAccessKey']

_create_option('s3.keyPrefix',
    description = """"Subdirectory" within the S3 bucket to save reports.

        Defaults to '', which means the root directory. S3 calls paths
        "keys" which is why the keyPrefix is like a subdirectory.
        """,
    default_val = '')

_create_option('s3.region',
    description = """AWS region where the bucket is located.

        The AWS region, for example 'us-west-2'. Defaults to None.
        """,
    default_val = None)

_create_option('s3.profile',
    description = """AWS credentials profile to use for saving data.

        Defaults to None.
        """,
    default_val = None)

@util.memoize
def _get_default_credentials():
    STREAMLIT_CREDENTIALS_URL = 'http://streamlit.io/tmp/st_pub_write.json'
    LOGGER.info('Getting credentials from ' + STREAMLIT_CREDENTIALS_URL)
    try:
        response = urllib.request.urlopen(
            STREAMLIT_CREDENTIALS_URL, timeout=0.5).read()
        return ast.literal_eval(response.decode('utf-8'))
    except Exception as e:
        LOGGER.info(
            'Error getting Streamlit credentials. Sharing will be '
            'disabled. %s', e)
        return None

### Config Section: Client ###

_create_section('client', 'Configuration of browser front-end.')

_create_option('client.remotelyTrackUsage',
    description = 'Whether to send usage statistics to Streamlit.',
    default_val = True)



### Public Interface ###

def set_option(key, value):
    """Ses the config option.

    Note that some config parameters depend on others, so changing one parameter
    may affect others in unexpected ways.

    Parameters
    ----------
    key : string
        The config option key of the form "section.optionName"
    value
        The new value of the parameter.

    """
    _set_option(key, value, _USER_DEFINED)

def get_option(key):
    """Return the config option with the given key.

    Parameters
    ----------
    key : string
        The config option key of the form "section.optionName"

    """
    if key not in _config_options:
        raise RuntimeError('Config key "%s" not defined.' % key)
    return _config_options[key].value

def get_where_defined(key):
    """Indicate where (e.g. in which file) this option was defined.

    Parameters
    ----------
    key : string
        The config option key of the form "section.optionName"

    """
    if key not in _config_options:
        raise RuntimeError('Config key "%s" not defined.' % key)
    return _config_options[key].where_defined



### Load Config Files ###

# Indicates that this was defined by the user.
_USER_DEFINED = '<user defined>'

def _set_option(key, value, where_defined):
    """Sets a config option by key / value pair.

    Parameters
    ----------
    key : string
        The key of the option, like "global.logLevel".
    value
        The value of the option.
    where_defined : string
        Tells the config system where this was set.
    """
    assert key in _config_options, 'Key "%s" is not defined.' % key
    _config_options[key].set_value(value, where_defined)

def _update_config_with_toml(raw_toml, where_defined):
    """Updates the config system by parsing this string.

    Parameters
    ----------
    raw_toml : string
        The TOML file to parse to update the config values.
    where_defined : string
        Tells the config system where this was set.
    """
    all_sections = toml.loads(raw_toml)
    for section, options in all_sections.items():
        for name, value in options.items():
            _set_option(f'{section}.{name}', value, where_defined)

def _parse_config_file():
    """Parse the config file and update config parameters."""
    # Find the path to the config file.
    home = os.getenv('HOME', None)
    if home is None:
        raise RuntimeError('No home directory.')
    config_fileanme = os.path.join(home, '.streamlit', 'config.toml')

    # Parse the config file.
    if not os.path.exists(config_fileanme):
        return
    with open(config_fileanme) as input:
        _update_config_with_toml(input.read(), config_fileanme)

# Acually parse the config file.
_parse_config_file()
