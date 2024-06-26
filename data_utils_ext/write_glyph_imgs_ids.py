# write_glyph_imgs_ids.py

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import multiprocessing as mp
import data_preprocess_options
import charset_parser
import logging
from datetime import datetime

# Set up logging
log_dir = "../logs/write_glyph_imgs_ids"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_filename = os.path.join(log_dir, f"write_glyph_imgs_ids_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=log_filename, level=logging.INFO)

print("Current Working Directory:", os.getcwd())

def get_bbox(img):
    img = 255 - np.array(img)
    sum_x = np.sum(img, axis=0)
    sum_y = np.sum(img, axis=1)
    range_x = np.where(sum_x > 0)
    width = range_x[0][-1] - range_x[0][0]
    range_y = np.where(sum_y > 0)
    height = range_y[0][-1] - range_y[0][0]
    return width, height

def write_glyph_imgs_ids_mp(opts):
    charset = charset_parser.parse_charset(opts.charset_path, 'full')
    fonts_file_path = opts.ttf_path
    sfd_path = opts.sfd_path

    for root, dirs, files in os.walk(fonts_file_path):
        ttf_names = files
    ttf_names.sort()
    font_num = len(ttf_names)
    charset_lenw = len(str(len(charset)))
    process_nums = min(opts.workers, mp.cpu_count() - 1)
    font_num_per_process = font_num // process_nums + 1

    print(f"Fonts to process: {font_num}")
    logging.info(f"Fonts to process: {font_num}")

    processed_fonts = mp.Value('i', 0)

    def process(process_id, font_num_p_process):
        nonlocal processed_fonts
        worker_name = f"worker_{process_id}"
        start_index = process_id * font_num_p_process
        end_index = min((process_id + 1) * font_num_p_process, font_num)
        logging.info(f"{worker_name} assigned to process fonts from index {start_index} to {end_index - 1}")

        for i in range(start_index, end_index):
            if i >= font_num:
                break

            fontname = ttf_names[i].split('.')[0]
            ttf_file_path = os.path.join(fonts_file_path, ttf_names[i])
            logging.info(f"Processing {ttf_file_path} by worker {worker_name}")

            if not os.path.exists(os.path.join(sfd_path, fontname)):
                logging.info(f"Skipping {ttf_file_path} as corresponding directory does not exist")
                continue

            try:
                font = ImageFont.truetype(ttf_file_path, opts.img_size, encoding="unic")
            except Exception as e:
                logging.info(f"Can't open {ttf_file_path}. Error: {e}")
                continue

            fontimgs_array = np.zeros((len(charset), opts.img_size, opts.img_size), np.uint8)
            fontimgs_array[:, :, :] = 255

            flag_success = True

            for charid, char in enumerate(charset):
                txt_fpath = os.path.join(sfd_path, fontname, f"{fontname}_{char[1]}.txt")
                try:
                    txt_lines = open(txt_fpath, 'r').read().split('\n')
                except Exception as e:
                    logging.info(f"Cannot read text file: {txt_fpath} for charid: {charid} font: {fontname}. Error: {e}")
                    flag_success = False
                    break
                if len(txt_lines) < 5:
                    logging.info(f"File {txt_fpath} does not contain enough lines. Expected 5, got {len(txt_lines)}.")
                    flag_success = False
                    break

                try:
                    vbox_w = float(txt_lines[1])
                    vbox_h = float(txt_lines[2])
                    norm = max(int(vbox_w), int(vbox_h))
                except ValueError as ve:
                    logging.info(f"Error parsing dimensions in file {txt_fpath}: {ve}.")
                    flag_success = False
                    break

                if int(vbox_h) > int(vbox_w):
                    add_to_y = 0
                    add_to_x = abs(int(vbox_h) - int(vbox_w)) / 2
                    add_to_x = add_to_x * (float(opts.img_size) / norm)
                else:
                    add_to_y = abs(int(vbox_h) - int(vbox_w)) / 2
                    add_to_y = add_to_y * (float(opts.img_size) / norm)
                    add_to_x = 0

                array = np.ndarray((opts.img_size, opts.img_size), np.uint8)
                array[:, :] = 255
                image = Image.fromarray(array)
                draw = ImageDraw.Draw(image)
                try:
                    font_width, font_height = font.getsize(char[3])
                except Exception as e:
                    logging.info(f"Can't calculate height and width for charid {charid} in font {fontname}. Error: {e}")
                    flag_success = False
                    break

                try:
                    ascent, descent = font.getmetrics()
                except Exception as e:
                    logging.info(f"Cannot get ascent, descent for charid {charid} in font {fontname}. Error: {e}")
                    flag_success = False
                    break

                draw_pos_x = add_to_x + opts.margin
                draw_pos_y = add_to_y + opts.img_size - ascent - int((opts.img_size / 24.0) * (4.0 / 3.0)) + opts.margin

                draw.text((draw_pos_x, draw_pos_y), char[3], (0), font=font)

                if opts.debug:
                    image.save(os.path.join(sfd_path, fontname, f"{char[1]}_{opts.img_size}.png"))

                try:
                    char_w, char_h = get_bbox(image)
                except:
                    flag_success = False
                    break

                if (char_w < opts.img_size * 0.15) and (char_h < opts.img_size * 0.15):
                    flag_success = False
                    break

                fontimgs_array[charid] = np.array(image)

            if flag_success:
                npy_path = os.path.join(sfd_path, fontname, f"imgs_{opts.img_size}.npy")
                try:
                    np.save(npy_path, fontimgs_array)
                    print(f"Generated {npy_path} by {worker_name}")
                    logging.info(f"Generated {npy_path} by {worker_name}")
                except Exception as e:
                    print(f"Failed to generate {npy_path} by {worker_name}. Error: {e}")
                    logging.info(f"Failed to generate {npy_path} by {worker_name}. Error: {e}")
                with processed_fonts.get_lock():
                    processed_fonts.value += 1

        logging.info(f"{worker_name} completed processing. Fonts remaining: {font_num - processed_fonts.value}")

    processes = [mp.Process(target=process, args=(pid, font_num_per_process)) for pid in range(process_nums)]

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    print(f"Processed fonts: {font_num}/{processed_fonts.value}")
    logging.info(f"Processed fonts: {font_num}/{processed_fonts.value}")

def main():
    parser = data_preprocess_options.get_data_preprocess_options()
    opts = parser.parse_args()
    write_glyph_imgs_ids_mp(opts)

if __name__ == "__main__":
    main()
