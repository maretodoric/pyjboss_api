from logging import Formatter, StreamHandler, ERROR, getLogger

module_initialized = False

log = getLogger(__name__)

if not module_initialized:
    module_initialized = True

    # Set logging level and formatter
    log.setLevel(ERROR)
    log.propagate = False
    fmt = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)")

    # create console handler with a higher log level
    ch = StreamHandler()
    ch.setLevel(ERROR)
    ch.setFormatter(fmt)

    # Remove any existing log handlers, this fixes double log message printing on restart/update
    while log.hasHandlers():
        log.removeHandler(log.handlers[0])

    log.addHandler(ch)
