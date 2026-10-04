import logging
import json
import time
import sys
import ast

## Below class is just to format the logging informtion in JSON or dict format, as GCP Cloud logging have functionaly to query on the 
## log file which is in JSON or dict fomrat

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "severity": record.levelname#,
            #"message": record.getMessage(),
        }
        try:
            message_body = ast.literal_eval(record.getMessage())
        except Exception as e:
            message_body = str(record.getMessage())
        if type(message_body) is str:
            log_entry["message"] = message_body
        if type(message_body) is dict:
            for k,v in message_body.items():
                log_entry[k] = v
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        return json.dumps(log_entry)

def get_logger(logger_name,log_level):
    logger = logging.getLogger(logger_name)
    if log_level.strip().upper() == "INFO":
        logger.setLevel(logging.INFO)
    elif log_level.strip().upper() == "WARNING":
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.ERROR)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    return logger
