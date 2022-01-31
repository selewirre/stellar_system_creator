import cairocffi as cairo


class Color:
    def __init__(self, red, green, blue, alpha=None, inverted_color_space=True):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

        if inverted_color_space:
            self.mode = 'BGR'
        else:
            self.mode = 'RGB'

        if self.alpha is not None:
            self.mode = self.mode + 'A'

    def get_color(self, mode=None):
        if mode is None:
            mode = self.mode
        output = []
        if mode.startswith('RGB'):
            output = [self.red, self.green, self.blue]
        elif mode.startswith('BGR'):
            output = [self.blue, self.green, self.red]
        else:
            TypeError(f'Mode {mode} not recognized')

        if self.alpha is not None:
            output.append(self.alpha)

        return output

    def change_mode(self, to_mode='RGBA'):
        if self.mode != to_mode and to_mode in ['RGBA', 'BGRA', 'RGB', 'BGR']:
            self.mode = to_mode

    def __repr__(self):
        return self.get_color().__repr__()


class GradientColor(Color):

    def __init__(self, pos, red, green, blue, alpha=None, inverted_color_space=True):
        self.pos = pos
        super().__init__(red, green, blue, alpha, inverted_color_space)

    def get_color(self, mode=None):
        return [self.pos] + super().get_color(mode)


def get_text_extents(text_extents):
    if cairo.__name__ == 'cairocffi':
        return CairocffiTextExtents(text_extents)
    else:
        return text_extents


class CairocffiTextExtents:
    def __init__(self, text_extents_tuple):
        self.x_bearing = text_extents_tuple[0]
        self.y_bearing = text_extents_tuple[1]
        self.width = text_extents_tuple[2]
        self.height = text_extents_tuple[3]
        self.x_advance = text_extents_tuple[4]
        self.y_advance = text_extents_tuple[5]

# class SVGSurface(cairo.Surface):
#
#     def __init__(self, fobj, width_in_points, height_in_points):
#         self = cairo.SVGSurface(fobj, width_in_points, height_in_points)
#         self._width = width_in_points
#         self._height = height_in_points
#
#     def get_width(self):
#         return self._width
#
#     def get_height(self):
#         return self._height