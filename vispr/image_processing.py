"""Contains some helper functions for processing images."""

import math

import numpy
import matplotlib.cm
from PIL import Image


def add_border(image, new_width, new_height, method):
    """
    Up-samples the specified image, by making a border around the image.

    Parameters
    ----------
        image: numpy.ndarray
            The image that is to be up-sampled.
        new_width: int
            The new width to which the image is to be up-sampled.
        new_height: int
            The new height to which the image is to be up-sampled.
        method: str
            The method that is to be used to create the border. Supported methods are 'fill_zeros' to fill up the border
            with zeros, 'fill_ones' to fill up the border with ones, 'edge_repeat' to repeat the values at the edge of
            the image, 'mirror_edge' to mirror the image at the edge, and 'wrap_around' to wrap the image around (e.g.
            the left edge is filled up with values from the right edge).

    Raises
    ------
        ValueError
            If the specified method is not supported, then a ValueError is raised

    Returns
    -------
        numpy.ndarray
            Returns the up-sampled image.
    """

    if len(image.shape) == 2:
        width, height = image.shape
    else:
        width, height, _ = image.shape
    horizontal_padding = max(0, new_width - width)
    vertical_padding = max(0, new_height - height)
    left_padding = math.ceil(float(horizontal_padding) / 2.0)
    right_padding = math.floor(float(horizontal_padding) / 2.0)
    top_padding = math.ceil(float(vertical_padding) / 2.0)
    bottom_padding = math.floor(float(vertical_padding) / 2.0)

    if method in ['fill_zeros', 'fill_ones']:
        return numpy.pad(
            image,
            ((left_padding, right_padding), (top_padding, bottom_padding), (0, 0)),
            'constant',
            constant_values=0 if method == 'zeros' else 1
        )

    internal_methods_map = {
        'edge_repeat': 'edge',
        'mirror_edge': 'reflect',
        'wrap_around': 'wrap'
    }
    if method in internal_methods_map.keys():
        return numpy.pad(
            image,
            ((left_padding, right_padding), (top_padding, bottom_padding), (0, 0)),
            internal_methods_map[method]
        )

    raise ValueError('The specified method "{0}" is not supported.'.format(method))


def center_crop(image, new_width, new_height):
    """
    Crops the image evenly on all sides to the desired size.

    Parameters
    ----------
        image: numpy.ndarray
            The image that is to be down-sampled.
        new_width: int
            The new width to which the image is to be down-sampled.
        new_height: int
            The new height to which the image is to be down-sampled.
    """

    if len(image.shape) == 2:
        width, height = image.shape
    else:
        width, height, _ = image.shape
    horizontal_crop = max(0, width - new_width)
    vertical_crop = max(0, height - new_width)
    left_crop = math.ceil(float(horizontal_crop) / 2.0)
    right_crop = math.floor(float(horizontal_crop) / 2.0)
    top_crop = math.ceil(float(vertical_crop) / 2.0)
    bottom_crop = math.floor(float(vertical_crop) / 2.0)

    return image[left_crop:new_width + right_crop, top_crop:new_height + bottom_crop, :]


def render_heatmap(attribution_data, color_map):
    """
    Takes the raw attribution data and converts it so that the data can be visualized as a heatmap.

    Parameters
    ----------
        attribution_data: numpy.ndarray
            The raw attribution data for which the heatmap is to be rendered.
        color_map: str
            The name of color map that is to be used to render the heatmap.

    Raises
    ------
        ValueError
            If the specified color map is unknown, then a ValueError is raised.
    """

    # Creates a dictionary, which maps the name of a custom color map to a method that produces the heatmap image
    # using that color map
    custom_color_maps = {
        'gray-red': generate_heatmap_image_gray_red,
        'black-green': generate_heatmap_image_black_green,
        'black-fire-red': generate_heatmap_image_black_fire_red,
        'blue-black-yellow': generate_heatmap_image_black_yellow
    }

    # Creates a list of 'fall-back'-color-maps from matplotlib, which can also be used
    matplotlib_color_maps = {
        'blue-white-red': 'bwr',
        'afm-hot': 'afmhot',
        'jet': 'jet',
        'seismic': 'seismic'
    }

    # Checks if the raw attribution has more than one channel, in that case the channels are summed up
    if len(attribution_data.shape) == 3 and attribution_data.shape[-1] > 1:
        attribution_data = numpy.sum(attribution_data, axis=2)

    # Checks the name of the color map and renders the heatmap image accordingly, if the color map is not supported,
    # then an exception is raised
    if color_map in custom_color_maps:
        heatmap_image = custom_color_maps[color_map](attribution_data)
    elif color_map in matplotlib_color_maps:
        heatmap_image = generate_heatmap_image_using_matplotlib(attribution_data, matplotlib_color_maps[color_map])
    else:
        raise ValueError('The color map "{0}" is not supported.'.format(color_map))
    heatmap_image *= 255.0
    heatmap_image = heatmap_image.astype(numpy.uint8)
    return heatmap_image


def render_superimposed_heatmap(attribution_data, superimpose, color_map):
    """
    Renders the heatmap an superimposes it onto the specified image.

    Parameters
    ----------
        attribution_data: numpy.ndarray
            The raw attribution data for which the heatmap is to be rendered.
        superimpose: numpy.ndarray
            An image onto which the image is to be superimposed.
        color_map: str
            The name of color map that is to be used to render the heatmap.

    Raises
    ------
        ValueError
            If the specified color map is unknown, then a ValueError is raised.
    """

    # Checks if the raw attribution has more than one channel, in that case the channels are summed up
    attribution_data = attribution_data.squeeze()
    superimpose = superimpose.squeeze()
    if len(attribution_data.shape) == 3 and attribution_data.shape[-1] > 1:
        attribution_data = numpy.sum(attribution_data, axis=2)

    # Renders the heatmap
    heatmap = render_heatmap(attribution_data, color_map)
    heatmap = Image.fromarray(heatmap, 'RGB')

    # Takes the attribution data, and normalizes it to the range [0, 1], this will be used as the alpha channel top
    # superimpose the heatmap onto the specified image, the positive and negative parts of the attribution data are
    # considered separately, because otherwise the negative attributions would show up less significantly than the
    # positive attributions
    positive_attributions_mask = numpy.clip(attribution_data, 0, numpy.max(attribution_data))
    positive_attributions_mask = positive_attributions_mask / numpy.max(positive_attributions_mask) * 0.9
    positive_attributions_mask = Image.fromarray((positive_attributions_mask * 255).astype(numpy.uint8), 'L')
    negative_attributions_mask = numpy.clip(attribution_data * -1, 0, numpy.max(attribution_data * -1))
    negative_attributions_mask = negative_attributions_mask / numpy.max(negative_attributions_mask) * 0.9
    negative_attributions_mask = Image.fromarray((negative_attributions_mask * 255).astype(numpy.uint8), 'L')

    # Superimposes the positive and the negative attributions onto the specified image
    superimpose = Image.fromarray(superimpose.astype(numpy.uint8)).convert('LA').convert('RGB')
    heatmap = heatmap.resize(superimpose.size)
    positive_attributions_mask = positive_attributions_mask.resize(superimpose.size)
    negative_attributions_mask = negative_attributions_mask.resize(superimpose.size)

    superimposed_heatmap = Image.composite(heatmap, superimpose, positive_attributions_mask)
    superimposed_heatmap = Image.composite(heatmap, superimposed_heatmap, negative_attributions_mask)

    # Returns the rendered heatmap
    return superimposed_heatmap


def generate_heatmap_image_using_matplotlib(raw_heatmap, color_map_name):
    """
    Generates a heatmap image from the specified raw heatmap using the color maps provided by matplotlib.

    Parameters
    ----------
        raw_heatmap: numpy.ndarray
            The raw heatmap, which are to be converted into an image representation.
        color_map_name: str
            The name of the color map that is used to produce the image heatmap.

    Returns
    -------
        numpy.ndarray
            Returns an array that contains the RGB values of the resulting heatmap image.
    """

    # Gets the color map specified by the name
    color_map = getattr(matplotlib.cm, color_map_name)

    # Brings the raw heatmap data into a value range of 0.0 and 1.0
    raw_heatmap = raw_heatmap / numpy.max(numpy.abs(raw_heatmap))
    raw_heatmap = (raw_heatmap + 1.0) / 2.0

    # Applies the color map to the raw heatmap
    heatmap_height, heatmap_width = raw_heatmap.shape
    heatmap_image = color_map(raw_heatmap.flatten())
    heatmap_image = heatmap_image[:, 0:3].reshape([heatmap_height, heatmap_width, 3])

    # Returns the created heatmap image
    return heatmap_image


def generate_heatmap_image_gray_red(raw_heatmap):
    """
    Generates a heatmap with a gray background, where red tones are used to visualize positive relevance values and
    blue tones are used to visualize negative relevances.

    Parameters
    ----------
        raw_heatmap: numpy.ndarray
            The raw heatmap, which are to be converted into an image representation.

    Returns
    -------
        numpy.ndarray
            Returns an array that contains the RGB values of the resulting heatmap image.
    """

    # Creates the floating point representation of a the base gray color that is used in the heatmap, and creates a
    # new heatmap image, with that base gray as the background color
    basegray = 0.8
    heatmap_image = numpy.ones([raw_heatmap.shape[0], raw_heatmap.shape[1], 3]) * basegray

    # Generates the actual heatmap image
    absolute_maximum = numpy.max(raw_heatmap)
    truncated_values = numpy.maximum(numpy.minimum(raw_heatmap / absolute_maximum, 1.0), -1.0)
    negatives = raw_heatmap < 0
    heatmap_image[negatives, 0] += truncated_values[negatives] * basegray
    heatmap_image[negatives, 1] += truncated_values[negatives] * basegray
    heatmap_image[negatives, 2] += -truncated_values[negatives] * (1 - basegray)
    positives = raw_heatmap >= 0
    heatmap_image[positives, 0] += truncated_values[positives] * (1 - basegray)
    heatmap_image[positives, 1] += -truncated_values[positives] * basegray
    heatmap_image[positives, 2] += -truncated_values[positives] * basegray

    # Returns the created heatmap image
    return heatmap_image


def generate_heatmap_image_black_green(raw_heatmap):
    """
    Generates a heatmap with a black background, where green tones are used to visualize positive relevance values
    and blue tones are used to visualize negative relevances.

    Parameters
    ----------
        raw_heatmap: numpy.ndarray
            The raw heatmap, which are to be converted into an image representation.

    Returns
    -------
        numpy.ndarray
            Returns an array that contains the RGB values of the resulting heatmap image.
    """

    # Creates the heatmap image with all pixel values set to 0
    absolute_maximum = numpy.max(raw_heatmap)
    heatmap_image = numpy.zeros([raw_heatmap.shape[0], raw_heatmap.shape[1], 3])

    # Applies the heatmap to the negative relevances
    negatives = raw_heatmap < 0
    heatmap_image[negatives, 2] = -raw_heatmap[negatives] / absolute_maximum

    # Applies the heatmap to the positive relevances
    positives = raw_heatmap >= 0
    heatmap_image[positives, 1] = raw_heatmap[positives] / absolute_maximum

    # Returns the generated heatmap image
    return heatmap_image


def generate_heatmap_image_black_fire_red(raw_heatmap):
    """
    Generates a heatmap with a gray background, where red tones are used to visualize positive relevance values and
    blue tones are used to visualize negative relevances.

    Parameters
    ----------
        raw_heatmap: numpy.ndarray
            The raw heatmap, which are to be converted into an image representation.

    Returns
    -------
        numpy.ndarray
            Returns an array that contains the RGB values of the resulting heatmap image.
    """

    # Prepares the raw heatmap
    raw_heatmap = raw_heatmap / numpy.max(numpy.abs(raw_heatmap))

    # Applies the heatmap to the positive relevances
    heatmap_red_positive = numpy.clip(raw_heatmap - 0.00, 0, 0.25) / 0.25
    heatmap_green_positive = numpy.clip(raw_heatmap - 0.25, 0, 0.25) / 0.25
    heatmap_blue_positive = numpy.clip(raw_heatmap - 0.50, 0, 0.50) / 0.50

    # Applies the heatmap to the negative relevances
    heatmap_red_negative = numpy.clip(-raw_heatmap - 0.50, 0, 0.50) / 0.50
    heatmap_green_negative = numpy.clip(-raw_heatmap - 0.25, 0, 0.25) / 0.25
    heatmap_blue_negative = numpy.clip(-raw_heatmap - 0.00, 0, 0.25) / 0.25

    # Combines the positive and negative relevances, concatenates the individual color channels back together, and
    # returns the generated heatmap image
    return numpy.concatenate([
        (heatmap_red_positive + heatmap_red_negative)[..., None],
        (heatmap_green_positive + heatmap_green_negative)[..., None],
        (heatmap_blue_positive + heatmap_blue_negative)[..., None]
    ], axis=2)


def generate_heatmap_image_black_yellow(raw_heatmap):
    """
    Generates a heatmap with a black background, where yellow tones are used to visualize positive relevance values
    and blue tones are used to visualize negative relevances.

    Parameters
    ----------
        raw_heatmap: numpy.ndarray
            The raw heatmap, which are to be converted into an image representation.

    Returns
    -------
        numpy.ndarray
            Returns an array that contains the RGB values of the resulting heatmap image.
    """

    # Creates the heatmap image with all pixel values set to 0
    absolute_maximum = numpy.max(raw_heatmap)
    heatmap_image = numpy.zeros([raw_heatmap.shape[0], raw_heatmap.shape[1], 3])

    # Applies the heatmap to the negative relevances
    negatives = raw_heatmap < 0
    heatmap_image[negatives, 2] = -raw_heatmap[negatives] / absolute_maximum

    # Applies the heatmap to the positive relevances
    positives = raw_heatmap >= 0
    heatmap_image[positives, 0] = raw_heatmap[positives] / absolute_maximum
    heatmap_image[positives, 1] = raw_heatmap[positives] / absolute_maximum

    # Returns the generated heatmap image
    return heatmap_image
