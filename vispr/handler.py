import os
import json
import logging
from argparse import Namespace

import h5py
import numpy as np
from bokeh.layouts import row, column, gridplot
from bokeh.models import ColumnDataSource, CDSView, IndexFilter, DataTable, TableColumn, Range1d, LinearColorMapper
from bokeh.events import Reset
from bokeh.transform import linear_cmap
from bokeh.plotting import figure, curdoc
from bokeh.models.widgets import RadioButtonGroup, Select, Slider
from bokeh.palettes import brewer, d3

from .data import OrigImage, AttrImage

logger = logging.getLogger(__name__)

def modify_doc(doc, original_path, attribution_path, analysis_path, wordmap_path, wnid_path):
    logger.info('Setting up document...')

    # load all analysis category names
    with h5py.File(analysis_path, 'r') as fd:
        categories = list(fd)
    # load mapping from label number to wnid
    with open(wnid_path, 'r') as fp:
        wnids = fp.read().split('\n')[:-1]
    # load mapping from wnid to description
    with open(wordmap_path, 'r') as fd:
        words = json.load(fd)
    mapwnid = lambda x: words.get(x, 'UNKNOWN')

    # loader for original input images
    original_loader = OrigImage(original_path)
    attribution_loader = AttrImage(attribution_path)

    # Namespace to store data references
    data = Namespace()
    data.sel = Namespace()
    data.sel.cat = categories[0]
    data.sel.clu = None
    data.sel.vis = None

    # load data for a new category
    def update_cat(attr, old, new):
        data.sel.cat = new

        # analysis data
        with h5py.File(analysis_path, 'r') as fd:
            fd = fd[data.sel.cat]
            data.cluster = {key: val[:] for key, val in fd['cluster'].items() }
            data.visualization = {key: val[:] for key, val in fd['visualization'].items() }
            data.eigenvalue = fd['eigenvalue'][:]
            data.index = fd['index'][:]

        # reset selected values if necessary
        if data.sel.clu not in data.cluster:
            data.sel.clu = next(iter(data.cluster))
        if data.sel.vis not in data.visualization:
            data.sel.vis = next(iter(data.visualization))

        # attribution data
        inds = list(range(num))
        with h5py.File(attribution_path, 'r') as fd:
            data.prediction = fd['prediction'][data.index, :]

        # label descriptions for each sample prediction
        visual_desc = [mapwnid(wnids[label_id]) for label_id in data.prediction.argmax(1)]
        visual_x, visual_y = data.visualization[data.sel.vis].T
        visual_cluster = data.cluster[data.sel.clu]

        # update sample source with new category data
        sample_src.data.update({'i': range(len(visual_x)), 'x': visual_x, 'y': visual_y, 'cluster': visual_cluster,
                                'prediction': visual_desc})
        # unselect everything
        sample_src.selected.indices = []

        # decide which images to show in image_src
        image_src.data.update({
            'attribution': attribution_loader[data.index[inds]],
            'original'   : list(original_loader[data.index[inds]]),
            'x'          : (np.arange(len(inds), dtype=int)*wid)%maxwid,
            'y'          : (np.arange(len(inds), dtype=int)*wid)//maxwid*hei,
        })

        # update eigenvalue plot
        eigval_src.data.update({
            'x': range(len(data.eigenvalue)),
            'y': data.eigenvalue[::-1],
        })


    # various plotting constants
    cmap = d3['Category20'][20]
    #cmap = ['red', 'green', 'blue', 'orange', 'cyan', 'magenta', 'black', 'violet']

    wid, hei = (224, 224)
    maxwid = 4*224
    maxhei = 4*224
    num = 16

    # initialize sources
    sample_src = ColumnDataSource({'i': [], 'x': [], 'y': [], 'cluster': [], 'prediction': []})
    image_src = ColumnDataSource({'attribution': [], 'original': [], 'x': [], 'y': []})
    eigval_src = ColumnDataSource({'x': [], 'y': []})

    update_cat(None, data.sel.cat, data.sel.cat)

    TOOLS="pan,wheel_zoom,box_select,lasso_select,reset"

    # === Eigenvalue Figure ===
    eigval_fig  = figure(tools=[], plot_width=200, plot_height=800, min_border=1, min_border_left=1,
                        toolbar_location="above", title="Eigenvalues")
    eigval_rend = eigval_fig.scatter('x', 'y', source=eigval_src, size=4, color="#3A5785")

    # === Cluster Visualization Figure (e.g. TSNE) ===
    visual_fig  = figure(tools=TOOLS, plot_width=600, plot_height=800, min_border=1, min_border_left=1,
                        toolbar_location="above", x_axis_location=None, y_axis_location=None,
                        title="Visualization")
    visual_cmap = linear_cmap('cluster', cmap, 0, len(cmap) - 1)
    visual_rend = visual_fig.scatter('x', 'y', source=sample_src, size=6, color=visual_cmap,
                                    nonselection_alpha=0.2, nonselection_color=visual_cmap)

    # === Table of selected Samples ===
    sample_columns = [
        TableColumn(field='cluster', title='cluster', width=50),
        TableColumn(field='prediction', title='prediction'),
    ]
    sample_table = DataTable(source=sample_src, columns=sample_columns, width=250, height=800)

    # === Figure containing original images and attributions ===
    image_fig = figure(tools=[], plot_width=800, plot_height=800, min_border=10, min_border_left=10,
                       toolbar_location=None, x_axis_location=None, y_axis_location=None,
                       title="Images", x_range=Range1d(start=0, end=maxwid), y_range=Range1d(start=0, end=maxhei))
    attribution_rend = image_fig.image('attribution', x='x', y='y', dw=wid, dh=hei, source=image_src, palette='Magma256', global_alpha=0.0)
    original_rend    = image_fig.image_rgba('original', x='x', y='y', dw=wid, dh=hei, source=image_src, global_alpha=1.0)

    # === Widgets ==
    category_select = Select(value=data.sel.cat, options=[(k, '{} ({})'.format(words[k], k)) for k in categories])
    cluster_select  = Select(value=data.sel.clu, options=[k for k in data.cluster], width=200)
    alpha_slider = Slider(start=0.0, end=1.0, step=0.05, value=0.0, width=100)

    # === Document Layout ===
    top = row(category_select, cluster_select, alpha_slider)
    bottom = row(eigval_fig, sample_table, visual_fig, image_fig)
    layout = column(top, bottom)
    doc.add_root(layout)
    doc.title = "Sprincl TSNE"

    def update_selection(attr, old, new):
        sample_table.view = CDSView(source=sample_src, filters=[IndexFilter(new)])
        inds = sample_src.selected.indices[:num] if len(sample_src.selected.indices) else list(range(num))
        inds = sorted(inds)
        image_src.data.update({
            'attribution': attribution_loader[data.index[inds]],
            'original'  : list(original_loader[data.index[inds]]),
            'x'     : (np.arange(len(inds), dtype=int)*wid)%maxwid,
            'y'     : (np.arange(len(inds), dtype=int)*wid)//maxwid*hei,
        })

    def update_clusters(attr, old, new):
        data.sel.clu = new
        sample_src.data.update({'cluster': data.cluster[data.sel.clu]})

    def update_alpha(attr, old, new):
        original_rend.glyph.global_alpha=1.-new
        attribution_rend.glyph.global_alpha=new

    # === Event Registration ===
    category_select.on_change('value', update_cat)
    cluster_select.on_change('value', update_clusters)
    alpha_slider.on_change('value', update_alpha)
    sample_src.selected.on_change('indices', update_selection)

    logger.info('Ready for service.')

