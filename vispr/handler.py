import os
import json

import numpy as np

from argparse import Namespace

from bokeh.layouts import row, column, gridplot
from bokeh.models import ColumnDataSource, CDSView, IndexFilter, DataTable, TableColumn, Range1d, LinearColorMapper
from bokeh.events import Reset
from bokeh.transform import linear_cmap
from bokeh.plotting import figure, curdoc
from bokeh.models.widgets import RadioButtonGroup, Select, Slider
from bokeh.palettes import brewer, d3

from .data import center_crop, get_attrib, get_clu, get_ew, get_tsne, OrigImage

def modify_doc(doc, inpath, atpath, anpath, wordmap):
    cats = [fname[:-7] for fname in os.listdir(anpath) if fname[-7:] == '.clu.h5']
    with open(wordmap, 'r') as fd:
        words = json.load(fd)

    data = Namespace()
    data.cat = cats[0]
    data.lab = 0

    def update_cat(attr, old, new):
        data.kcluster, data.label = get_clu(anpath, new)
        tsne = get_tsne(anpath, new)
        x, y = tsne.T
        ew = get_ew(anpath, new)
        data.orig = OrigImage(inpath, new)
        data.attrib, pred = get_attrib(atpath, new)
        source.data.update({'i': range(len(x)), 'x': x, 'y': y, 'label': data.label[data.lab],
                            'pred': cats.index(new) == pred})
        inds = source.selected.indices[:num] if len(source.selected.indices) else list(range(num))
        imattrib = list(data.attrib[inds])
        imorig = list(data.orig[inds])
        imsource.data.update({
            'attrib': imattrib,
            'orig': imorig,
            'x': (np.arange(len(inds), dtype=int)*wid)%maxwid,
            'y': (np.arange(len(inds), dtype=int)*wid)//maxwid*hei,
        })
        ewsource.data.update({
            'x': range(len(ew)),
            'y': ew[::-1],
        })
        data.cat = new
        source.selected.indices = []

    #cmap = ['red', 'green', 'blue', 'orange', 'cyan', 'magenta', 'black', 'violet']
    cmap = d3['Category20'][12]
    wid, hei = (224, 224)
    maxwid = 4*224
    maxhei = 4*224
    num = 16

    source = ColumnDataSource({'i': [], 'x': [], 'y': [], 'label': [], 'pred': []})
    imsource = ColumnDataSource({'attrib': [], 'orig': [], 'x': [], 'y': []})
    ewsource = ColumnDataSource({'x': [], 'y': []})

    update_cat(None, data.cat, data.cat)

    TOOLS="pan,wheel_zoom,box_select,lasso_select,reset"

    fbcol = "#3A5785"
    ewp = figure(tools=[], plot_width=200, plot_height=800, min_border=1, min_border_left=1,
                 toolbar_location="above", title="Eigenvalues")
    r = ewp.scatter('x', 'y', source=ewsource, size=4, color=fbcol)

    # create the scatter plot
    p = figure(tools=TOOLS, plot_width=600, plot_height=800, min_border=1, min_border_left=1,
               toolbar_location="above", x_axis_location=None, y_axis_location=None,
               title="TSNE")

    col = linear_cmap('label', cmap, 0, len(cmap) - 1)
    r = p.scatter('x', 'y', source=source, size=6, color=col,
                  nonselection_alpha=0.2, nonselection_color=col)

    columns = [
        TableColumn(field='label', title='label'),
        #TableColumn(field='pred', title='pred'),
    ]
    stats = DataTable(source=source, columns=columns, width=150, height=800)

    pi = figure(tools=[], plot_width=800, plot_height=800, min_border=10, min_border_left=10,
                toolbar_location=None, x_axis_location=None, y_axis_location=None,
                title="Images", x_range=Range1d(start=0, end=maxwid), y_range=Range1d(start=0, end=maxhei))

    imattr = pi.image('attrib', x='x', y='y', dw=wid, dh=hei, source=imsource, palette='Magma256', global_alpha=0.0)
    imorig = pi.image_rgba('orig', x='x', y='y', dw=wid, dh=hei, source=imsource, global_alpha=1.0)

    select = Select(value=data.cat, options=[(k, '%s (%s)'%(words[k], k)) for k in cats])
    radio = RadioButtonGroup(labels=["%d"%i for i in data.kcluster], active=data.lab, width=400)
    slider = Slider(start=0.0, end=1.0, step=0.05, value=0.0, width=100)

    top = row(select, radio, slider)
    bottom = row(ewp, stats, p, pi)
    layout = column(top, bottom)

    doc.add_root(layout)
    doc.title = "Sprincl TSNE"

    empty = np.zeros_like(data.attrib[0])

    def update_selection(attr, old, new):
        stats.view = CDSView(source=source, filters=[IndexFilter(new)])
        inds = source.selected.indices[:num] if len(source.selected.indices) else list(range(num))
        imattrib = list(data.attrib[inds])
        imorig = list(data.orig[inds])
        imsource.data.update({
            'attrib': imattrib,
            'orig': imorig,
            'x': (np.arange(len(inds), dtype=int)*wid)%maxwid,
            'y': (np.arange(len(inds), dtype=int)*wid)//maxwid*hei,
        })

    def update_clusters(attr, old, new):
        source.data.update({'label': data.label[new]})
        data.lab = new

    def update_alpha(attr, old, new):
        imorig.glyph.global_alpha=1.-new
        imattr.glyph.global_alpha=new

    source.selected.on_change('indices', update_selection)
    radio.on_change('active', update_clusters)
    slider.on_change('value', update_alpha)
    select.on_change('value', update_cat)

