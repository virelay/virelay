"""Bokeh plotting handler."""

import json
import logging
import random
from argparse import Namespace

import h5py
import numpy as np
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, CDSView, IndexFilter, DataTable, TableColumn, Range1d
from bokeh.transform import linear_cmap
from bokeh.plotting import figure
from bokeh.models.widgets import Select, Slider
from bokeh.palettes import d3 # pylint: disable=no-name-in-module

from .data import OrigImage, AttrImage

def modify_doc(doc, original_path, attribution_path, analysis_path, wordmap_path, wnid_path):
    """Handler for Bokeh server."""

    logger = logging.getLogger(__name__)
    logger.info('Setting up document...')

    # load all analysis category names
    with h5py.File(analysis_path, 'r') as analysis_file:
        categories = list(analysis_file)

    # load mapping from label number to wnid
    with open(wnid_path, 'r') as wnid_file:
        wnids = wnid_file.read().split('\n')[:-1]

    # load mapping from wnid to description
    with open(wordmap_path, 'r') as wordmap_file:
        words = json.load(wordmap_file)

    def map_wnid(wnid):
        return words.get(wnid, 'UNKNOWN')

    # loader for original input images
    original_loader = OrigImage(original_path)
    attribution_loader = AttrImage(attribution_path)

    # Namespace to store data references
    data = Namespace()
    data.sel = Namespace()
    data.sel.cat = categories[random.randint(0, len(categories))]
    data.sel.clu = None
    data.sel.vis = None

    # load data for a new category
    # pylint: disable=unused-argument
    def update_cat(attr, old, new):
        data.sel.cat = new

        # analysis data
        with h5py.File(analysis_path, 'r') as analysis_file:
            analysis_file = analysis_file[data.sel.cat]
            data.cluster = {key: val[:] for key, val in analysis_file['cluster'].items()}
            data.visualization = {key: val[:] for key, val in analysis_file['visualization'].items()}
            data.eigenvalue = analysis_file['eigenvalue'][:]
            data.index = analysis_file['index'][:]

        # reset selected values if necessary
        if data.sel.clu not in data.cluster:
            data.sel.clu = next(iter(data.cluster))
        if data.sel.vis not in data.visualization:
            data.sel.vis = next(iter(data.visualization))

        # attribution data
        indices = list(range(num))
        with h5py.File(attribution_path, 'r') as attribution_file:
            data.prediction = attribution_file['prediction'][data.index, :]

        # label descriptions for each sample prediction
        visual_desc = [map_wnid(wnids[label_id]) for label_id in data.prediction.argmax(1)]
        visual_x, visual_y = data.visualization[data.sel.vis].T
        visual_cluster = data.cluster[data.sel.clu]

        # update sample source with new category data
        sample_src.data.update({
            'i': range(len(visual_x)),
            'x': visual_x,
            'y': visual_y,
            'cluster': visual_cluster,
            'prediction': visual_desc
        })

        # unselect everything
        sample_src.selected.indices = []

        # decide which images to show in image_src
        image_src.data.update({
            'attribution': attribution_loader[data.index[indices]],
            'original': list(original_loader[data.index[indices]]),
            'x': (np.arange(len(indices), dtype=int) * width) % max_width,
            'y': (np.arange(len(indices), dtype=int) * width) // max_width * height,
        })

        # update eigenvalue plot
        eigen_value_src.data.update({
            'x': range(len(data.eigenvalue)),
            'y': data.eigenvalue[::-1],
        })

    # various plotting constants
    cmap = d3['Category20'][20]
    width, height = (224, 224)
    max_width = 4 * 224
    max_height = 4 * 224
    num = 16

    # initialize sources
    sample_src = ColumnDataSource({'i': [], 'x': [], 'y': [], 'cluster': [], 'prediction': []})
    image_src = ColumnDataSource({'attribution': [], 'original': [], 'x': [], 'y': []})
    eigen_value_src = ColumnDataSource({'x': [], 'y': []})

    update_cat(None, data.sel.cat, data.sel.cat)

    # === Eigenvalue Figure ===
    eigen_value_figure = figure(
        tools=[],
        plot_width=200,
        plot_height=800,
        min_border=1,
        min_border_left=1,
        toolbar_location="above",
        title="Eigenvalues"
    )

    # === Cluster Visualization Figure (e.g. TSNE) ===
    visual_fig = figure(
        tools="pan,wheel_zoom,box_select,lasso_select,reset",
        plot_width=600,
        plot_height=800,
        min_border=1,
        min_border_left=1,
        toolbar_location="above",
        x_axis_location=None,
        y_axis_location=None,
        title="Visualization",
        active_drag='box_select'
    )
    visual_cmap = linear_cmap('cluster', cmap, 0, len(cmap) - 1)
    visual_fig.scatter(
        'x',
        'y',
        source=sample_src,
        size=6,
        color=visual_cmap,
        nonselection_alpha=0.2,
        nonselection_color=visual_cmap
    )

    # === Table of selected Samples ===
    sample_columns = [
        TableColumn(field='cluster', title='cluster', width=50),
        TableColumn(field='prediction', title='prediction'),
    ]
    sample_table = DataTable(source=sample_src, columns=sample_columns, width=250, height=800)

    # === Figure containing original images and attributions ===
    image_fig = figure(
        tools=[],
        plot_width=800,
        plot_height=800,
        min_border=10,
        min_border_left=10,
        toolbar_location=None,
        x_axis_location=None,
        y_axis_location=None,
        title="Images",
        x_range=Range1d(start=0, end=max_width),
        y_range=Range1d(start=0, end=max_height)
    )
    attribution_rend = image_fig.image(
        'attribution',
        x='x',
        y='y',
        dw=width,
        dh=height,
        source=image_src,
        palette='Magma256',
        global_alpha=0.0
    )
    original_rend = image_fig.image_rgba(
        'original',
        x='x',
        y='y',
        dw=width,
        dh=height,
        source=image_src,
        global_alpha=1.0
    )

    # === Widgets ==
    category_select = Select(value=data.sel.cat, options=[(k, '{} ({})'.format(words[k], k)) for k in categories])
    cluster_select = Select(value=data.sel.clu, options=[k for k in data.cluster], width=200)
    alpha_slider = Slider(start=0.0, end=1.0, step=0.05, value=0.0, width=400, align='center')

    # === Document Layout ===
    top = row(category_select, cluster_select)
    bottom = row(eigen_value_figure, sample_table, visual_fig, column(image_fig, alpha_slider))
    layout = column(top, bottom)
    doc.add_root(layout)
    doc.title = "Sprincl TSNE"

    def update_selection(attr, old, new):
        sample_table.view = CDSView(source=sample_src, filters=[IndexFilter(new)])
        indices = sample_src.selected.indices[:num] if sample_src.selected.indices else list(range(num))
        indices = sorted(indices)
        image_src.data.update({
            'attribution': attribution_loader[data.index[indices]],
            'original': list(original_loader[data.index[indices]]),
            'x': (np.arange(len(indices), dtype=int) * width) % max_width,
            'y': (np.arange(len(indices), dtype=int) * width) // max_width * height,
        })

    # pylint: disable=unused-argument
    def update_clusters(attr, old, new):
        data.sel.clu = new
        sample_src.data.update({'cluster': data.cluster[data.sel.clu]})

    # pylint: disable=unused-argument
    def update_alpha(attr, old, new):
        original_rend.glyph.global_alpha = 1. - new
        attribution_rend.glyph.global_alpha = new

    # === Event Registration ===
    category_select.on_change('value', update_cat)
    cluster_select.on_change('value', update_clusters)
    alpha_slider.on_change('value', update_alpha)
    sample_src.selected.on_change('indices', update_selection) # pylint: disable=no-member
    logger.info('Ready for service.')
