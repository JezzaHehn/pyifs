from array import array
from math import log10
from numpy import zeros
import struct
import zlib


# how much each channel contributes to luminance
RGB_LUMINANCE = (0.2126, 0.7152, 0.0722)

DISPLAY_LUMINANCE_MAX = 200.0

# formula from Ward "A Contrast-Based Scalefactor for Luminance Display"
SCALEFACTOR_NUMERATOR = 1.219 + (DISPLAY_LUMINANCE_MAX * 0.25) ** 0.4


GAMMA_ENCODE = 0.45


class Image(object):

    def __init__(self, width, height, iterations):
        """
        initialize blank image.
        """
        self.width = width
        self.height = height
        self.iterations = iterations
        self.data = array("d", [0]) * (width * height * 3)

    def _index(self, t):
        x, y, channel = t
        index = (x + ((self.height - 1 - y) * self.width)) * 3 + channel

        return index % len(self.data)

    def __getitem__(self, t):
        return self.data[self._index(t)]

    def __setitem__(self, t, val):
        self.data[self._index(t)] = val

    def add_radiance(self, x, y, radiance):
        """
        add radiance (an RGB tuple) to given x, y position on image.
        """
        self[x, y, 0] += radiance[0]
        self[x, y, 1] += radiance[1]
        self[x, y, 2] += radiance[2]

    def calculate_scalefactor(self):
        """
        calculate the linear tone-mapping scalefactor for this image
        """
        ## calculate the log-mean luminance of the image

        sum_of_logs = 0.0

        for x in range(self.width):
            for y in range(self.height):
                lum = self[x, y, 0] * RGB_LUMINANCE[0]
                lum += self[x, y, 1] * RGB_LUMINANCE[1]
                lum += self[x, y, 2] * RGB_LUMINANCE[2]
                lum /= self.iterations

                sum_of_logs += log10(max(lum, 0.0001))

        log_mean_luminance = 10.0 ** (sum_of_logs / (self.height * self.width))

        ## calculate the scalefactor for linear tone-mapping

        # formula from Ward "A Contrast-Based Scalefactor for Luminance Display"

        scalefactor = (
            (SCALEFACTOR_NUMERATOR / (1.219 + log_mean_luminance ** 0.4)) ** 2.5
        ) / DISPLAY_LUMINANCE_MAX

        return scalefactor

    def display_pixels(self):
        """
        iterate over each channel of each pixel in image returning
        gamma-corrected number scaled 0 - 1 (although not clipped to 1).
        """
        scalefactor = self.calculate_scalefactor()

        for value in self.data:
            yield max(value * scalefactor / self.iterations, 0) ** GAMMA_ENCODE

    def black_ratio(self):
        """
        ratio of total pixel count to black pixels, used for quality check
        """
        return len(self.data) / float(len([i for i in self.data if i < 10]))

    def colour_ratio(self):
        """
        ratio of unique values to total value count, used for quality check
        """
        return float(len(set([int(i) for i in self.data]))) / len(self.data)

    def interest_factor(self):
        """
        combination of factors to check for potential visual appeal
        """
        return self.black_ratio() * self.colour_ratio()**0.5 * 10e2

    def save(self, filename):
        """
        save the image to given filename using zlib's compressor
        """
        with open(filename, "wb") as f:
            f.write(bytes(struct.pack("8B", 137, 80, 78, 71, 13, 10, 26, 10)))
            output_chunk(f, "IHDR".encode("utf-8"), struct.pack("!2I5B", self.width, self.height, 8, 2, 0, 0, 0))
            compressor = zlib.compressobj()
            data = array("B")
            pixels = self.display_pixels()
            for y in range(self.height):
                data.append(0)
                for x in range(self.width):
                    for channel in range(3):
                        data.append(min(255, max(0, int(pixels.__next__() * 255.0 + 0.5))))
            compressed = compressor.compress(data.tostring())
            flushed = compressor.flush()
            output_chunk(f, "IDAT".encode("utf-8"), compressed + flushed)
            output_chunk(f, "IEND".encode("utf-8"), "".encode("utf-8"))

def output_chunk(f, chunk_type, data):
    """
    give chunks of packed image data for saving to file
    """
    f.write(struct.pack("!I", len(data)))
    f.write(chunk_type)
    f.write(data)
    checksum = zlib.crc32(data, zlib.crc32(chunk_type))
    f.write(struct.pack("!I", checksum))
