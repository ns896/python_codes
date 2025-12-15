"""
Author: Navneet Singh
iostats_hdf5_plotter.py
This script generates plots for all columns in the HDF5 iostat data file

Usage:
    python iostats_hdf5_plotter.py input.h5 [--output-dir output_folder]
"""

import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import argparse
import os
import sys


def read_hdf5_data(file_path: str):
    """Read data from HDF5 file"""
    try:
        with h5py.File(file_path, 'r') as f:
            if 'iostat_data' not in f:
                raise ValueError(f"Dataset 'iostat_data' not found in {file_path}")
            
            dataset = f['iostat_data']
            data = dataset[:]
            
            # Get column names from dtype
            column_names = [name for name, _ in dataset.dtype.descr]
            
            # Extract timestamp
            timestamps = data['time_stamp_unix']
            
            # Convert to datetime if timestamps are valid
            if len(timestamps) > 0 and timestamps[0] > 0:
                times = [datetime.fromtimestamp(ts) for ts in timestamps]
            else:
                # Use index as time if timestamps are invalid
                times = list(range(len(timestamps)))
            
            print(f"Loaded {len(data)} records from {file_path}")
            return data, column_names, times
            
    except Exception as e:
        print(f"Error reading HDF5 file: {e}", file=sys.stderr)
        sys.exit(1)


def plot_column(data, column_name, times, output_path, title_suffix=""):
    """Plot a single column vs time"""
    try:
        values = data[column_name]
        
        # Skip string columns for plotting
        if values.dtype.kind in ['S', 'U']:
            return False
        
        # Skip if all values are zero or NaN
        if np.all(np.isnan(values)) or np.all(values == 0):
            print(f"  Skipping {column_name}: all values are zero or NaN")
            return False
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the data
        ax.plot(times, values, linewidth=1.5, alpha=0.8)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel(column_name.replace('_', ' ').title(), fontsize=12)
        
        # Format title
        title = f"{column_name.replace('_', ' ').title()}"
        if title_suffix:
            title += f" - {title_suffix}"
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Format x-axis if using datetime
        if isinstance(times[0], datetime):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.xticks(rotation=45)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Add statistics text
        mean_val = np.nanmean(values)
        max_val = np.nanmax(values)
        min_val = np.nanmin(values)
        stats_text = f"Mean: {mean_val:.2f} | Max: {max_val:.2f} | Min: {min_val:.2f}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return True
        
    except Exception as e:
        print(f"  Error plotting {column_name}: {e}")
        return False


def plot_calculated_metric(data, numerator_col, denominator_col, times, output_path, metric_name="", title=""):
    """Plot a calculated metric (numerator / denominator)"""
    try:
        # Check if both columns exist
        if numerator_col not in data.dtype.names:
            print(f"  Skipping {metric_name}: column '{numerator_col}' not found")
            return False
        if denominator_col not in data.dtype.names:
            print(f"  Skipping {metric_name}: column '{denominator_col}' not found")
            return False
        
        numerator = data[numerator_col]
        denominator = data[denominator_col]
        
        # Check if columns are numeric
        if numerator.dtype.kind in ['S', 'U'] or denominator.dtype.kind in ['S', 'U']:
            print(f"  Skipping {metric_name}: columns must be numeric")
            return False
        
        # Calculate the ratio, handling division by zero and NaN
        with np.errstate(divide='ignore', invalid='ignore'):
            calculated_values = np.divide(numerator, denominator)
            calculated_values = np.where(np.isfinite(calculated_values), calculated_values, np.nan)
        
        # Skip if all values are NaN or zero
        if np.all(np.isnan(calculated_values)) or np.all(calculated_values == 0):
            print(f"  Skipping {metric_name}: all calculated values are zero or NaN")
            return False
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the calculated data
        ax.plot(times, calculated_values, linewidth=1.5, alpha=0.8, color='purple')
        ax.set_xlabel('Time', fontsize=12)
        
        # Set ylabel and title
        if title:
            ylabel = title
            plot_title = title
        else:
            ylabel = f"{numerator_col}/{denominator_col}"
            plot_title = f"{numerator_col}/{denominator_col}"
        
        ax.set_ylabel(ylabel.replace('_', ' ').title(), fontsize=12)
        ax.set_title(plot_title.replace('_', ' ').title(), fontsize=14, fontweight='bold')
        
        # Format x-axis if using datetime
        if isinstance(times[0], datetime):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.xticks(rotation=45)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Add statistics text
        mean_val = np.nanmean(calculated_values)
        max_val = np.nanmax(calculated_values)
        min_val = np.nanmin(calculated_values)
        stats_text = f"Mean: {mean_val:.2f} | Max: {max_val:.2f} | Min: {min_val:.2f}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return True
        
    except Exception as e:
        print(f"  Error plotting calculated metric {metric_name}: {e}")
        return False


def plot_grouped(data, column_groups, times, output_dir, group_name):
    """Create grouped subplots for related metrics"""
    try:
        # Filter out columns that don't exist or are invalid
        valid_groups = {}
        for group_title, columns in column_groups.items():
            valid_cols = []
            for col in columns:
                if col in data.dtype.names:
                    values = data[col]
                    if values.dtype.kind not in ['S', 'U'] and not (np.all(np.isnan(values)) or np.all(values == 0)):
                        valid_cols.append(col)
            if valid_cols:
                valid_groups[group_title] = valid_cols
        
        if not valid_groups:
            return False
        
        # Create subplots (2x2 or 2x3 layout)
        num_groups = len(valid_groups)
        cols = 2
        rows = (num_groups + 1) // 2
        
        fig, axes = plt.subplots(rows, cols, figsize=(16, 6 * rows))
        if rows == 1:
            axes = axes.reshape(1, -1)
        axes = axes.flatten()
        
        for idx, (group_title, columns) in enumerate(valid_groups.items()):
            if idx >= len(axes):
                break
            
            ax = axes[idx]
            for col in columns:
                values = data[col]
                label = col.replace('_', ' ').title()
                ax.plot(times, values, label=label, linewidth=1.5, alpha=0.7)
            
            ax.set_title(group_title, fontsize=12, fontweight='bold')
            ax.set_xlabel('Time', fontsize=10)
            ax.set_ylabel('Value', fontsize=10)
            ax.legend(loc='best', fontsize=8)
            ax.grid(True, alpha=0.3)
            
            # Format x-axis if using datetime
            if isinstance(times[0], datetime):
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Hide unused subplots
        for idx in range(len(valid_groups), len(axes)):
            axes[idx].set_visible(False)
        
        plt.suptitle(f"{group_name} - Grouped Metrics", fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{group_name}_grouped.png"), dpi=150, bbox_inches='tight')
        plt.close()
        
        return True
        
    except Exception as e:
        print(f"  Error creating grouped plot {group_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Generate plots from iostat HDF5 data file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
                Examples:
                python iostats_hdf5_plotter.py test_output.h5
                python iostats_hdf5_plotter.py test_output.h5 --output-dir plots
                python iostats_hdf5_plotter.py test_output.h5 --output-dir plots --no-grouped
        """
    )
    parser.add_argument('input_file', help='Input HDF5 file path')
    parser.add_argument('--output-dir', default='iostat_plots',
                        help='Output directory for plots (default: iostat_plots)')
    parser.add_argument('--no-grouped', action='store_true',
                        help='Skip creating grouped plots')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Output directory: {args.output_dir}")
    print("-" * 60)
    
    # Read data
    data, column_names, times = read_hdf5_data(args.input_file)
    
    # Define column groups for grouped plots
    column_groups = {
        'Requests Per Second': ['r_s', 'w_s', 'd_s', 'f_s'],
        'Data Transfer (kB/s)': ['rkB_s', 'wkB_s', 'dkB_s'],
        'Merged Requests Per Second': ['rrqm_s', 'wrqm_s', 'drqm_s'],
        'Merged Requests': ['rrqm', 'wrqm', 'drqm'],
        'Wait Times (ms)': ['r_await', 'w_await', 'd_await', 'f_await'],
        'Request Sizes (kB)': ['rareq_sz', 'wareq_sz', 'dareq_sz'],
        'Queue & Utilization': ['aqu_sz', 'util'],
    }
    
    # Plot individual columns
    print("\nGenerating individual plots...")
    plotted_count = 0
    skipped_columns = ['disk_device', 'time_stamp_unix', 'time_stamp_iso']  # Skip these
    
    for col_name in column_names:
        if col_name in skipped_columns:
            continue
        
        output_path = os.path.join(args.output_dir, f"{col_name}.png")
        if plot_column(data, col_name, times, output_path):
            plotted_count += 1
            print(f"  ✓ {col_name}")
    
    print(f"\nGenerated {plotted_count} individual plots")
    
    # Plot calculated metrics
    print("\nGenerating calculated metric plots...")
    calculated_metrics = [
        ('wareq_sz', 'w_await', 'wareq_sz_w_await_ratio', 'Write Request Size / Write Wait Time (kB/ms)'),
    ]
    
    calculated_count = 0
    for num_col, den_col, filename, title in calculated_metrics:
        output_path = os.path.join(args.output_dir, f"{filename}.png")
        if plot_calculated_metric(data, num_col, den_col, times, output_path, metric_name=filename, title=title):
            calculated_count += 1
            print(f"  ✓ {title}")
    
    if calculated_count > 0:
        print(f"\nGenerated {calculated_count} calculated metric plot(s)")
    
    # Create grouped plots
    if not args.no_grouped:
        print("\nGenerating grouped plots...")
        grouped_count = 0
        for group_name, columns in column_groups.items():
            if plot_grouped(data, {group_name: columns}, times, args.output_dir, group_name.lower().replace(' ', '_')):
                grouped_count += 1
                print(f"  ✓ {group_name}")
        
        if grouped_count > 0:
            print(f"\nGenerated {grouped_count} grouped plots")
    
    # Create summary plot
    print("\nGenerating summary plot...")
    try:
        fig, axes = plt.subplots(3, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        key_metrics = [
            ('util', 'Utilization (%)'),
            ('r_s', 'Read IOPS'),
            ('w_s', 'Write IOPS'),
            ('rkB_s', 'Read kB/s'),
            ('wkB_s', 'Write kB/s'),
            ('aqu_sz', 'Average Queue Size'),
        ]
        
        for idx, (col_name, title) in enumerate(key_metrics):
            if idx >= len(axes):
                break
            if col_name not in data.dtype.names:
                continue
            
            ax = axes[idx]
            values = data[col_name]
            
            if values.dtype.kind not in ['S', 'U'] and not (np.all(np.isnan(values)) or np.all(values == 0)):
                ax.plot(times, values, linewidth=1.5, alpha=0.8)
                ax.set_title(title, fontsize=12, fontweight='bold')
                ax.set_xlabel('Time', fontsize=10)
                ax.set_ylabel(title, fontsize=10)
                ax.grid(True, alpha=0.3)
                
                if isinstance(times[0], datetime):
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Hide unused subplots
        for idx in range(len(key_metrics), len(axes)):
            axes[idx].set_visible(False)
        
        plt.suptitle('IOStat Summary - Key Metrics', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(args.output_dir, 'summary.png'), dpi=150, bbox_inches='tight')
        plt.close()
        print("  ✓ Summary plot created")
    except Exception as e:
        print(f"  Error creating summary plot: {e}")
    
    print("\n" + "=" * 60)
    print(f"✅ All plots generated successfully!")
    print(f"📁 Output directory: {os.path.abspath(args.output_dir)}")
    print("=" * 60)


if __name__ == "__main__":
    main()

