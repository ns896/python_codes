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
  # Run for 60 seconds
  python main.py --dbc example.dbc --port 192.168.1.100:8080 --output ./logs --duration 60
  
  # Process 1000 frames
  python main.py --dbc example.dbc --port 192.168.1.100:8080 --output ./logs --frames 1000
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
    
    # Validate DBC file extension
    if not args.dbc.lower().endswith('.dbc'):
        print(f"Warning: DBC file does not have .dbc extension: {args.dbc}", file=sys.stderr)
    
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
    # Parse command-line arguments
    args = parse_arguments()
    
    # Validate arguments
    validate_arguments(args)

    # Initialize logger
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

    while True:
        message = can_engine.next()
        if message is not None:
            LOG.info(f"Message: {message}")
        else:
            LOG.warning("No message received")
            time.sleep(0.01)
        

if __name__ == '__main__':
    main()
