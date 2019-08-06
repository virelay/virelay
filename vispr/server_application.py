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

class ServerApplication:
    """Represents the Bokeh server application that renders the data on the client and handles user input."""

    def __init__(self, input_path, attribution_path, analysis_path, wnid_path, wordmap_path):
        """
        Initializes a new ServerApplication instance.

        Parameters:
        -----------
            input_path: str
                The path to the directory that contains the images of the dataset.
            attribution_path: str
                The path to the HDF5 file that contains the attributions.
            analysis_path: str
                The path to the HDF5 file that contains the analysis.
            wnids_path: str
                The path to the text file that contains the WordNet IDs of the classes of the classifier.
            wordmap_path: str
                The path to the JSON file that contains the mappings between the WordNet IDs and human-readable class
                names.
        """

        # Stores the arguments for later use
        self.input_path = input_path
        self.attribution_path = attribution_path
        self.analysis_path = analysis_path
        self.wordmap_path = wordmap_path
        self.wnid_path = wnid_path

        # Some configuration constants for the plotting
        self.number_of_images = 16
        self.width = 224
        self.height = 224
        self.maximum_width = 4 * self.width
        self.maximum_height = 4 * self.height
        self.colormap = d3['Category20'][20]

        # Gets the logger for the module
        self.logger = logging.getLogger(__name__)

        # Loads the analysis file and extracts the category names
        with h5py.File(self.analysis_path, 'r') as analysis_file:
            self.categories = list(analysis_file)

        # Loads the WordNet IDs file, which contains a mapping from the label numbers to the WNIDs
        with open(self.wnid_path, 'r') as wnid_file:
            self.wnids = wnid_file.read().split('\n')[:-1]

        # Loads the wordmap file, which contains the mapping between the WNIDs and their corresponding cleartext
        # descriptions
        with open(self.wordmap_path, 'r') as wordmap_file:
            self.wordmap = json.load(wordmap_file)

        # Loads the input images and the attributed images
        self.original_image_loader = OrigImage(self.input_path)
        self.attribution_image_loader = AttrImage(self.attribution_path)

        # Namespace to store data references
        self.data = Namespace()
        self.data.selected = Namespace()
        self.data.selected.category = self.categories[random.randint(0, len(self.categories))]
        self.data.selected.cluster = None
        self.data.selected.visualization = None

        # Initializes other class members
        self.sample_source = None
        self.image_source = None
        self.eigen_value_source = None
        self.sample_table = None
        self.original_image_renderer = None
        self.attribution_image_renderer = None

    def get_wnid_description(self, wnid):
        """
        Gets the human-readable cleartext descriptions for the specified WordNet ID.

        Parameters:
        -----------
            wnid: str
                The WordNet ID that is to be mapped.

        Returns:
        --------
            str:
                Returns the cleartext description for the specified WordNet ID. If the WordNet ID is invalid, 'UNKNOWN'
                is returned.
        """

        return self.wordmap.get(wnid, 'UNKNOWN')

    # load data for a new category
    def update_category(self, new_category):
        """
        Selects a new category and loads the associated data for it.

        Parameters:
        -----------
            new_category:
                The new category that is to be selected.
        """

        # Selects the new category and deselects everything selected previously
        self.data.selected.category = new_category
        self.sample_source.selected.indices = []

        # Loads the data of the newly selected category
        with h5py.File(self.analysis_path, 'r') as analysis_file:
            analysis_file = analysis_file[self.data.selected.category]
            self.data.cluster = {key: value[:] for key, value in analysis_file['cluster'].items()}
            self.data.visualization = {key: value[:] for key, value in analysis_file['visualization'].items()}
            self.data.eigen_value = analysis_file['eigen_value'][:]
            self.data.index = analysis_file['index'][:]

        # Resets the selected cluster and visualization if necessary (that is, when they are not in the newly selected
        # category)
        if self.data.selected.cluster not in self.data.cluster:
            self.data.selected.cluster = next(iter(self.data.cluster))
        if self.data.selected.visualization not in self.data.visualization:
            self.data.selected.visualization = next(iter(self.data.visualization))

        # Loads the attribution data for the newly selected category
        with h5py.File(self.attribution_path, 'r') as attribution_file:
            self.data.prediction = attribution_file['prediction'][self.data.index, :]

        # Updates the sample source with new category data
        description = [self.get_wnid_description(self.wnids[label_id]) for label_id in self.data.prediction.argmax(1)]
        visual_x, visual_y = self.data.visualization[self.data.selected.visualization].T
        visual_cluster = self.data.cluster[self.data.selected.cluster]
        self.sample_source.data.update({
            'i': range(len(visual_x)),
            'x': visual_x,
            'y': visual_y,
            'cluster': visual_cluster,
            'prediction': description
        })

        # Decides which images to show
        indices = list(range(self.number_of_images))
        self.image_source.data.update({
            'attribution': self.attribution_image_loader[self.data.index[indices]],
            'original': list(self.original_image_loader[self.data.index[indices]]),
            'x': (np.arange(self.number_of_images, dtype=int) * self.width) % self.maximum_width,
            'y': (np.arange(self.number_of_images, dtype=int) * self.width) // self.maximum_width * self.height,
        })

        # Updates the eigen value plot
        self.eigen_value_source.data.update({
            'x': range(len(self.data.eigen_value)),
            'y': self.data.eigen_value[::-1],
        })

    def update_selection(self, new_sample_index):
        """
        Updates the selected sample.

        Parameters:
        -----------
            new_sample_index: int
                The index of the sample that is to be selected.
        """

        self.sample_table.view = CDSView(source=self.sample_source, filters=[IndexFilter(new_sample_index)])

        if self.sample_source.selected.indices: # pylint: disable=no-member
            indices = self.sample_source.selected.indices[:self.number_of_images] # pylint: disable=no-member
        else:
            indices = list(range(self.number_of_images))
        indices = sorted(indices)

        self.image_source.data.update({
            'attribution': self.attribution_image_loader[self.data.index[indices]],
            'original': list(self.original_image_loader[self.data.index[indices]]),
            'x': (np.arange(len(indices), dtype=int) * self.width) % self.maximum_width,
            'y': (np.arange(len(indices), dtype=int) * self.width) // self.maximum_width * self.height,
        })

    def update_clusters(self, new_cluster):
        """
        Updates the clusters.

        Parameters:
        -----------
            new_cluster
                The new cluster.
        """

        self.data.selected.cluster = new_cluster
        self.sample_source.data.update({'cluster': self.data.cluster[self.data.selected.cluster]})

    def update_alpha(self, new_alpha):
        """
        Updates the alpha channel of the original and the attribution images. This slowly hides or reveals the original
        image, which is rendered under the attribution image.

        Parameters:
        -----------
            new_alpha: float
                The new value for the alpha channel.
        """

        self.original_image_renderer.glyph.global_alpha = 1.0 - new_alpha
        self.attribution_image_renderer.glyph.global_alpha = new_alpha

    def setup_up_bokeh_document(self, document):
        """
        Sets up the Bokeh server document.

        Parameters:
        -----------
            document:
                The document that represents the website displayed by the Bokeh server.
        """

        # Starts the initialization of the document
        self.logger.info('Setting up document...')


        # Initializes the source of the samples, images, and eigen values
        self.sample_source = ColumnDataSource({'i': [], 'x': [], 'y': [], 'cluster': [], 'prediction': []})
        self.image_source = ColumnDataSource({'attribution': [], 'original': [], 'x': [], 'y': []})
        self.eigen_value_source = ColumnDataSource({'x': [], 'y': []})

        # Loads the data for the initial selected category
        self.update_category(self.data.selected.category)

        # Creates a figure for the eigen values
        eigen_value_figure = figure(
            tools=[],
            plot_width=200,
            plot_height=800,
            min_border=1,
            min_border_left=1,
            toolbar_location="above",
            title="Eigen values"
        )

        # Creates a figure for the visualization (e.g. TSNE)
        visualization_figure = figure(
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
        visualization_colormap = linear_cmap('cluster', self.colormap, 0, len(self.colormap) - 1)
        visualization_figure.scatter(
            'x',
            'y',
            source=self.sample_source,
            size=6,
            color=visualization_colormap,
            nonselection_alpha=0.2,
            nonselection_color=visualization_colormap
        )

        # Creates the table for the selected samples
        sample_columns = [
            TableColumn(field='cluster', title='cluster', width=50),
            TableColumn(field='prediction', title='prediction'),
        ]
        sample_table = DataTable(source=self.sample_source, columns=sample_columns, width=250, height=800)

        # Creates a figure containing the original images and attributions
        image_figure = figure(
            tools=[],
            plot_width=800,
            plot_height=800,
            min_border=10,
            min_border_left=10,
            toolbar_location=None,
            x_axis_location=None,
            y_axis_location=None,
            title="Images",
            x_range=Range1d(start=0, end=self.maximum_width),
            y_range=Range1d(start=0, end=self.maximum_height)
        )
        self.attribution_image_renderer = image_figure.image(
            'attribution',
            x='x',
            y='y',
            dw=self.width,
            dh=self.height,
            source=self.image_source,
            palette='Magma256',
            global_alpha=0.0
        )
        self.original_image_renderer = image_figure.image_rgba(
            'original',
            x='x',
            y='y',
            dw=self.width,
            dh=self.height,
            source=self.image_source,
            global_alpha=1.0
        )

        # Adds some widgets to the document for selecting categories, selecting clusters, and changing the alpha channel
        # of the images (the attribution images are rendered above the respective original image, changing the alpha
        # reveals the original image or hides it behind the attribution image)
        category_select = Select(
            value=self.data.selected.category,
            options=[(category, '{0} ({1})'.format(self.wordmap[category], category)) for category in self.categories]
        )
        cluster_select = Select(
            value=self.data.selected.cluster,
            options=[cluster for cluster in self.data.cluster],
            width=200
        )
        alpha_slider = Slider(start=0.0, end=1.0, step=0.05, value=0.0, width=400, align='center')

        # Registers the event handlers for the UI controls
        category_select.on_change('value', self.update_category)
        cluster_select.on_change('value', self.update_clusters)
        alpha_slider.on_change('value', self.update_alpha)
        self.sample_source.selected.on_change('indices', self.update_selection) # pylint: disable=no-member

        # Sets up the layouting of the document
        top = row(category_select, cluster_select)
        bottom = row(eigen_value_figure, sample_table, visualization_figure, column(image_figure, alpha_slider))
        layout = column(top, bottom)
        document.add_root(layout)
        document.title = 'SPRINCL'

        # Finishes the setup of the Bokeh application
        self.logger.info('Ready for service.')
