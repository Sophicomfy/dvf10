import os
from write_data_to_dirs_create_db import create_db
from write_data_to_dirs_cal_mean_stddev import cal_mean_stddev
from data_preprocess_options import get_data_preprocess_options

def main():
    parser = get_data_preprocess_options()
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
