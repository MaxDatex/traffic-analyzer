import argparse
from core.video_processor import process_video
from config.config_handler import DetectorConfig, load_config, save_config
import os


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Vehicle tracking and speed detection system",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Config file arguments
    parser.add_argument(
        "--config", "-c", type=str, help="Path to YAML configuration file"
    )

    parser.add_argument(
        "--input",
        "-i",
        type=str,
        help="Path to input video file",
        required=True,
    )

    parser.add_argument("--output", "-o", type=str, help="Path to output video file")

    parser.add_argument(
        "--analysis",
        type=str,
        choices=["simple", "linreg"],
        help="Type of trend analysis to use",
    )

    parser.add_argument(
        "--draw-tracks", action="store_true", help="Draw tracking lines for vehicles"
    )

    parser.add_argument(
        "--draw-direction",
        action="store_true",
        help="Draw direction arrows for vehicles",
    )

    parser.add_argument(
        "--show", action="store_true", help="Show processing in real-time"
    )

    return parser.parse_args()


def main():
    """Main function for CLI operation."""
    args = parse_args()

    # try:
    # Load configuration
    if args.config:
        config = load_config(args.config)
    else:
        if not args.input:
            raise ValueError("Either --config or --input must be specified")
        config = DetectorConfig()

    # Update config with command line arguments
    config.update_from_args(args)

    output = args.output
    if not os.path.isabs(args.input):
        args.input = os.path.join(config.base_dir, args.input)
    process_video(video_path=args.input, config=config, output_path=output)
    return 0


main()
