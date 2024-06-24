import os
import data_preprocess_options
from write_data_to_dirs_create_db import create_db
from write_data_to_dirs_cal_mean_stddev import cal_mean_stddev

def main():
    parser = data_preprocess_options.get_data_preprocess_options()
    opts = parser.parse_args()
    assert os.path.exists(opts.sfd_path), "specified sfd glyphs path does not exist"

    output_path = opts.output_path
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