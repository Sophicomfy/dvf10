from datetime import datetime

def log_progress(process_id, processed_fonts, font_num, fontname, output_path):
    sequence_path = f"{output_path}/sequence.npy"
    seq_len_path = f"{output_path}/seq_len.npy"
    class_path = f"{output_path}/class.npy"
    font_id_path = f"{output_path}/font_id.npy"
    rendered_path = f"{output_path}/rendered_{fontname}.npy"

    print(f"[{datetime.now()}] Process {process_id} processed font {processed_fonts.value}/{font_num} — {fontname}")
    print(f"  {sequence_path}")
    print(f"  {seq_len_path}")
    print(f"  {class_path}")
    print(f"  {font_id_path}")
    print(f"  {rendered_path}")
