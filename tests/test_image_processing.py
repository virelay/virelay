"""Contains the tests for the image processing helper functions of ViRelAy"""

import numpy
import pytest
from PIL import Image

from virelay.image_processing import (
    add_border,
    center_crop,
    render_heatmap,
    render_superimposed_heatmap,
    generate_heatmap_image_using_matplotlib,
    generate_heatmap_image_gray_red,
    generate_heatmap_image_black_green,
    generate_heatmap_image_black_fire_red,
    generate_heatmap_image_black_yellow
)


def test_add_border():
    """Tests the function for adding borders to images."""

    # Creates the image on which the tests are performed
    input_image = numpy.array(Image.new('RGB', (2, 2), color=(255, 255, 255)))

    # Validates that a ValueError is raised, when a method is specified that is not supported
    with pytest.raises(ValueError):
        add_border(input_image, 4, 4, 'unknown_method')

    # Validates that a border of zeros is properly added
    expected_image = numpy.pad(input_image, ((1, 1), (1, 1), (0, 0)), 'constant', constant_values=0)
    actual_image = add_border(input_image, 4, 4, 'fill_zeros')
    assert numpy.array_equal(expected_image, actual_image)
    expected_image = numpy.pad(input_image, ((2, 1), (2, 1), (0, 0)), 'constant', constant_values=0)
    actual_image = add_border(input_image, 5, 5, 'fill_zeros')
    assert numpy.array_equal(expected_image, actual_image)

    # Validates that a border of ones is properly added
    expected_image = numpy.pad(input_image, ((1, 1), (1, 1), (0, 0)), 'constant', constant_values=1)
    actual_image = add_border(input_image, 4, 4, 'fill_ones')
    assert numpy.array_equal(expected_image, actual_image)
    expected_image = numpy.pad(input_image, ((2, 1), (2, 1), (0, 0)), 'constant', constant_values=1)
    actual_image = add_border(input_image, 5, 5, 'fill_ones')
    assert numpy.array_equal(expected_image, actual_image)

    # Validates whether the border is the repetition of the edge
    expected_image = numpy.pad(input_image, ((1, 1), (1, 1), (0, 0)), 'edge')
    actual_image = add_border(input_image, 4, 4, 'edge_repeat')
    assert numpy.array_equal(expected_image, actual_image)
    expected_image = numpy.pad(input_image, ((2, 1), (2, 1), (0, 0)), 'edge')
    actual_image = add_border(input_image, 5, 5, 'edge_repeat')
    assert numpy.array_equal(expected_image, actual_image)

    # Validates whether the border is a mirroring of the edge
    expected_image = numpy.pad(input_image, ((1, 1), (1, 1), (0, 0)), 'reflect')
    actual_image = add_border(input_image, 4, 4, 'mirror_edge')
    assert numpy.array_equal(expected_image, actual_image)
    expected_image = numpy.pad(input_image, ((2, 1), (2, 1), (0, 0)), 'reflect')
    actual_image = add_border(input_image, 5, 5, 'mirror_edge')
    assert numpy.array_equal(expected_image, actual_image)

    # Validates whether the border is a wrapping around
    expected_image = numpy.pad(input_image, ((1, 1), (1, 1), (0, 0)), 'wrap')
    actual_image = add_border(input_image, 4, 4, 'wrap_around')
    assert numpy.array_equal(expected_image, actual_image)
    expected_image = numpy.pad(input_image, ((2, 1), (2, 1), (0, 0)), 'wrap')
    actual_image = add_border(input_image, 5, 5, 'wrap_around')
    assert numpy.array_equal(expected_image, actual_image)


def test_center_crop():
    """Tests the function for center cropping images."""

    # Creates the image on which the tests are performed
    input_image = numpy.array(Image.new('RGB', (6, 6), color=(255, 255, 255)))

    # Validates that the center crop works when the size is reduced by an even number of pixels
    expected_image = input_image[1:5, 1:5]
    actual_image = center_crop(input_image, 4, 4)
    assert numpy.array_equal(expected_image, actual_image)

    # Validates that the center crop works when the size is reduced by an odd number of pixels
    expected_image = input_image[2:5, 2:5]
    actual_image = center_crop(input_image, 3, 3)
    assert numpy.array_equal(expected_image, actual_image)

    # Validates that the image is not cropped at all, if the target size is greater than the original size
    expected_image = input_image
    actual_image = center_crop(input_image, 7, 7)
    assert numpy.array_equal(expected_image, actual_image)


def test_render_heatmap_unknown_color_map():
    """Tests the function for rendering heatmap images using an unknown color map."""

    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)
    with pytest.raises(ValueError):
        render_heatmap(attribution_data, 'unknown-color-map')


def test_render_heatmap_with_multiple_dimensions():
    """Tests the function for rendering heatmap images, where the attribution data has multiple channel dimensions."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.stack([numpy.linspace(-1.0, 1.0, 10).reshape(10, 1)] * 2, axis=2)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[  0,   0, 255]],
         [[ 56,  56, 255]],
         [[112, 112, 255]],
         [[170, 170, 255]],
         [[226, 226, 255]],
         [[255, 226, 226]],
         [[255, 170, 170]],
         [[255, 112, 112]],
         [[255,  56,  56]],
         [[255,   0,   0]]],
        dtype=numpy.uint8
    )
    actual_heatmap = render_heatmap(attribution_data, 'blue-white-red')
    assert numpy.array_equal(expected_heatmap, actual_heatmap)


def test_render_heatmap_blue_white_red():
    """Tests the function for rendering heatmap images using the blue-white-red color map."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[  0,   0, 255]],
         [[ 56,  56, 255]],
         [[112, 112, 255]],
         [[170, 170, 255]],
         [[226, 226, 255]],
         [[255, 226, 226]],
         [[255, 170, 170]],
         [[255, 112, 112]],
         [[255,  56,  56]],
         [[255,   0,   0]]],
        dtype=numpy.uint8
    )
    actual_heatmap = render_heatmap(attribution_data, 'blue-white-red')
    assert numpy.array_equal(expected_heatmap, actual_heatmap)


def test_render_heatmap_afm_hot():
    """Tests the function for rendering heatmap images using the afm-hot color map."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[  0,   0,   0]],
         [[ 56,   0,   0]],
         [[112,   0,   0]],
         [[170,  42,   0]],
         [[226,  98,   0]],
         [[255, 156,  29]],
         [[255, 212,  84]],
         [[255, 255, 143]],
         [[255, 255, 198]],
         [[255, 255, 255]]],
        dtype=numpy.uint8
    )
    actual_heatmap = render_heatmap(attribution_data, 'afm-hot')
    assert numpy.array_equal(expected_heatmap, actual_heatmap)


def test_render_heatmap_jet():
    """Tests the function for rendering heatmap images using the jet color map."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[  0,   0, 127]],
         [[  0,   0, 254]],
         [[  0,  96, 255]],
         [[  0, 212, 255]],
         [[ 76, 255, 170]],
         [[170, 255,  76]],
         [[255, 229,   0]],
         [[255, 122,   0]],
         [[254,  18,   0]],
         [[127,   0,   0]]],
        dtype=numpy.uint8
    )
    actual_heatmap = render_heatmap(attribution_data, 'jet')
    assert numpy.array_equal(expected_heatmap, actual_heatmap)


def test_render_heatmap_seismic():
    """Tests the function for rendering heatmap images using the seismic color map."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[  0,   0,  76]],
         [[  0,   0, 154]],
         [[  0,   0, 233]],
         [[ 85,  85, 255]],
         [[197, 197, 255]],
         [[255, 197, 197]],
         [[255,  85,  85]],
         [[239,   0,   0]],
         [[183,   0,   0]],
         [[127,   0,   0]]],
        dtype=numpy.uint8
    )
    actual_heatmap = render_heatmap(attribution_data, 'seismic')
    assert numpy.array_equal(expected_heatmap, actual_heatmap)


def test_render_heatmap_gray_red():
    """Tests the function for rendering heatmap images using the gray-red color map."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[  0,   0, 255]],
         [[ 45,  45, 243]],
         [[ 90,  90, 232]],
         [[136, 136, 221]],
         [[181, 181, 209]],
         [[209, 181, 181]],
         [[221, 136, 136]],
         [[232,  90,  90]],
         [[243,  45,  45]],
         [[255,   0,   0]]],
        dtype=numpy.uint8
    )
    actual_heatmap = render_heatmap(attribution_data, 'gray-red')
    assert numpy.array_equal(expected_heatmap, actual_heatmap)


def test_render_heatmap_black_green():
    """Tests the function for rendering heatmap images using the black-green color map."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[  0,   0, 255]],
         [[  0,   0, 198]],
         [[  0,   0, 141]],
         [[  0,   0,  85]],
         [[  0,   0,  28]],
         [[  0,  28,   0]],
         [[  0,  84,   0]],
         [[  0, 141,   0]],
         [[  0, 198,   0]],
         [[  0, 255,   0]]],
        dtype=numpy.uint8
    )
    actual_heatmap = render_heatmap(attribution_data, 'black-green')
    assert numpy.array_equal(expected_heatmap, actual_heatmap)


def test_render_heatmap_black_fire_red():
    """Tests the function for rendering heatmap images using the black-fire-red color map."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[255, 255, 255]],
         [[141, 255, 255]],
         [[ 28, 255, 255]],
         [[  0,  85, 255]],
         [[  0,   0, 113]],
         [[113,   0,   0]],
         [[255,  84,   0]],
         [[255, 255,  28]],
         [[255, 255, 141]],
         [[255, 255, 255]]],
        dtype=numpy.uint8
    )
    actual_heatmap = render_heatmap(attribution_data, 'black-fire-red')
    assert numpy.array_equal(expected_heatmap, actual_heatmap)


def test_render_heatmap_black_yellow():
    """Tests the function for rendering heatmap images using the black-yellow color map."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[  0,   0, 255]],
         [[  0,   0, 198]],
         [[  0,   0, 141]],
         [[  0,   0,  85]],
         [[  0,   0,  28]],
         [[ 28,  28,   0]],
         [[ 84,  84,   0]],
         [[141, 141,   0]],
         [[198, 198,   0]],
         [[255, 255,   0]]],
        dtype=numpy.uint8
    )
    actual_heatmap = render_heatmap(attribution_data, 'black-yellow')
    assert numpy.array_equal(expected_heatmap, actual_heatmap)


def test_render_superimposed_heatmap():
    """Tests the rendering of heatmap images that are then superimposed onto another image using the attribution data as
    alpha-channel."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1.0, 1.0, 10).reshape(5, 2)
    superimpose = numpy.ones((5, 2, 3))

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[  0,   0, 229],
          [ 39,  39, 178]],
         [[ 56,  56, 128],
          [ 51,  51,  77]],
         [[ 23,  23,  26],
          [ 26,  23,  23]],
         [[ 77,  51,  51],
          [128,  56,  56]],
         [[178,  39,  39],
          [229,   0,   0]]],
        dtype=numpy.uint8
    )
    actual_heatmap = render_superimposed_heatmap(attribution_data, superimpose, 'blue-white-red')
    assert numpy.array_equal(expected_heatmap, actual_heatmap)


def test_render_superimposed_heatmap_with_multiple_dimensions():
    """Tests the rendering of heatmap images that are then superimposed onto another image using the attribution data as
    alpha-channel, where the attribution data has multiple channel dimensions."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.stack([numpy.linspace(-1.0, 1.0, 10).reshape(5, 2)] * 2, axis=2)
    superimpose = numpy.ones((5, 2, 3))

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[  0,   0, 229],
          [ 39,  39, 178]],
         [[ 56,  56, 128],
          [ 51,  51,  77]],
         [[ 23,  23,  26],
          [ 26,  23,  23]],
         [[ 77,  51,  51],
          [128,  56,  56]],
         [[178,  39,  39],
          [229,   0,   0]]],
        dtype=numpy.uint8
    )
    actual_heatmap = render_superimposed_heatmap(attribution_data, superimpose, 'blue-white-red')
    assert numpy.array_equal(expected_heatmap, actual_heatmap)


def test_generate_heatmap_image_using_matplotlib_bwr():
    """Tests the function for generating heatmaps using the bwr color map of Matplotlib."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[0.0,        0.0,        1.0       ]],
         [[0.21960784, 0.21960784, 1.0       ]],
         [[0.43921569, 0.43921569, 1.0       ]],
         [[0.66666667, 0.66666667, 1.0       ]],
         [[0.88627451, 0.88627451, 1.0       ]],
         [[1.0,        0.88627451, 0.88627451]],
         [[1.0,        0.66666667, 0.66666667]],
         [[1.0,        0.43921569, 0.43921569]],
         [[1.0,        0.21960784, 0.21960784]],
         [[1.0,        0.0,        0.0       ]]]
    )
    actual_heatmap = generate_heatmap_image_using_matplotlib(attribution_data, 'bwr')
    assert numpy.allclose(expected_heatmap, actual_heatmap)


def test_generate_heatmap_image_using_matplotlib_afmhot():
    """Tests the function for generating heatmaps using the afmhot color map of Matplotlib."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[0.0,        0.0,        0.0       ]],
         [[0.21960784, 0.0,        0.0       ]],
         [[0.43921569, 0.0,        0.0       ]],
         [[0.66666667, 0.16666667, 0.0       ]],
         [[0.88627451, 0.38627451, 0.0       ]],
         [[1.0,        0.61372549, 0.11372549]],
         [[1.0,        0.83333333, 0.33333333]],
         [[1.0,        1.0,        0.56078431]],
         [[1.0,        1.0,        0.78039216]],
         [[1.0,        1.0,        1.0       ]]]
    )
    actual_heatmap = generate_heatmap_image_using_matplotlib(attribution_data, 'afmhot')
    assert numpy.allclose(expected_heatmap, actual_heatmap)


def test_generate_heatmap_image_using_matplotlib_jet():
    """Tests the function for generating heatmaps using the jet color map of Matplotlib."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[0.0,        0.0,        0.5       ]],
         [[0.0,        0.0,        0.99910873]],
         [[0.0,        0.37843137, 1.0       ]],
         [[0.0,        0.83333333, 1.0       ]],
         [[0.30044276, 1.0,        0.66729918]],
         [[0.66729918, 1.0,        0.30044276]],
         [[1.0,        0.90123457, 0.0       ]],
         [[1.0,        0.48002905, 0.0       ]],
         [[0.99910873, 0.07334786, 0.0       ]],
         [[0.5,        0.0,        0.0       ]]]
    )
    actual_heatmap = generate_heatmap_image_using_matplotlib(attribution_data, 'jet')
    assert numpy.allclose(expected_heatmap, actual_heatmap)


def test_generate_heatmap_image_using_matplotlib_seismic():
    """Tests the function for generating heatmaps using the seismic color map of Matplotlib."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[0.0,        0.0,        0.3       ]],
         [[0.0,        0.0,        0.60745098]],
         [[0.0,        0.0,        0.91490196]],
         [[0.33333333, 0.33333333, 1.0       ]],
         [[0.77254902, 0.77254902, 1.0       ]],
         [[1.0,        0.77254902, 0.77254902]],
         [[1.0,        0.33333333, 0.33333333]],
         [[0.93921569, 0.0,        0.0       ]],
         [[0.71960784, 0.0,        0.0       ]],
         [[0.5,        0.0,        0.0       ]]]
    )
    actual_heatmap = generate_heatmap_image_using_matplotlib(attribution_data, 'seismic')
    assert numpy.allclose(expected_heatmap, actual_heatmap)


def test_generate_heatmap_image_gray_red():
    """Tests the function for generating heatmaps using the gray-red color map."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[0.0,        0.0,        1.0       ]],
         [[0.17777778, 0.17777778, 0.95555556]],
         [[0.35555556, 0.35555556, 0.91111111]],
         [[0.53333333, 0.53333333, 0.86666667]],
         [[0.71111111, 0.71111111, 0.82222222]],
         [[0.82222222, 0.71111111, 0.71111111]],
         [[0.86666667, 0.53333333, 0.53333333]],
         [[0.91111111, 0.35555556, 0.35555556]],
         [[0.95555556, 0.17777778, 0.17777778]],
         [[1.0,        0.0,        0.0      ]]]
    )
    actual_heatmap = generate_heatmap_image_gray_red(attribution_data)
    assert numpy.allclose(expected_heatmap, actual_heatmap)


def test_generate_heatmap_image_black_green():
    """Tests the function for generating heatmaps using the black-green color map."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[0.0,        0.0,        1.0       ]],
         [[0.0,        0.0,        0.77777778]],
         [[0.0,        0.0,        0.55555556]],
         [[0.0,        0.0,        0.33333333]],
         [[0.0,        0.0,        0.11111111]],
         [[0.0,        0.11111111, 0.0       ]],
         [[0.0,        0.33333333, 0.0       ]],
         [[0.0,        0.55555556, 0.0       ]],
         [[0.0,        0.77777778, 0.0       ]],
         [[0.0,        1.0,        0.0       ]]]
    )
    actual_heatmap = generate_heatmap_image_black_green(attribution_data)
    assert numpy.allclose(expected_heatmap, actual_heatmap)


def test_generate_heatmap_image_black_fire_red():
    """Tests the function for generating heatmaps using the black-fire-red color map."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[1.0,        1.0,        1.0       ]],
         [[0.55555556, 1.0,        1.0       ]],
         [[0.11111111, 1.0,        1.0       ]],
         [[0.0,        0.33333333, 1.0       ]],
         [[0.0,        0.0,        0.44444444]],
         [[0.44444444, 0.0,        0.0       ]],
         [[1.0,        0.33333333, 0.0       ]],
         [[1.0,        1.0,        0.11111111]],
         [[1.0,        1.0,        0.55555556]],
         [[1.0,        1.0,        1.0       ]]]
    )
    actual_heatmap = generate_heatmap_image_black_fire_red(attribution_data)
    assert numpy.allclose(expected_heatmap, actual_heatmap)


def test_generate_heatmap_image_black_yellow():
    """Tests the function for generating heatmaps using the black-yellow color map."""

    # Creates the raw heatmap on which the tests are performed
    attribution_data = numpy.linspace(-1, 1, 10).reshape(10, 1)

    # Validates the colors assigned by the heatmap
    expected_heatmap = numpy.array(
        [[[0.0,        0.0,        1.0       ]],
         [[0.0,        0.0,        0.77777778]],
         [[0.0,        0.0,        0.55555556]],
         [[0.0,        0.0,        0.33333333]],
         [[0.0,        0.0,        0.11111111]],
         [[0.11111111, 0.11111111, 0.0       ]],
         [[0.33333333, 0.33333333, 0.0       ]],
         [[0.55555556, 0.55555556, 0.0       ]],
         [[0.77777778, 0.77777778, 0.0       ]],
         [[1.0,        1.0,        0.0       ]]]
    )
    actual_heatmap = generate_heatmap_image_black_yellow(attribution_data)
    assert numpy.allclose(expected_heatmap, actual_heatmap)
