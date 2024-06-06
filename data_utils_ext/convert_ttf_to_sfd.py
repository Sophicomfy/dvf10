import fontforge  # noqa
import os
import multiprocessing as mp
import data_preprocess_options

def convert_mp(opts):
    """Using multiprocessing to convert all fonts to sfd files"""
    with open(opts.charset_path, 'r') as f:
        charset = [line.strip() for line in f if line.strip()]
    charset_lenw = len(str(len(charset)))
    fonts_file_path = opts.ttf_path
    sfd_path = opts.sfd_path
    for root, dirs, files in os.walk(fonts_file_path):
        ttf_fnames = files
    
    font_num = len(ttf_fnames)
    process_num = min(opts.workers, mp.cpu_count() - 1)
    font_num_per_process = font_num // process_num + 1

    def process(process_id, font_num_p_process):
        for i in range(process_id * font_num_p_process, (process_id + 1) * font_num_p_process):
            if i >= font_num:
                break
            
            font_id = ttf_fnames[i].split('.')[0]
            font_name = ttf_fnames[i]
            
            font_file_path = os.path.join(fonts_file_path, font_name)
            try:
                cur_font = fontforge.open(font_file_path)
            except Exception as e:
                print('Cannot open ', font_name)
                print(e)
                continue

            target_dir = os.path.join(sfd_path, "{}".format(font_id))
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            for char_id, char in enumerate(charset):
                char_description = open(os.path.join(target_dir, '{}_{num:0{width}}.txt'.format(font_id, num=char_id, width=charset_lenw)), 'w')

                # Default Unicode handling
                if not char.startswith('uni'):
                    char = 'uni' + char.encode("unicode_escape")[2:].decode("utf-8")
                
                try:
                    cur_font.selection.select(char)
                    cur_font.copy()

                    new_font_for_char = fontforge.font()
                    new_font_for_char.selection.select('A')
                    new_font_for_char.paste()
                    new_font_for_char.fontname = "{}_".format(font_id) + font_name

                    if opts.margin:
                        new_font_for_char['A'].left_side_bearing = opts.margin
                        new_font_for_char['A'].right_side_bearing = opts.margin

                    new_font_for_char.save(os.path.join(target_dir, '{}_{num:0{width}}.sfd'.format(font_id, num=char_id, width=charset_lenw)))

                    char_description.write(str(ord(char)) + '\n')
                    char_description.write(str(new_font_for_char['A'].width) + '\n')
                    char_description.write(str(new_font_for_char['A'].vwidth) + '\n')
                    char_description.write('{num:0{width}}'.format(num=char_id, width=charset_lenw) + '\n')
                    char_description.write('{}'.format(font_id))

                except Exception as e:
                    print(f'Error processing character {char}: {e}')
                
                char_description.close()

            cur_font.close()

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
