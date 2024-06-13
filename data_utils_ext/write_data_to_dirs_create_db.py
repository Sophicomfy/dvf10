import os
import numpy as np
import multiprocessing as mp
import svg_utils
from write_data_to_dirs_utils import exist_empty_imgs
from write_data_to_dirs_log import log_progress

def create_db(opts, output_path, log_path):
    charset = open(opts.charset_path, 'r', encoding="utf-8").read()
    print("Process sfd to npy files in dirs....")
    sdf_path = opts.sfd_path
    all_font_ids = sorted(os.listdir(sdf_path))
    num_fonts = len(all_font_ids)
    num_fonts_w = len(str(num_fonts))
    print(f"Number of fonts before processing", num_fonts)
    num_processes = mp.cpu_count() - 2
    fonts_per_process = num_fonts // num_processes + 1
    num_chars = len(charset)
    num_chars_w = len(str(num_chars))
    processed_fonts = mp.Value('i', 0)  # Shared variable to count processed fonts

    def process(process_id):
        cur_process_log_file = open(os.path.join(log_path, f'log_{process_id}.txt'), 'w')
        for i in range(process_id * fonts_per_process, (process_id + 1) * fonts_per_process):
            if i >= num_fonts:
                break
            font_id = all_font_ids[i]
            cur_font_sfd_dir = os.path.join(sdf_path, font_id)
            cur_font_glyphs = []

            if not os.path.exists(os.path.join(cur_font_sfd_dir, 'imgs_' + str(opts.img_size) + '.npy')):
                continue

            for char_id in range(num_chars):
                print(char_id)
                if not os.path.exists(os.path.join(cur_font_sfd_dir, '{}_{num:0{width}}.sfd'.format(font_id, num=char_id, width=num_chars_w))):
                    break

                char_desp_f = open(os.path.join(cur_font_sfd_dir, '{}_{num:0{width}}.txt'.format(font_id, num=char_id, width=num_chars_w)), 'r')
                char_desp = char_desp_f.readlines()
                sfd_f = open(os.path.join(cur_font_sfd_dir, '{}_{num:0{width}}.sfd'.format(font_id, num=char_id, width=num_chars_w)), 'r')
                sfd = sfd_f.read()

                uni = int(char_desp[0].strip())
                width = int(char_desp[1].strip())
                vwidth = int(char_desp[2].strip())
                char_idx = char_desp[3].strip()
                font_idx = char_desp[4].strip()

                cur_glyph = {
                    'uni': uni,
                    'width': width,
                    'vwidth': vwidth,
                    'sfd': sfd,
                    'id': char_idx,
                    'binary_fp': font_idx
                }

                if not svg_utils.is_valid_glyph(cur_glyph):
                    msg = f"font {font_idx}, char {char_idx} is not a valid glyph\n"
                    cur_process_log_file.write(msg)
                    char_desp_f.close()
                    sfd_f.close()
                    break

                pathunibfp = svg_utils.convert_to_path(cur_glyph)

                if not svg_utils.is_valid_path(pathunibfp):
                    msg = f"font {font_idx}, char {char_idx}'s sfd is not a valid path\n"
                    cur_process_log_file.write(msg)
                    char_desp_f.close()
                    sfd_f.close()
                    break

                example = svg_utils.create_example(pathunibfp)
                cur_font_glyphs.append(example)
                char_desp_f.close()
                sfd_f.close()

            if len(cur_font_glyphs) == num_chars:
                rendered = np.load(os.path.join(cur_font_sfd_dir, 'imgs_' + str(opts.img_size) + '.npy'))

                if (rendered[0] == rendered[1]).all() == True:
                    continue

                sequence = []
                seq_len = []
                binaryfp = []
                char_class = []
                for char_id in range(num_chars):
                    example = cur_font_glyphs[char_id]
                    sequence.append(example['sequence'])
                    seq_len.append(example['seq_len'])
                    char_class.append(example['class'])
                    binaryfp = example['binary_fp']
                font_dir = os.path.join(output_path, '{num:0{width}}'.format(num=i, width=num_fonts_w))
                if not os.path.exists(font_dir):
                    os.mkdir(font_dir)

                np.save(os.path.join(font_dir, 'sequence.npy'), np.array(sequence))
                np.save(os.path.join(font_dir, 'seq_len.npy'), np.array(seq_len))
                np.save(os.path.join(font_dir, 'class.npy'), np.array(char_class))
                np.save(os.path.join(font_dir, 'font_id.npy'), np.array(binaryfp))
                np.save(os.path.join(font_dir, 'rendered_' + str(opts.img_size) + '.npy'), rendered)

                with processed_fonts.get_lock():
                    processed_fonts.value += 1

                log_progress(process_id, processed_fonts, num_fonts, font_id, font_dir)

    while processed_fonts.value < num_fonts:
        processes = [mp.Process(target=process, args=[pid]) for pid in range(num_processes)]
        for p in processes:
            p.start()
        for p in processes:
            p.join()

    print("Finished processing all sfd files, logs (invalid glyphs and paths) are saved to", log_path)
