import fontforge  # noqa
import os
import multiprocessing as mp
import data_preprocess_options
import charset_parser

def convert_mp(opts):
    charset = charset_parser.parse_charset(opts.charset_path, opts.char_type)
    charset_lenw = len(str(len(charset)))
    fonts_file_path = opts.ttf_path
    sfd_path = opts.sfd_path
    for root, dirs, files in os.walk(fonts_file_path):
        ttf_fnames = files
    
    font_num = len(ttf_fnames)
    print(f"Total fonts to be processed: {font_num}")
    process_num = min(opts.workers, mp.cpu_count() - 1)
    font_num_per_process = font_num // process_num + 1
    processed_fonts = mp.Value('i', 0)

    def process(process_id, font_num_p_process):
        nonlocal processed_fonts
        for i in range(process_id * font_num_p_process, (process_id + 1) * font_num_p_process):
            if i >= font_num:
                break
            
            font_id = ttf_fnames[i].split('.')[0]
            font_name = ttf_fnames[i]
            
            font_file_path = os.path.join(fonts_file_path, font_name)
            try:
                cur_font = fontforge.open(font_file_path)
            except Exception as e:
                print(f"Cannot open {font_name}")
                print(e)
                continue

            target_dir = os.path.join(sfd_path, "{}".format(font_id))
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            for char in charset:
                char_id = char[1]  # Use the second column as the Character ID
                char_description = open(os.path.join(target_dir, '{}_{}.txt'.format(font_id, char_id)), 'w')

                try:
                    unicode_char = char[0]
                    decimal_char = char[1]
                    glyph_name = char[2]

                    cur_font.selection.select(unicode_char)
                    cur_font.copy()

                    new_font_for_char = fontforge.font()
                    new_font_for_char.selection.select('A')
                    new_font_for_char.paste()
                    new_font_for_char.fontname = "{}_".format(font_id) + font_name

                    if opts.margin:
                        new_font_for_char['A'].left_side_bearing = opts.margin
                        new_font_for_char['A'].right_side_bearing = opts.margin

                    sfd_file_path = os.path.join(target_dir, '{}_{}.sfd'.format(font_id, char_id))
                    new_font_for_char.save(sfd_file_path)

                    # Set StartChar and Encoding
                    with open(sfd_file_path, 'r') as file:
                        sfd_content = file.read()
                    sfd_content = sfd_content.replace("StartChar: A", f"StartChar: {glyph_name}")
                    sfd_content = sfd_content.replace("Encoding: 65 65 0", f"Encoding: {decimal_char} {decimal_char} 0")
                    with open(sfd_file_path, 'w') as file:
                        file.write(sfd_content)

                    # Write to the char description file
                    char_description.write(f"{decimal_char}\n")
                    char_description.write(f"{new_font_for_char['A'].width}\n")
                    char_description.write(f"{new_font_for_char['A'].vwidth}\n")
                    char_description.write(f"{char_id}\n")
                    char_description.write(f"{font_id}")

                except Exception as e:
                    print(f"Error processing character {char}: {e}")

                char_description.close()

            cur_font.close()
            with processed_fonts.get_lock():
                processed_fonts.value += 1
                print(f"Progress: {processed_fonts.value}/{font_num} processed fonts")
            print(f"Processed font: {font_file_path} to {target_dir} by worker {process_id}")

    processes = [mp.Process(target=process, args=(pid, font_num_per_process)) for pid in range(process_num)]

    for p in processes:
        p.start()
    for p in processes:
        p.join()

def main():
    parser = data_preprocess_options.get_data_preprocess_options()
    opts = parser.parse_args()
    convert_mp(opts)

if __name__ == "__main__":
    main()
