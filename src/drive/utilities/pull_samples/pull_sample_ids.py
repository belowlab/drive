from log import CustomLogger

logger = CustomLogger.get_logger(__name__)


def run_pull_samples(args) -> None:

    with open(args.input, "r", encoding="utf-8") as drive_results:
        samples = []
        _ = next(drive_results)
        for line in drive_results:
            split_line = line.strip().split("\t")
            if split_line[0] == args.network_id:
                samples = split_line[6].strip().split(",")
                break
        if len(samples) != 0:
            with open(args.output, "w", encoding="utf-8") as output_file:
                for grid in samples:
                    output_file.write(f"{grid}\n")
        else:
            logger.critical(
                f"The network id, {args.network_id}, was not found within the networks file at {args.input}. Please ensure that all of the network ids are properly formatted and that the network is present within your input file."
            )
