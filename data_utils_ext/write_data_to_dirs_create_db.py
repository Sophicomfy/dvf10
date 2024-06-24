import os
import numpy as np
import multiprocessing as mp
import svg_utils
import charset_parser

def create_db(opts, output_path, log_path):
    charset = charset_parser.parse_charset(opts.charset_path, 'all')
    print("Process sfd to npy files in dirs....")
    sfd_path = opts.sfd_path
    all_font_ids = sorted(os.listdir(sfd_path))
    num_fonts = len(all_font_ids)
    num_fonts_w = len(str(num_fonts))
    print(f"Number of fonts before processing: {num_fonts}")
    num_processes = mp.cpu_count() - 2
    fonts_per_process = num_fonts // num_processes + 1
    num_chars = len(charset)
    num_chars_w = len(str(num_chars))

    def process(process_id):
        cur_process_log_file = open(os.path.join(log_path, f'log_{process_id}.txt'), 'w')
        for i in range(process_id * fonts_per_process, (process_id + 1) * fonts_per_process):
            if i >= num_fonts:
                break
            font_id = all_font_ids[i]
            cur_font_sfd_dir = os.path.join(sfd_path, font_id)
            cur_font_glyphs = []

            imgs_path = os.path.join(cur_font_sfd_dir, 'imgs_' + str(opts.img_size) + '.npy')
            print(f"Trying to read file: {imgs_path}")
            if not os.path.exists(imgs_path):
                print(f"File {imgs_path} not found")
                continue

            print(f"Processing {imgs_path} by worker_{process_id}")

            for char_id in range(num_chars):
                print(char_id)
                sfd_file = os.path.join(cur_font_sfd_dir, '{}_{num:0{width}}.sfd'.format(font_id, num=char_id, width=num_chars_w))
                if not os.path.exists(sfd_file):
                    print(f"File {sfd_file} not found")
                    break

                char_desp_f = open(os.path.join(cur_font_sfd_dir, '{}_{num:0{width}}.txt'.format(font_id, num=char_id, width=num_chars_w)), 'r')
                char_desp = char_desp_f.readlines()
                sfd_f = open(sfd_file, 'r')
                sfd = sfd_f.read()

                uni = int(char_desp[0].strip())
                width = int(char_desp[1].strip())
                vwidth = int(char_desp[2].strip())
                char_idx = char_desp[3].strip()
                font_idx = char_desp[4].strip()

                cur_glyph = {}
                cur_glyph['uni'] = uni
                cur_glyph['width'] = width
                cur_glyph['vwidth'] = vwidth
                cur_glyph['sfd'] = sfd
                cur_glyph['id'] = char_idx
                cur_glyph['binary_fp'] = font_idx

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
                rendered = np.load(imgs_path)

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
                    char_class.append(example['class'])  # char_name
                    binaryfp = example['binary_fp']
                if not os.path.exists(os.path.join(output_path, '{num:0{width}}'.format(num=i, width=num_fonts_w))):
                    os.mkdir(os.path.join(output_path, '{num:0{width}}'.format(num=i, width=num_fonts_w)))

                np.save(os.path.join(output_path, '{num:0{width}}'.format(num=i, width=num_fonts_w), 'sequence.npy'), np.array(sequence))
                np.save(os.path.join(output_path, '{num:0{width}}'.format(num=i, width=num_fonts_w), 'seq_len.npy'), np.array(seq_len))
                np.save(os.path.join(output_path, '{num:0{width}}'.format(num=i, width=num_fonts_w), 'class.npy'), np.array(char_class))
                np.save(os.path.join(output_path, '{num:0{width}}'.format(num=i, width=num_fonts_w), 'font_id.npy'), np.array(binaryfp))
                np.save(os.path.join(output_path, '{num:0{width}}'.format(num=i, width=num_fonts_w), 'rendered_' + str(opts.img_size) + '.npy'), rendered)

            print(f"Processed {imgs_path} by worker_{process_id}")

    processes = [mp.Process(target=process, args=[pid]) for pid in range(num_processes)]

    for p in processes:
        try:
            p.start()
        except Exception as e:
            print(f"Could not start process {p.name} due to: {e}")
    for p in processes:
        p.join()

    print("Finished processing all sfd files, logs (invalid glyphs and paths) are saved to", log_path)