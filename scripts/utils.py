import logging, sys 


def init_logging( level=logging.DEBUG, to_stdout=True, to_syslog=True, log_identifier=None ):

    logger = logging.getLogger()
    logger.setLevel( level )

    if to_stdout:
        
        handler = logging.StreamHandler( sys.stdout )
        logger.addHandler( handler )

    if to_syslog:
        
        log_address = '/var/run/syslog' if sys.platform == 'darwin' else '/dev/log'
        handler = logging.handlers.SysLogHandler( address=log_address )
        if idenfitier is not None:
            formatter = logging.Formatter( '{}: %(message)s'.format(idenfitier) )
            handler.setFormatter( formatter )
        logger.addHandler( handler )
