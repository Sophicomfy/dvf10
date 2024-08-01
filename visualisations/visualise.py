import pandas as pd
import matplotlib.pyplot as plt

# Load the log files
train_log_path = '/Users/flp/Desktop/git/dvf-extended/logs/train_loss_log.txt'
val_log_path = '/Users/flp/Desktop/git/dvf-extended/logs/val_loss_log.txt'

# Function to parse log files
def parse_log_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split(',')
            if len(parts) < 3:  # Ensure there are at least three parts to avoid IndexError
                continue
            epoch_info = parts[0].split(':')[-1].strip().split('/')
            try:
                epoch = int(epoch_info[0])
            except ValueError:
                continue
            batch_info = parts[1].split(':')[-1].strip().split('/')
            try:
                batch = int(batch_info[0])
            except ValueError:
                continue
            try:
                loss_dict = {kv.split(':')[0].strip(): float(kv.split(':')[1].strip()) for kv in parts[2:] if ':' in kv}
            except (IndexError, ValueError):  # Skip lines that don't match the expected format
                continue
            data.append({'epoch': epoch, 'batch': batch, **loss_dict})
    return pd.DataFrame(data)

# Parse the log files
train_df = parse_log_file(train_log_path)
val_df = parse_log_file(val_log_path)

# Display the dataframes
print("Training Loss Data")
print(train_df.head())

print("Validation Loss Data")
print(val_df.head())

# Check if validation DataFrame is empty
if not val_df.empty:
    plt.figure(figsize=(12, 6))
    plt.plot(train_df['epoch'], train_df['Loss'], label='Training Loss', color='blue')
    plt.plot(val_df['epoch'], val_df['Val loss total'], label='Validation Loss', color='red')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss Over Epochs')
    plt.legend()
    plt.grid(True)
    plt.show()
else:
    plt.figure(figsize=(12, 6))
    plt.plot(train_df['epoch'], train_df['Loss'], label='Training Loss', color='blue')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Loss Over Epochs')
    plt.legend()
    plt.grid(True)
    plt.show()
    print("Validation log file is empty or not in the expected format.")
