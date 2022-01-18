import cairo


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

    def get_color(self):
        output = []
        if self.mode.startswith('RGB'):
            output = [self.red, self.green, self.blue]
        elif self.mode.startswith('BGR'):
            output = [self.blue, self.green, self.red]
        else:
            TypeError(f'Mode {self.mode} not recognized')

        if self.alpha is not None:
            output.append(self.alpha)

        return output

    def change_mode(self, to_mode='RGBA'):
        if self.mode != to_mode and to_mode in ['RGBA', 'BGRA', 'RGB', 'BGR']:
            self.mode = to_mode


class GradientColor(Color):

    def __init__(self, pos, red, green, blue, alpha=None, inverted_color_space=True):
        self.pos = pos
        super().__init__(red, green, blue, alpha, inverted_color_space)

    def get_color(self):
        return [self.pos] + super().get_color()


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