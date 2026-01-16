#!/usr/bin/env python3
"""
KRV CAN Bus Engine - Main Entry Point

This script provides the command-line interface for the KRV CAN Bus Engine.
It handles argument parsing and initializes the CAN bus monitoring process.
"""

import argparse
import sys
import os
from pathlib import Path
import time

from krv_logger.krv_logger import KRV_Logger
from can_engine import KRV_CanEngine

def parse_arguments():
    """
    Parse command-line arguments for the KRV CAN Bus Engine.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description='KRV CAN Bus Engine - Monitor and log CAN bus traffic using DBC files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        # Run TUI interface
        python main.py --dbc example.dbc --port can0 --output ./logs --tui

        # Run TUI interface with filter IDs
        python main.py --dbc example.dbc --port can0 --output ./logs --tui --filter-ids 0x123,0x456
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--dbc',
        type=str,
        required=True,
        help='Path to the DBC (Database Container) file that defines CAN message structure'
    )
    
    parser.add_argument(
        '--port',
        type=str,
        required=True,
        help='CAN bus IP port/address (format: can0, vcan0, etc.)'
    )

    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output directory where log files will be saved'
    )

    # Optional arguments
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set the logging level (default: INFO)'
    )

    parser.add_argument(
        '--tui',
        action='store_true',
        help='Launch TUI interface instead of logging to file'
    )

    parser.add_argument(
        '--filter-ids',
        type=str,
        help='Comma-separated list of message IDs to filter (e.g., 0x123,0x456 or 291,1234)'
    )

    return parser.parse_args()


def validate_arguments(args):
    """
    Validate the provided command-line arguments.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        bool: True if all validations pass
        
    Raises:
        SystemExit: If validation fails
    """
    # Validate DBC file exists
    if not os.path.isfile(args.dbc):
        print(f"Error: DBC file not found: {args.dbc}", file=sys.stderr)
        sys.exit(1)
    
    # Validate and create output directory
    output_path = Path(args.output)
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error: Cannot create output directory '{args.output}': {e}", file=sys.stderr)
        sys.exit(1)
   
    return True


def main():
    """
    Main entry point for the KRV CAN Bus Engine.
    """
    args = parse_arguments()
    validate_arguments(args)

    log_ = KRV_Logger(name="KRV_CanENGINE", output_dir=args.output, file_name="KRV_CanENGINE", level=args.log_level)
    LOG = log_.get_logger()

    LOG.info(">-*--*--*--*-  Jai Guru Dev  -*--*--*--*--*-<")
    LOG.info(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    LOG.info(f"DBC File: {args.dbc}")
    LOG.info(f"CAN Port: {args.port}")
    LOG.info(f"Output Dir: {args.output}")
    LOG.info(f"Log Level: {args.log_level}")
    LOG.info("-" * 60)
    LOG.info("")

    can_engine = KRV_CanEngine(dbc_file=args.dbc, can_port=args.port)

    if args.tui:
        # Launch TUI interface
        from can_engine_gui import CANMessageTUI
        
        # Parse filter IDs if provided
        filter_ids = None
        if args.filter_ids:
            try:
                filter_ids = []
                for id_str in args.filter_ids.split(','):
                    id_str = id_str.strip()
                    if id_str.startswith('0x') or id_str.startswith('0X'):
                        filter_ids.append(int(id_str, 16))
                    else:
                        filter_ids.append(int(id_str))
            except ValueError as e:
                LOG.error(f"Invalid filter ID format: {e}")
                print(f"Error: Invalid filter ID format. Use hex (0x123) or decimal (291)", file=sys.stderr)
                sys.exit(1)
        
        # Start TUI
        tui = CANMessageTUI(can_engine=can_engine, filter_ids=filter_ids)
        tui.start()  # Use start() method from BasicTUI which handles curses.wrapper
    else:
        # Logging mode - write to file
        while True:
            try:
                message = can_engine.next()
                if message is not None:
                    LOG.info(f"Message: {message}")
                else:
                    LOG.warning("No message received")
                    time.sleep(0.01)
            except KeyboardInterrupt:
                LOG.info("Interrupted by user. Shutting down...")
                can_engine.can_receiver_destructor()
                break


if __name__ == '__main__':
    main()
