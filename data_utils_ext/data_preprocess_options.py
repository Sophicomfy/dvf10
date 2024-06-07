import argparse
import multiprocessing as mp

def get_data_preprocess_options():
    parser = argparse.ArgumentParser(description="Data preprocessing options for font conversion scripts")
    parser.add_argument("--ttf_path", type=str, required=True, help='Path to TTF font files directory')
    parser.add_argument('--sfd_path', type=str, required=True, help='Path to save SFD font files')
    parser.add_argument('--charset_path', type=str, required=True, help='Path to charset.txt file')
    parser.add_argument('--workers', type=int, default=mp.cpu_count() - 1, help='Number of worker processes to use')
    parser.add_argument('--margin', type=int, default=0, help='Margin for character bounding box')
    parser.add_argument('--img_size', type=int, default=64, help='Image size for glyphs')  # Added argument
    parser.add_argument('--debug', type=bool, default=False, help='Enable debug mode')  # Added argument
    return parser

if __name__ == "__main__":
    options = get_data_preprocess_options().parse_args()
    print(options)
