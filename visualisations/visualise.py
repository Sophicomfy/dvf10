# run by python3 visualise.py ../logs/

import matplotlib.pyplot as plt
import numpy as np
import os
import sys

def plot_metric(metric, train_values, val_values, title):
    min_length = min(len(train_values), len(val_values))
    train_values = train_values[:min_length]
    val_values = val_values[:min_length]
    epochs = range(1, min_length + 1)
    plt.figure()
    plt.plot(epochs, train_values, 'bo-', label=f'Training {metric}')
    plt.plot(epochs, val_values, 'r-', label=f'Validation {metric}')
    plt.title(title)
    plt.xlabel('Epochs')
    plt.ylabel(metric)
    plt.legend()
    plt.grid(True)
    print(f"Plotting {title}")
    print(f"Training {metric}: min={min(train_values)}, max={max(train_values)}, mean={np.mean(train_values)}")
    print(f"Validation {metric}: min={min(val_values)}, max={max(val_values)}, mean={np.mean(val_values)}")

def extract_loss_values(log_lines):
    loss_values = []
    for line in log_lines:
        try:
            parts = line.split(',')
            loss_part = parts[2].split(':')[-1].strip()
            loss_value = float(loss_part)
            loss_values.append(loss_value)
        except (IndexError, ValueError):
            continue
    return loss_values

def load_and_plot_log(log_dir, train_log_file, val_log_file, metric, title):
    train_log_path = os.path.join(log_dir, train_log_file)
    val_log_path = os.path.join(log_dir, val_log_file)

    with open(train_log_path, 'r') as f:
        train_lines = f.readlines()
        train_values = extract_loss_values(train_lines)

    with open(val_log_path, 'r') as f:
        val_lines = f.readlines()
        val_values = extract_loss_values(val_lines)

    if len(train_values) == 0 or len(val_values) == 0:
        print(f"Skipping {title}: insufficient data.")
        return

    plot_metric(metric, train_values, val_values, title)

def process_logs(log_dir):
    train_files = {}
    val_files = {}

    for filename in os.listdir(log_dir):
        if 'train_loss_log' in filename:
            prefix = filename.split('_train_loss_log')[0]
            train_files[prefix] = filename
        elif 'val_loss_log' in filename:
            prefix = filename.split('_val_loss_log')[0]
            val_files[prefix] = filename

    print("Found training files:", train_files)
    print("Found validation files:", val_files)

    for prefix in train_files:
        if prefix in val_files:
            train_log_file = train_files[prefix]
            val_log_file = val_files[prefix]
            title = f'{prefix.replace("_", " ").title()} Training and Validation Loss'
            try:
                load_and_plot_log(log_dir, train_log_file, val_log_file, 'Loss', title)
            except Exception as e:
                print(f"Skipping {title}: {str(e)}")
        else:
            print(f"Skipping {prefix.replace('_', ' ').title()} Training and Validation Loss: no matching validation file.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python visualise.py <path_to_logs_directory>")
        sys.exit(1)

    log_dir = sys.argv[1]
    if not os.path.exists(log_dir):
        print(f"The directory {log_dir} does not exist.")
        sys.exit(1)

    process_logs(log_dir)
    plt.show()
