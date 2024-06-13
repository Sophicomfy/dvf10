import argparse
import multiprocessing as mp

def get_data_preprocess_options():
    parser = argparse.ArgumentParser(description="Data preprocessing options for font conversion scripts")
    parser.add_argument("--ttf_path", type=str, required=True, help='Path to TTF font files directory')
    parser.add_argument('--sfd_path', type=str, required=True, help='Path to save SFD font files')
    parser.add_argument('--charset_path', type=str, required=True, help='Path to charset.txt file')
    parser.add_argument('--output_path', type=str, required=True, help="Path to write the database to")  # Added argument
    parser.add_argument('--img_size', type=int, default=64, help='Image size for glyphs')
    parser.add_argument('--workers', type=int, default=mp.cpu_count() - 1, help='Number of worker processes to use')
    parser.add_argument('--margin', type=int, default=0, help='Margin for character bounding box')
    parser.add_argument('--phase', type=int, default=0, choices=[0, 1, 2], help='0 all, 1 create db, 2 cal stddev')  # Added argument
    parser.add_argument('--debug', type=bool, default=False, help='Enable debug mode')
    return parser

if __name__ == "__main__":
    options = get_data_preprocess_options().parse_args()
    print(options)
