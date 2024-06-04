import fontforge  # noqa
import os
import multiprocessing as mp
import argparse
import time
from datetime import datetime
import threading

# conda deactivate
# apt install python3-fontforge

def convert_mp(opts):
    """Using multiprocessing to convert all fonts to sfd files"""
    charset = open(f"../data/char_set/{opts.language}.txt", 'r').read()
    charset_lenw = len(str(len(charset)))
    fonts_file_path = os.path.join(opts.ttf_path, opts.language)
    sfd_path = os.path.join(opts.sfd_path, opts.language)
    for root, dirs, files in os.walk(os.path.join(fonts_file_path, opts.split)):
        ttf_fnames = files
    
    font_num = len(ttf_fnames)
    print(f"Total number of fonts to process: {font_num}")  # Print total number of fonts at the beginning
    process_num = min(opts.workers, mp.cpu_count() - 1)  # Adjust the number of workers
    font_num_per_process = font_num // process_num + 1

    processed_fonts = mp.Value('i', 0)  # Shared counter to track processed fonts
    task_queue = mp.Queue()
    assigned_fonts = mp.Manager().list()  # Track assigned fonts

    # Populate the task queue
    for i in range(font_num):
        task_queue.put(i)

    def process(process_id, font_num_p_process):
        while not task_queue.empty():
            try:
                i = task_queue.get(timeout=1)
                print(f"[{datetime.now()}] Process {process_id} assigned font {i} - {ttf_fnames[i]}")
                assigned_fonts.append(i)
            except queue.Empty:
                break

            font_id = ttf_fnames[i].split('.')[0]
            split = opts.split
            font_name = ttf_fnames[i]
            
            font_file_path = os.path.join(fonts_file_path, split, font_name)
            try:
                cur_font = fontforge.open(font_file_path)
                cur_font.encoding = "UnicodeFull"  # Set encoding to UnicodeFull
            except Exception as e:
                print('Cannot open ', font_name)
                print(e)
                continue

            target_dir = os.path.join(sfd_path, split, "{}".format(font_id))
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            for char_id, char in enumerate(charset):
                char_description = open(os.path.join(target_dir, '{}_{num:0{width}}.txt'.format(font_id, num=char_id, width=charset_lenw)), 'w')

                if opts.language == 'chn':
                    char = 'uni' + char.encode("unicode_escape")[2:].decode("utf-8")
                
                cur_font.selection.select(ord(char))
                cur_font.copy()

                new_font_for_char = fontforge.font()
                new_font_for_char.encoding = "UnicodeFull"  # Set encoding to UnicodeFull
                new_font_for_char.selection.select('A')
                new_font_for_char.paste()
                new_font_for_char.fontname = "{}_{}".format(font_id, font_name)

                new_font_for_char.save(os.path.join(target_dir, '{}_{num:0{width}}.sfd'.format(font_id, num=char_id, width=charset_lenw)))

                width_with_margin = new_font_for_char['A'].width + 2 * opts.margin
                vwidth_with_margin = new_font_for_char['A'].vwidth + 2 * opts.margin

                char_description.write(str(ord(char)) + '\n')
                char_description.write(str(width_with_margin) + '\n')
                char_description.write(str(vwidth_with_margin) + '\n')
                char_description.write('{num:0{width}}'.format(num=char_id, width=charset_lenw) + '\n')
                char_description.write('{}'.format(font_id))

                char_description.close()

            cur_font.close()
            with processed_fonts.get_lock():
                processed_fonts.value += 1

            print(f"[{datetime.now()}] Process {process_id} processed font {processed_fonts.value}/{font_num} - {font_name}")

    def monitor_processes(processes, task_queue, interval=10):
        while any(p.is_alive() for p in processes) or not task_queue.empty():
            remaining_fonts = task_queue.qsize()
            running_processes = []
            stopped_processes = []
            restarted_processes = []
            print(f"[{datetime.now()}] Checking running processes... Remaining fonts in queue: {remaining_fonts}")
            for i, p in enumerate(processes):
                if p.is_alive():
                    running_processes.append(i)
                else:
                    stopped_processes.append(i)
                    if not task_queue.empty():
                        processes[i] = mp.Process(target=process, args=(i, font_num_per_process))
                        processes[i].start()
                        restarted_processes.append(i)

            print(f"[{datetime.now()}] Processes report - Running: {running_processes}, Restarted: {restarted_processes}")

            time.sleep(interval)

        # Check for unprocessed fonts
        if processed_fonts.value < font_num:
            unprocessed_fonts = set(range(font_num)) - set(assigned_fonts)
            if unprocessed_fonts:
                print(f"[{datetime.now()}] Unprocessed fonts found: {unprocessed_fonts}")
                # Re-populate the task queue with unprocessed fonts
                for i in unprocessed_fonts:
                    task_queue.put(i)
                print(f"[{datetime.now()}] Re-populated task queue with unprocessed fonts.")
                # Restart processes to handle unprocessed fonts
                for i, p in enumerate(processes):
                    if not p.is_alive():
                        processes[i] = mp.Process(target=process, args=(i, font_num_per_process))
                        processes[i].start()
                        print(f"[{datetime.now()}] Restarted Process {i} to handle unprocessed fonts.")

    processes = [mp.Process(target=process, args=(pid, font_num_per_process)) for pid in range(process_num)]

    start_time = time.time()
    for p in processes:
        p.start()
    
    monitor_thread = threading.Thread(target=monitor_processes, args=(processes, task_queue))
    monitor_thread.start()

    for p in processes:
        p.join()
    monitor_thread.join()
    
    end_time = time.time()

    print(f"Total number of fonts processed: {processed_fonts.value}")  # Print total number of fonts processed
    print(f"Total processing time: {end_time - start_time:.2f} seconds")


def main():
    parser = argparse.ArgumentParser(description="Convert ttf fonts to sfd files")
    parser.add_argument("--language", type=str, default='eng', choices=['eng', 'chn'])
    parser.add_argument("--ttf_path", type=str, default='../data/font_ttfs')
    parser.add_argument('--sfd_path', type=str, default='../data/font_sfds')
    parser.add_argument('--split', type=str, default='train')
    parser.add_argument('--workers', type=int, default=mp.cpu_count() - 2, help='Number of worker processes to run')
    parser.add_argument('--margin', type=int, default=0, help='Margin to add to bounding box dimensions')
    opts = parser.parse_args()
    convert_mp(opts)

if __name__ == "__main__":
    main()
