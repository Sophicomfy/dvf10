import os
import numpy as np
import multiprocessing as mp
import svg_utils

def cal_mean_stddev(opts, output_path):
    print("Calculating all glyphs' mean stddev ....")
    charset = open(f"../data/char_set/{opts.language}.txt", 'r').read()
    font_paths = []
    for root, dirs, files in os.walk(output_path):
        for dir_name in dirs:
            font_paths.append(os.path.join(output_path, dir_name))
    font_paths.sort()
    num_fonts = len(font_paths)
    num_processes = mp.cpu_count() - 2
    fonts_per_process = num_fonts // num_processes + 1
    num_chars = len(charset)
    manager = mp.Manager()
    return_dict = manager.dict()
    main_stddev_accum = svg_utils.MeanStddev()

    def process(process_id, return_dict):
        mean_stddev_accum = svg_utils.MeanStddev()
        cur_sum_count = mean_stddev_accum.create_accumulator()
        for i in range(process_id * fonts_per_process, (process_id + 1) * fonts_per_process):
            if i >= num_fonts:
                break
            cur_font_path = font_paths[i]
            for charid in range(num_chars):
                cur_font_char = {}
                cur_font_char['seq_len'] = np.load(os.path.join(cur_font_path, 'seq_len.npy')).tolist()[charid]
                cur_font_char['sequence'] = np.load(os.path.join(cur_font_path, 'sequence.npy')).tolist()[charid]
                cur_sum_count = mean_stddev_accum.add_input(cur_sum_count, cur_font_char)
        return_dict[process_id] = cur_sum_count

    processes = [mp.Process(target=process, args=[pid, return_dict]) for pid in range(num_processes)]

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    merged_sum_count = main_stddev_accum.merge_accumulators(return_dict.values())
    output = main_stddev_accum.extract_output(merged_sum_count)
    mean = output['mean']
    stdev = output['stddev']
    mean = np.concatenate((np.zeros([4]), mean[4:]), axis=0)
    stdev = np.concatenate((np.ones([4]), stdev[4:]), axis=0)
    # finally, save the mean and stddev files
    output_path_ = os.path.join(opts.output_path, opts.language)
    np.save(os.path.join(output_path_, 'mean'), mean)
    np.save(os.path.join(output_path_, 'stdev'), stdev)

    # rename npy to npz, don't mind about it, just some legacy issue 
    os.rename(os.path.join(output_path_, 'mean.npy'), os.path.join(output_path_, 'mean.npz'))
    os.rename(os.path.join(output_path_, 'stdev.npy'), os.path.join(output_path_, 'stdev.npz'))
