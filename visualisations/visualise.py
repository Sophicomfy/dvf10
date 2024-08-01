# run by python3 visualise.py ../logs/

import matplotlib.pyplot as plt
import numpy as np
import os
import sys

def plot_metric(metric, train_values, val_values, title):
    epochs = range(1, len(train_values) + 1)
    plt.plot(epochs, train_values, 'bo-', label=f'Training {metric}')
    plt.plot(epochs, val_values, 'r-', label=f'Validation {metric}')
    plt.title(title)
    plt.xlabel('Epochs')
    plt.ylabel(metric)
    plt.legend()
    plt.show()

def load_and_plot_log(log_dir, train_log_file, val_log_file, metric, title):
    train_log_path = os.path.join(log_dir, train_log_file)
    val_log_path = os.path.join(log_dir, val_log_file)
    with open(train_log_path, 'r') as f:
        train_values = [float(line.strip()) for line in f]
    with open(val_log_path, 'r') as f:
        val_values = [float(line.strip()) for line in f]
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
    for prefix in train_files:
        if prefix in val_files:
            train_log_file = train_files[prefix]
            val_log_file = val_files[prefix]
            title = f'{prefix.replace("_", " ").title()} Training and Validation Loss'
            load_and_plot_log(log_dir, train_log_file, val_log_file, 'Loss', title)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python visualise.py <log_directory>")
        sys.exit(1)
    log_dir = sys.argv[1]
    process_logs(log_dir)