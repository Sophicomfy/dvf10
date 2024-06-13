import argparse
import os
from write_data_to_dirs_create_db import create_db
from write_data_to_dirs_cal_mean_stddev import cal_mean_stddev

def main():
    parser = argparse.ArgumentParser(description="LMDB creation")
    parser.add_argument("--ttf_path", type=str, default='../data/font_ttfs')
    parser.add_argument('--sfd_path', type=str, default='../data/font_sfds')
    parser.add_argument("--output_path", type=str, default='../data/vecfont_dataset_/', help="Path to write the database to")
    parser.add_argument('--img_size', type=int, default=64, help="the height and width of glyph images")
    parser.add_argument("--charset_path", type=str, required=True, help="Path to charset.txt file")
    parser.add_argument("--phase", type=int, default=0, choices=[0, 1, 2], help="0 all, 1 create db, 2 cal stddev")

    opts = parser.parse_args()
    assert os.path.exists(opts.sfd_path), "specified sfd glyphs path does not exist"
    assert os.path.exists(opts.charset_path), "specified charset path does not exist"

    output_path = os.path.join(opts.output_path)
    log_path = os.path.join(opts.sfd_path, 'log')

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    if opts.phase <= 1:
        create_db(opts, output_path, log_path)

    if opts.phase <= 2:
        cal_mean_stddev(opts, output_path)

if __name__ == "__main__":
    main()
