import io
import os
import pkgutil

import numpy as np
from PIL import Image


# stellar_body_marker_dict = {}
#
# folder = '../visualization/default_images'
# for filename in os.listdir(folder):
#     if filename.endswith('.png'):
#         image_array = np.array(Image.open(f"{folder}/{filename}"))
#
#         name = filename.split('.')[0]
#         stellar_body_marker_dict[name] = image_array


class StellarBodyMarkerDict:

    def __init__(self):
        super().__init__()
        self.folder = pkgutil.extend_path(['stellar_body_creator'], name='visualization')[1]
        self._dict = {}

    def __getitem__(self, item):
        if item not in self._dict:
            for filename in os.listdir(self.folder + '/default_images'):
                if filename.split('.')[0] == item:
                    image_packaged_data = pkgutil.get_data('visualization', f"default_images/{filename}")
                    image_array = np.array(Image.open(io.BytesIO(image_packaged_data)))
                    self._dict[item] = image_array
        return self._dict[item]


stellar_body_marker_dict = StellarBodyMarkerDict()

# a = stellar_body_marker_dict['patata']

kelvin_table = {
    3000: (255, 56, 0),
    3250: (255, 109, 0),
    3500: (255, 137, 18),
    3750: (255, 161, 72),
    4000: (255, 180, 107),
    4250: (255, 196, 137),
    4500: (255, 209, 163),
    4750: (255, 219, 186),
    5000: (255, 228, 206),
    5250: (255, 236, 224),
    5500: (255, 243, 239),
    5750: (255, 249, 253),
    6000: (245, 243, 255),
    6250: (235, 238, 255),
    6500: (227, 233, 255),
    7750: (220, 229, 255),
    8000: (214, 225, 255),
    8250: (208, 222, 255),
    8500: (204, 219, 255)}


def adjust_star_image_by_temp(image, temp):
    from PIL import Image
    new_image_rgba = image
    image_rgb = new_image_rgba[:, :, :3]

    kelvin_table_keys = np.array(list(kelvin_table.keys()))
    arg_closest_values = np.argpartition(np.abs(kelvin_table_keys - temp), 1)[0:2]
    closest_temps = kelvin_table_keys[arg_closest_values]
    r, g, b = (np.interp(temp, closest_temps,
                         [kelvin_table[ct][color_index] for ct in closest_temps])
               for color_index in range(3))

    matrix = (r*temp/2500 / 255.0, 0.0, 0.0, 0.0,
              0.0, g*temp/3500 / 255.0, 0.0, 0.0,
              0.0, 0.0, b*temp/1500 / 255.0, 0.0)
    new_image_rbg = np.array(Image.fromarray(image_rgb).convert('RGB', matrix))

    new_image_rgba[:, :, :3] = new_image_rbg
    return new_image_rgba


def load_user_image(filename):
    return np.array(Image.open(filename))
