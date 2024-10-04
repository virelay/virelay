"""Contains some helper functions for processing images."""

import math
from typing import Literal, TypeAlias

import numpy
import numpy.typing
import matplotlib.cm
from PIL import Image
from numpy.typing import NDArray


BorderMethod: TypeAlias = Literal['fill_zeros', 'fill_ones', 'edge_repeat', 'mirror_edge', 'wrap_around']
"""Represents the different methods that can be used to create a border around an image."""


def add_border(
        image: NDArray[numpy.float64],
        new_width: int,
        new_height: int,
        method: BorderMethod) -> NDArray[numpy.float64]:
    """Up-samples the specified image, by making a border around the image.

    Args:
        image (NDArray[numpy.float64]): The image that is to be up-sampled.
        new_width (int): The new width to which the image is to be up-sampled.
        new_height (int): The new height to which the image is to be up-sampled.
        method (BorderMethod): The method that is to be used to create the border. Supported methods are 'fill_zeros' to fill up the border with
            zeros, 'fill_ones' to fill up the border with ones, 'edge_repeat' to repeat the values at the edge of the image, 'mirror_edge' to mirror
            the image at the edge, and 'wrap_around' to wrap the image around (e.g. the left edge is filled up with values from the right edge).

    Raises:
        ValueError: If the specified method is not supported, then a ValueError is raised.

    Returns:
        NDArray[numpy.float64]: Returns the up-sampled image.
    """

    width = image.shape[0]
    height = image.shape[1]
    horizontal_padding = max(0, new_width - width)
    vertical_padding = max(0, new_height - height)
    left_padding = math.ceil(float(horizontal_padding) / 2.0)
    right_padding = math.floor(float(horizontal_padding) / 2.0)
    top_padding = math.ceil(float(vertical_padding) / 2.0)
    bottom_padding = math.floor(float(vertical_padding) / 2.0)

    padding = ((left_padding, right_padding), (top_padding, bottom_padding), (0, 0))
    if method in ['fill_zeros', 'fill_ones']:
        return numpy.pad(image, padding, 'constant', constant_values=0 if method == 'fill_zeros' else 1)
    if method == 'edge_repeat':
        return numpy.pad(image, padding, 'edge')
    if method == 'mirror_edge':
        return numpy.pad(image, padding, 'reflect')
    if method == 'wrap_around':
        return numpy.pad(image, padding, 'wrap')

    raise ValueError(f'The specified method "{method}" is not supported.')


def center_crop(image: NDArray[numpy.float64], new_width: int, new_height: int) -> NDArray[numpy.float64]:
    """Crops the image evenly on all sides to the desired size.

    Args:
        image (NDArray[numpy.float64]): The image that is to be down-sampled.
        new_width (int): The new width to which the image is to be down-sampled.
        new_height (int): The new height to which the image is to be down-sampled.

    Returns:
        NDArray[numpy.float64]: Returns the center-cropped image.
    """

    width = image.shape[0]
    height = image.shape[1]
    horizontal_crop = max(0, width - new_width)
    vertical_crop = max(0, height - new_height)
    left_crop = math.ceil(horizontal_crop / 2)
    top_crop = math.ceil(vertical_crop / 2)

    return image[left_crop:new_width + left_crop, top_crop:new_height + top_crop]


def render_heatmap(attribution_data: NDArray[numpy.float64], color_map: str) -> NDArray[numpy.float64]:
    """Takes the raw attribution data and converts it so that the data can be visualized as a heatmap.

    Args:
        attribution_data (NDArray[numpy.float64]): The raw attribution data for which the heatmap is to be rendered.
        color_map (str): The name of color map that is to be used to render the heatmap.

    Raises:
        ValueError: If the specified color map is unknown, then a ValueError is raised.

    Returns:
        NDArray[numpy.float64]: Returns the heatmap image.
    """

    # Creates a dictionary, which maps the name of a custom color map to a method that produces the heatmap image using that color map
    custom_color_maps = {
        'gray-red': generate_heatmap_image_gray_red,
        'black-green': generate_heatmap_image_black_green,
        'black-fire-red': generate_heatmap_image_black_fire_red,
        'black-yellow': generate_heatmap_image_black_yellow
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

    # Checks the name of the color map and renders the heatmap image accordingly, if the color map is not supported, then an exception is raised
    if color_map in custom_color_maps:
        heatmap_image = custom_color_maps[color_map](attribution_data)
    elif color_map in matplotlib_color_maps:
        heatmap_image = generate_heatmap_image_using_matplotlib(attribution_data, matplotlib_color_maps[color_map])
    else:
        raise ValueError(f'The color map "{color_map}" is not supported.')
    heatmap_image *= 255.0
    heatmap_image = heatmap_image.astype(numpy.uint8)
    heatmap_image = heatmap_image.squeeze()
    return heatmap_image


def render_superimposed_heatmap(
        attribution_data: NDArray[numpy.float64],
        image_to_superimpose: NDArray[numpy.float64],
        color_map: str) -> NDArray[numpy.float64]:
    """Renders the heatmap an superimposes it onto the specified image.

    Args:
        attribution_data (NDArray[numpy.float64]): The raw attribution data for which the heatmap is to be rendered.
        image_to_superimpose (NDArray[numpy.float64]): An image onto which the image is to be superimposed.
        color_map (str): The name of color map that is to be used to render the heatmap.

    Returns:
        NDArray[numpy.float64]: Returns the heatmap image.
    """

    # Checks if the raw attribution has more than one channel, in that case the channels are summed up
    attribution_data = attribution_data.squeeze()
    image_to_superimpose = image_to_superimpose.squeeze()
    if len(attribution_data.shape) == 3 and attribution_data.shape[-1] > 1:
        attribution_data = numpy.sum(attribution_data, axis=2)

    # Renders the heatmap
    heatmap_array = render_heatmap(attribution_data, color_map)
    heatmap = Image.fromarray(heatmap_array, 'RGB')

    # Takes the attribution data, and normalizes it to the range [0, 1], this will be used as the alpha channel top superimpose the heatmap onto the
    # specified image, the positive and negative parts of the attribution data are considered separately, because otherwise the negative attributions
    # would show up less significantly than the positive attributions
    absolute_maximum_attribution_value = numpy.max(numpy.abs(attribution_data))
    positive_attributions_mask_array = numpy.maximum(attribution_data, 0)
    positive_attributions_mask_array = positive_attributions_mask_array / absolute_maximum_attribution_value * 0.9
    positive_attributions_mask = Image.fromarray((positive_attributions_mask_array * 255).astype(numpy.uint8), 'L')
    negative_attributions_mask_array = numpy.abs(numpy.minimum(attribution_data, 0))
    negative_attributions_mask_array = negative_attributions_mask_array / absolute_maximum_attribution_value * 0.9
    negative_attributions_mask = Image.fromarray((negative_attributions_mask_array * 255).astype(numpy.uint8), 'L')

    # Superimposes the positive and the negative attributions onto the specified image
    loaded_image_to_superimpose = Image.fromarray(image_to_superimpose.astype(numpy.uint8)).convert('LA').convert('RGB')
    heatmap = heatmap.resize(loaded_image_to_superimpose.size)
    positive_attributions_mask = positive_attributions_mask.resize(loaded_image_to_superimpose.size)
    negative_attributions_mask = negative_attributions_mask.resize(loaded_image_to_superimpose.size)

    superimposed_heatmap = Image.composite(heatmap, loaded_image_to_superimpose, positive_attributions_mask)
    superimposed_heatmap = Image.composite(heatmap, superimposed_heatmap, negative_attributions_mask)

    # Returns the rendered heatmap
    return numpy.array(superimposed_heatmap)


def generate_heatmap_image_using_matplotlib(attribution_data: NDArray[numpy.float64], color_map_name: str) -> NDArray[numpy.float64]:
    """Generates a heatmap from the specified attribution data using the color maps provided by Matplotlib.

    Args:
        attribution_data (NDArray[numpy.float64]): The raw attribution data for which the heatmap is to be rendered.
        color_map_name (str): The name of the color map that is used to produce the heatmap.

    Returns:
        NDArray[numpy.float64]: Returns the heatmap.
    """

    # Gets the color map specified by the name
    color_map = matplotlib.colormaps.get_cmap(color_map_name)

    # Brings the raw heatmap data into a value range of 0.0 and 1.0
    attribution_data = attribution_data / numpy.max(numpy.abs(attribution_data))
    attribution_data = (attribution_data + 1.0) / 2.0

    # Applies the color map to the raw heatmap
    heatmap_height, heatmap_width = attribution_data.shape
    heatmap: NDArray[numpy.float64] = color_map(attribution_data.flatten())
    heatmap = heatmap[:, 0:3].reshape([heatmap_height, heatmap_width, 3])

    # Returns the created heatmap image
    return heatmap


def generate_heatmap_image_gray_red(attribution_data: NDArray[numpy.float64]) -> NDArray[numpy.float64]:
    """Generates a heatmap with a gray background, where red tones are used to visualize positive relevance values and blue tones are used to
    visualize negative relevances.

    Args:
        attribution_data (NDArray[numpy.float64]): The raw attribution data for which the heatmap is to be rendered.

    Returns:
        NDArray[numpy.float64]: Returns the heatmap.
    """

    # Creates the floating point representation of a the base gray color that is used in the heatmap, and creates a new heatmap image, with that base
    # gray as the background color
    base_gray = 0.8
    heatmap = numpy.ones([attribution_data.shape[0], attribution_data.shape[1], 3]) * base_gray

    # Generates the actual heatmap image
    absolute_maximum = numpy.max(attribution_data)
    truncated_values = numpy.maximum(numpy.minimum(attribution_data / absolute_maximum, 1.0), -1.0)
    negatives = attribution_data < 0
    heatmap[negatives, 0] += truncated_values[negatives] * base_gray
    heatmap[negatives, 1] += truncated_values[negatives] * base_gray
    heatmap[negatives, 2] += -truncated_values[negatives] * (1 - base_gray)
    positives = attribution_data >= 0
    heatmap[positives, 0] += truncated_values[positives] * (1 - base_gray)
    heatmap[positives, 1] += -truncated_values[positives] * base_gray
    heatmap[positives, 2] += -truncated_values[positives] * base_gray

    # Returns the created heatmap image
    return heatmap


def generate_heatmap_image_black_green(attribution_data: NDArray[numpy.float64]) -> NDArray[numpy.float64]:
    """Generates a heatmap with a black background, where green tones are used to visualize positive relevance values and blue tones are used to
    visualize negative relevances.

    Args:
        attribution_data (NDArray[numpy.float64]): The raw attribution data for which the heatmap is to be rendered.

    Returns:
        NDArray[numpy.float64]: Returns the heatmap.
    """

    # Creates the heatmap image with all pixel values set to 0
    absolute_maximum = numpy.max(attribution_data)
    heatmap = numpy.zeros([attribution_data.shape[0], attribution_data.shape[1], 3])

    # Applies the heatmap to the negative relevances
    negatives = attribution_data < 0
    heatmap[negatives, 2] = -attribution_data[negatives] / absolute_maximum

    # Applies the heatmap to the positive relevances
    positives = attribution_data >= 0
    heatmap[positives, 1] = attribution_data[positives] / absolute_maximum

    # Returns the generated heatmap image
    return heatmap


def generate_heatmap_image_black_fire_red(attribution_data: NDArray[numpy.float64]) -> NDArray[numpy.float64]:
    """Generates a heatmap with a gray background, where red tones are used to visualize positive relevance values and blue tones are used to
    visualize negative relevances.

    Args:
        attribution_data (NDArray[numpy.float64]): The raw attribution data for which the heatmap is to be rendered.

    Returns:
        NDArray[numpy.float64]: Returns the heatmap.
    """

    # Prepares the raw heatmap
    attribution_data = attribution_data / numpy.max(numpy.abs(attribution_data))

    # Applies the heatmap to the positive relevances
    heatmap_red_positive = numpy.clip(attribution_data - 0.00, 0, 0.25) / 0.25
    heatmap_green_positive = numpy.clip(attribution_data - 0.25, 0, 0.25) / 0.25
    heatmap_blue_positive = numpy.clip(attribution_data - 0.50, 0, 0.50) / 0.50

    # Applies the heatmap to the negative relevances
    heatmap_red_negative = numpy.clip(-attribution_data - 0.50, 0, 0.50) / 0.50
    heatmap_green_negative = numpy.clip(-attribution_data - 0.25, 0, 0.25) / 0.25
    heatmap_blue_negative = numpy.clip(-attribution_data - 0.00, 0, 0.25) / 0.25

    # Combines the positive and negative relevances, concatenates the individual color channels back together, and returns the generated heatmap image
    return numpy.concatenate([
        (heatmap_red_positive + heatmap_red_negative)[..., None],
        (heatmap_green_positive + heatmap_green_negative)[..., None],
        (heatmap_blue_positive + heatmap_blue_negative)[..., None]
    ], axis=2)


def generate_heatmap_image_black_yellow(attribution_data: NDArray[numpy.float64]) -> NDArray[numpy.float64]:
    """Generates a heatmap with a black background, where yellow tones are used to visualize positive relevance values and blue tones are used to
    visualize negative relevances.

    Args:
        attribution_data (NDArray[numpy.float64]): The raw attribution data for which the heatmap is to be rendered.

    Returns:
        NDArray[numpy.float64]: Returns the heatmap.
    """

    # Creates the heatmap image with all pixel values set to 0
    absolute_maximum = numpy.max(attribution_data)
    heatmap = numpy.zeros([attribution_data.shape[0], attribution_data.shape[1], 3])

    # Applies the heatmap to the negative relevances
    negatives = attribution_data < 0
    heatmap[negatives, 2] = -attribution_data[negatives] / absolute_maximum

    # Applies the heatmap to the positive relevances
    positives = attribution_data >= 0
    heatmap[positives, 0] = attribution_data[positives] / absolute_maximum
    heatmap[positives, 1] = attribution_data[positives] / absolute_maximum

    # Returns the generated heatmap image
    return heatmap
