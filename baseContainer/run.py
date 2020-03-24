#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper for all scripts inside the docker container. It provides error-log
redaction for unhandled exceptions that might occur in the wrapped scripts.

The scripts that should be executed must be supplied by the `RUN` environment
variable as space-separated filenames without the `.py` ending.
"""

import os
import sys
import redacted_logging as rlog


def redacted_excepthook(logger):
    """Supplies a modified excepthook that enables logging redaction.

    Usage: sys.excepthook = redacted_excepthook(logger)

    Args:
        logger (logging.Logger): Logger class that is used to handle the log
                                 messages.
    """
    def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
        """ Handler for unhandled exceptions that will write to the logs.

        Any unhandled exceptions will be properly logged to `logger`, even if
        not implemented in the code itself. `KeyboardInterrupt` is an exception
        and will exit normally, as it should not come as a surprise to the
        user.

        Args:
            exc_type (type): Type of the error
            exc_value (Error): Error object
            exc_traceback (traceback): Traceback message
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # call the default excepthook saved at __excepthook__
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value,
                                                         exc_traceback))

    return handle_unhandled_exception


def main():
    """Main function

    Executes the scripts listed in the `RUN` environment variable, one after
    another. Unhandled exceptions of these scripts will be redacted and logged.
    """
    logger = rlog.get_logger(__name__)
    sys.excepthook = redacted_excepthook(logger)

    script_list = []
    try:
        script_list = os.environ["RUN"].split()
    except KeyError:
        logger.error("No environment variable 'RUN' set. Please run docker "
                     "with '-e RUN=\"script_1 script_2 script_...\"'.")

    for script in script_list:
        try:
            module = __import__(script, fromlist=["main"])
            module.main()
        except ModuleNotFoundError:
            logger.error("No script named '" + script + "' supplied by the " +
                         "container. Please consult the README.md for valid " +
                         "options.")


if __name__ == "__main__":
    main()
