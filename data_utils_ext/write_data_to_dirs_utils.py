import numpy as np

def exist_empty_imgs(imgs_array, num_chars):
    for char_id in range(num_chars):
        if np.max(imgs_array[char_id]) == 0:
            return True
    return False
