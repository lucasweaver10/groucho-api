workers = 1
threads = 1
worker_class = 'uvicorn.workers.UvicornWorker'
timeout = 320
keepalive = 65

disable_redirect_access_to_syslog = True

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True

logconfig_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
    }
}
