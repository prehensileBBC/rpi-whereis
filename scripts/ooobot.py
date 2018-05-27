import logging
import os
import datetime

from exchangelib import Credentials, Account, Configuration, OofSettings, EWSDateTime

import jinja2
import keyring
from num2words import num2words

import utils


_IDENTIFIER="ooobot"


def ews_account():

    # TODO:  get from a keychain
    #ews_password = None
    # ews_password = input( "Password: " )
    ews_password = keyring.get_password( _IDENTIFIER, "master" )

    credentials = Credentials(
        os.environ.get( "EWS_ACCOUNT" ),
        ews_password
    )

    config = Configuration(
        server=os.environ.get( "EWS_SERVER" ),
        has_ssl=True,
        credentials=credentials
    )

    a = Account(
        primary_smtp_address=os.environ.get( "EWS_SMTP_ADDRESS" ),
        credentials=credentials,
        config=config
    )

    return a


def set_ooo( internal_reply, external_reply, dt_start, next_tuesday ):

    a = ews_account()

    # for some reason, creating a timezone from scracth is b0rked. 
    # use the existing timezone
    settings = a.oof_settings
    tz_ews = settings.start.tzinfo
    oof_start = EWSDateTime.from_datetime( dt_start )
    oof_end = EWSDateTime.from_datetime( next_tuesday )


    oof_settings = OofSettings(
        state = OofSettings.SCHEDULED,
        external_audience = 'All',
        internal_reply = internal_reply,
        external_reply = external_reply,
        start = tz_ews.localize( oof_start ),
        end = tz_ews.localize( oof_end )
    )

    a.oof_settings = oof_settings


def render_replies( next_tuesday ):

    template_path = os.path.join(
        os.path.dirname( __file__ ),
        "templates"
    )

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader( template_path ),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
    )
    
    tue_formatted = "{} {}".format(
        next_tuesday.strftime( "%A, %B" ),
        num2words( next_tuesday.day, to='ordinal_num' )
    )

    rendered_internal = env.get_template( 'ooo_internal.html' ).render(
        next_tuesday = tue_formatted
    )

    rendered_external = env.get_template( 'ooo_external.html' ).render(
        next_tuesday = tue_formatted
    )

    return rendered_internal, rendered_external


def run():

    """ Set an out-of-office mesage every Friday. """

    # now
    now = datetime.datetime.now()
    
    # today at 0900
    dt = datetime.datetime(
        now.year, now.month, now.day,
        8, 0
    )
    
    # next tuesday
    now_day = now.weekday()  # Monday is 0 and Sunday is 6
    days_delta = (6 - now_day) + 2

    # 0900 next tuesday
    next_tuesday = dt + datetime.timedelta( days=days_delta )
    
    # today at 1600 (ooo start datetime)
    dt_start = datetime.datetime(
        now.year, now.month, now.day,
        15, 0
    )

    # render ooo templates
    rendered_internal, rendered_external = render_replies( next_tuesday )

    # set ooo!
    set_ooo( rendered_internal, rendered_external, dt_start, next_tuesday )
    


if __name__ == '__main__':
    utils.init_logging( log_identifier=_IDENTIFIER )
    try:
        run()
    except Exception as e:
        logging.exception( e )
        raise e
