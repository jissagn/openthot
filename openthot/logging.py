import logging
import os
import sys

from simplejson import JSONEncoder
from structlog import wrap_logger
from structlog.processors import (
    ExceptionPrettyPrinter,
    StackInfoRenderer,
    TimeStamper,
    UnicodeDecoder,
    _json_fallback_handler,
    format_exc_info,
)
from structlog.stdlib import (
    PositionalArgumentsFormatter,
    add_logger_name,
    filter_by_level,
)


class LoggingFormat(object):
    HUMAN = "human"
    MACHINE = "machine"


# Read environment variable
LOG_LEVEL = os.environ.get("LOG_LEVEL", default=logging.INFO)
LOG_FORMAT = os.environ.get("LOG_FORMAT", default=LoggingFormat.HUMAN)

handler = logging.StreamHandler(sys.stdout)
root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(LOG_LEVEL)

# Update default logging level for werkzeug debugger
werkzeug_log = logging.getLogger("werkzeug")
werkzeug_log.setLevel(logging.WARNING)

default_encoder = JSONEncoder(
    separators=(",", ":"),
    ignore_nan=True,
    skipkeys=False,
    ensure_ascii=True,
    check_circular=True,
    allow_nan=True,
    indent=None,
    encoding="utf-8",
    default=_json_fallback_handler,
).encode


class JSONRenderer(object):
    def __call__(self, logger, name, event_dict):
        return default_encoder(event_dict)


class ConsoleRenderer(object):
    def __call__(self, logger, name, event_dict):
        string = "{timestamp} [{level}] {logger_name}: {msg}".format(
            timestamp=event_dict.pop("timestamp"),
            level=event_dict.pop("severity"),
            logger_name=event_dict.pop("logger", "root"),
            msg=event_dict.pop("msg", None) or event_dict.pop("message", None),
        )
        if extra := event_dict.get("extra", {}):
            string += " [{extra}]".format(
                extra=" ".join(k + "=" + repr(v) for k, v in extra.items())
            )

        return string


def add_loger_severity(_, method_name, event_dict):
    # add log severity to be compliant with stackdriver
    event_dict["severity"] = method_name.upper()
    return event_dict


def render_to_log_kwargs(wrapped_logger, method_name, event_dict):
    event = event_dict.pop("event")
    if event:
        return {"message": event, **event_dict}
    else:
        return event_dict


def getLogger(name=None):
    # list of all processors used by structlog
    processors = [
        filter_by_level,
        add_logger_name,
        add_loger_severity,
        PositionalArgumentsFormatter(),
        StackInfoRenderer(),
        format_exc_info,
        TimeStamper(fmt="iso"),
        UnicodeDecoder(),
        render_to_log_kwargs,
    ]

    if LOG_FORMAT == LoggingFormat.HUMAN:
        processors.extend([ExceptionPrettyPrinter(), ConsoleRenderer()])
    else:
        processors.extend([JSONRenderer()])

    return wrap_logger(
        logging.getLogger(name),
        processors=processors,
        context_class=dict,
        cache_logger_on_first_use=False,
    )
