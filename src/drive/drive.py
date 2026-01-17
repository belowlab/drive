from datetime import datetime
from importlib.metadata import version
import sys

from log import CustomLogger

from drive.parser import generate_cmd_parser
from drive.helper_funcs import generate_random_logfile_suffix


def main() -> None:
    parser = generate_cmd_parser()

    args = parser.parse_args()

    # Getting the program's start time
    start_time = datetime.now()

    # creating and configuring the logger and then recording user inputs
    logger = CustomLogger.create_logger()

    if not hasattr(args, "output"):
        logger.configure("", None, args.verbose, args.log_to_console)
    elif args.output.is_dir():
        logger.configure(
            args.output, args.log_filename, args.verbose, args.log_to_console
        )
    else:
        # add logic to check if the log file already exists and then we can add a
        # random identifier to the name to make it unique

        full_log_path = args.output.parent / args.log_filename

        if full_log_path.exists():
            args.log_filename = generate_random_logfile_suffix(args.log_filename)

        logger.configure(
            args.output.parent, args.log_filename, args.verbose, args.log_to_console
        )

    logger.info(f"DRIVE version: {version('drive-ibd')}")

    logger.info(f"command passed to DRIVE: {' '.join(sys.argv)}\n")

    # record the input parameters using a method from the logger object that
    # takes the parser as an argument
    logger.record_namespace(args)
    # We need to record the output directory when we run DRIVE unless it's for unit test
    if hasattr(args, "output"):
        logger.debug(f"Parent directory for log files and output: {args.output.parent}")

    logger.info(f"Analysis start time: {start_time}")

    args.func(args)

    end_time = datetime.now()

    logger.info(
        f"Analysis finished at {end_time}. Total runtime: {end_time - start_time}"
    )


if __name__ == "__main__":
    main()
