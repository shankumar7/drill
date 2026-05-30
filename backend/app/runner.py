import argparse
import logging

from backend.core.config import AppConfig, load_config
from backend.core.logging_utils import configure_logging
from backend.core.pipeline import Phase1Pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Military Drill Intelligence System - Phase 1")
    parser.add_argument("--config", default="configs/phase3.yaml")
    parser.add_argument("--source", help="Camera index or video path override")
    parser.add_argument("--mode", choices=["SAVDHAN", "VISHRAM"], help="Evaluation mode override")
    parser.add_argument("--headless", action="store_true", help="Disable OpenCV debug window")
    return parser


from backend.app.gui import run_gui


def run() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)
    if args.source is not None:
        config.runtime.source = int(args.source) if args.source.isdigit() else args.source
    if args.headless:
        config.runtime.display = False
    if args.mode is not None:
        config.evaluation.mode = args.mode

    configure_logging(config.logging.level)
    logging.getLogger(__name__).info("Starting Phase 1 pipeline")

    pipeline = Phase1Pipeline(config)
    
    if args.headless:
        pipeline.run_forever()
    else:
        run_gui(pipeline)
