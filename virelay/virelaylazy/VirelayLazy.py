import os
import yaml
import json
import torchvision
import torch
from typing import List


from .utils import *

from corelay.processor.affinity import SparseKNN
from corelay.processor.flow import Parallel
from corelay.pipeline.spectral import SpectralClustering
from corelay.processor.embedding import TSNEEmbedding, UMAPEmbedding, EigenDecomposition
from corelay.processor.clustering import KMeans, DBSCAN, HDBSCAN, AgglomerativeClustering
import zennit
from zennit.attribution import Gradient, SmoothGrad, IntegratedGradients, Occlusion
from zennit.composites import COMPOSITES

class VirelayLazy:
    """
    A wrapper for VireLay. https://virelay.readthedocs.io/en/latest/ 

    Args:
        model (torch.nn.module): The PyTorch model to be used for analysis.
        model_params_path (os.PathLike): The path to the model parameters.
        dataset_path (os.PathLike): The path to the dataset.
        transforms (torchvision.transforms): The image transformations to be applied to the dataset.
        device (torch.device, optional): The device on which the analysis will be performed (default is 'cuda:0' if available, otherwise 'cpu').
        label_dict (dict, optional): A dictionary mapping class indices to labels (default is None).
        num_classes (int, optional): The number of classes in the dataset (default is None).
        project_folder (os.PathLike, optional): The path to the project folder (default is "./").

    Attributes:
        model (torch.nn.module): The PyTorch model used for analysis.
        labels (list): A list of dictionaries representing class labels.
        attribution_name (str): The name of the attribution.
        analysis_folder (str): The path to the analysis folder.
        dataset_path (os.PathLike): The path to the dataset.
        project_folder (os.PathLike): The path to the project folder.
        transforms (torchvision.transforms): The image transformations applied to the dataset.
        device (torch.device): The device on which the analysis is performed.
        analyses (list): A list to store analysis results.

    Raises:
        ValueError: If neither `num_classes` nor `label_dict` is specified.

    """

    def __init__(self, model : torch.nn.Module,  
                 dataset_path : os.PathLike, 
                 transforms : torchvision.transforms,
                 model_weights_path : os.PathLike = None, 
                 device : torch.device = None, 
                 labels : List[dict] = None, 
                 num_classes : int = None, 
                 project_folder: os.PathLike = "./"):
        self.model = model
        if model_weights_path is not None:
            self.load_model_params(model_weights_path)
       
        if labels is None:
            if num_classes is not None:
                labels = [{"index" : i, "word_net_id": str(i), "name": f"Class {i}"} for i in range(num_classes)]
            else:
                raise ValueError("must specify either num_classes or labels")

        self.attribution_name = "unknown attribution"
        self.analysis_folder = os.path.join(project_folder,"analyses")
        self.dataset_path = dataset_path
        self.project_folder = project_folder
        self.transforms = transforms
        if device is None:
            self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        self.make_label_json(labels)
        self.attribution_file_path = None
        self.analyses = []

    def make_label_json(self, labels):
        self.label_map_file = os.path.join(self.project_folder,"label-map.json")
        with open(self.label_map_file, "w") as jfile:
            json.dump(labels, jfile)


    def set_dataset(self, path):
        self.dataset_path = path

    def set_project_folder(self, path):
        self.project_folder = path

    def load_model_params(self, path):
        params = torch.load(path)
        self.model_params = params
        self.model.load_state_dict(params)

    def lazy_init(self):
        '''
        Provides a lazy initialization of VireLay with options that generally work well
        '''
        eps = COMPOSITES["epsilon_gamma_box"](-3.0, 3.0)
        self.set_attributor("gradient", eps)
        self.meta_analysis()
        self.make_project_file("no regex")

    def set_attributor(self, attributor_name: str, composite : zennit.core.Composite, attributor_kwargs = None):
        ATTRIBUTORS = {
        'gradient': Gradient,
        'smoothgrad': SmoothGrad,
        'integrads': IntegratedGradients,
        'occlusion': Occlusion,
        'inputxgrad': IntegratedGradients,
        }
        if attributor_kwargs is None:
            attributor_kwargs = {
            'smoothgrad': {'noise_level': 0.08, 'n_iter': 10},
            'integrads': {'n_iter': 5},
            'inputxgrad': {'n_iter': 5},
            'occlusion': {'window': (48, 48), 'stride': (24, 24)},
            }.get(attributor_name, {})
        self.attribution_name = attributor_name
        return ATTRIBUTORS[attributor_name](self.model, composite, **attributor_kwargs)

    def set_attribution_path(self, path : str):
        if os.path.exists(path):
            self.attribution_file_path = path
            self.attribution_name = path.split(".")[0]
        else:
            raise FileNotFoundError

    def compute_attributions(self, batch_size : int, number_of_classes : int, composite : zennit.core.Composite, attributor_name = 'gradient' , params = None, attribution_file_name = None):
        """Uses LRP to generate attributions for a trained VGG16 model.

        Parameters
        ----------
            dataset_path: str
                The path to the CIFAR-10 dataset. If it does not exist, it is automatically downloaded.
            attribution_database_file_path: str
                The path to the attribution database HDF5 file that is to be created.
            batch_size: int
                The batch size that is to be used during the computation of the attributions.
        """
        if attribution_file_name is None:
            attribution_file_name = attributor_name
        
        self.attribution_file_path = os.path.join(self.project_folder,attribution_file_name)

        if params is not None:
            state_dict = torch.load(params)
            self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()
        
        train_dataset = AllowEmptyClassImageFolder(self.dataset_path, transform=self.transforms)
        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=False)
        number_of_samples = len(train_dataset)
      
        

        with create_attribution_database(
                self.attribution_file_path,
                train_dataset[0][0].shape,
                number_of_classes,
                number_of_samples) as attribution_database_file:

            attributor = self.set_attributor(attributor_name, composite)

            number_of_samples_processed = 0
            with attributor:
                for batch, labels in train_loader:
                    batch = batch.to(self.device)
                    labels = labels.to(self.device)
                    predictions, attributions = attributor(
                        batch,
                        torch.eye(number_of_classes, device=self.device)[labels]  # pylint: disable=no-member
                    )

                    append_attributions(
                        attribution_database_file,
                        number_of_samples_processed,
                        attributions,
                        predictions,
                        labels
                    )
                    number_of_samples_processed += attributions.shape[0]

                    print(f'Computed {number_of_samples_processed}/{number_of_samples} attributions')


    def check_attribution_path(self):
        if self.attribution_file_path is None:
            raise ValueError("Need to set attribution_file_path."
                             "If you have computed attributions use 'set_attribution_path(*path to attribution file*)'."
                             "If you have not computed attributions use 'compute_attributions(*args, **kwargs)'")


    #Make analysis
    def add_meta_analysis(
            self,
            variant = "spectral",
            class_indices = None,
            number_of_eigenvalues = 16,
            number_of_clusters_list = list(range(2, 31)),
            number_of_neighbors = 32,
            analysis_file_name = None) -> None:
        """Performs a meta-analysis over the specified attribution data and writes the results into an analysis database.

        Parameters
        ----------
            attribution_file_path: str
                The path to the attribution database file, that contains the attributions for which the meta-analysis is to
                be performed.
            analysis_file_path: str
                The path to the analysis database file, into which the results of the meta-analysis are to be written.
            variant: str
                The meta-analysis variant that is to be performed. Can be one of "absspectral", "spectral", "fullspectral",
                or "histogram".
            class_indices: List[int]
                The indices of the classes for which the meta-analysis is to be performed. If not specified, then the
                meta-analysis is performed for all classes.
            label_map_file_path: str
                The path to the label map file, which contains a mapping between the class indices and their corresponding
                names and WordNet IDs.
            number_of_eigenvalues: int
                The number of eigenvalues of the eigenvalue decomposition.
            number_of_clusters_list: List[int]
                A list that can contain multiple numbers of clusters. For each number of clusters in this list, all
                clustering methods and the meta-analysis are performed.
            number_of_neighbors: int
                The number of neighbors that are to be considered in the k-nearest neighbor clustering algorithm.
        """
        self.analyses.append(variant)
        if analysis_file_name is None:
            print("No file name provided. Using default file name: 'analysis.h5'")
            analysis_file_name = "analysis.h5"

        self.check_attribution_path()
        

        self.analysis_folder = os.path.join(self.project_folder,"analyses/")
        if not os.path.exists(self.analysis_folder):
            os.makedirs(self.analysis_folder)
        # Determines the pre-processing pipeline and the distance metric that are to be used for the meta-analysis
        pre_processing_pipeline = VARIANTS[variant]['preprocessing']
        distance_metric = VARIANTS[variant]['distance']
        analysis_file_path = os.path.join(self.analysis_folder,analysis_file_name)
        # Creates the meta-analysis pipeline
        pipeline = SpectralClustering(
            preprocessing=pre_processing_pipeline,
            pairwise_distance=distance_metric,
            affinity=SparseKNN(n_neighbors=number_of_neighbors, symmetric=True),
            embedding=EigenDecomposition(n_eigval=number_of_eigenvalues, is_output=True),
            clustering=Parallel([
                Parallel([
                    KMeans(n_clusters=number_of_clusters) for number_of_clusters in number_of_clusters_list
                ], broadcast=True),
                Parallel([
                    DBSCAN(eps=number_of_clusters / 10.0) for number_of_clusters in number_of_clusters_list
                ], broadcast=True),
                HDBSCAN(),
                Parallel([
                    AgglomerativeClustering(n_clusters=number_of_clusters) for number_of_clusters in number_of_clusters_list
                ], broadcast=True),
                Parallel([
                    UMAPEmbedding(),
                    TSNEEmbedding(),
                ], broadcast=True)
            ], broadcast=True, is_output=True)
        )

        # Loads the label map and converts it to a dictionary, which maps the class index to its WordNet ID
        if self.label_map_file is not None:
            with open(self.label_map_file, 'r', encoding='utf-8') as label_map_file:
                label_map = json.load(label_map_file)
            wordnet_id_map = {label['index']: label['word_net_id'] for label in label_map}
            class_name_map = {label['index']: label['name'] for label in label_map}
        else:
            wordnet_id_map = {}
            class_name_map = {}

        # Retrieves the labels of the samples
        with h5py.File(self.attribution_file_path, 'r') as attributions_file:
            labels = attributions_file['label'][:]

        # Gets the indices of the classes for which the meta-analysis is to be performed, if non were specified, the the
        # meta-analysis is performed for all classes
        if class_indices is None:
            class_indices = [int(label['index']) for label in label_map]

        # Truncate the analysis database
        if os.path.isfile(analysis_file_path):
            print(f'Truncating {analysis_file_path}')
        h5py.File(analysis_file_path, 'w').close()

        # Cycles through all classes and performs the meta-analysis for each of them
        for class_index in class_indices:
            # Loads the attribution data for the samples of the current class
            print(f'Loading class {class_name_map[class_index]}')
            with h5py.File(self.attribution_file_path, 'r') as attributions_file:
                indices_of_samples_in_class, = np.nonzero(labels == class_index)
                attribution_data = attributions_file['attribution'][indices_of_samples_in_class, :]
                if 'train' in attributions_file:
                    train_flag = attributions_file['train'][indices_of_samples_in_class.tolist()]
                else:
                    train_flag = None
            # Performs the meta-analysis for the attributions of the current class
            print(f'Computing class {class_name_map[class_index]}')
            (eigenvalues, embedding), (kmeans, dbscan, hdbscan, agglomerative, (umap, tsne)) = pipeline(attribution_data)

            # Append the meta-analysis to the analysis database
            print(f'Saving class {class_name_map[class_index]}')
            with h5py.File(analysis_file_path, 'a') as analysis_file:

                # The name of the analysis is the name of the class
                analysis_name = wordnet_id_map.get(class_index, f'{class_index:08d}')

                # Adds the indices of the samples in the current class to the analysis database
                analysis_group = analysis_file.require_group(analysis_name)
                analysis_group['index'] = indices_of_samples_in_class.astype('uint32')

                # Adds the spectral embedding to the analysis database
                embedding_group = analysis_group.require_group('embedding')
                embedding_group['spectral'] = embedding.astype(np.float32)
                embedding_group['spectral'].attrs['eigenvalue'] = eigenvalues.astype(np.float32)

                # Adds the t-SNE embedding to the analysis database
                embedding_group['tsne'] = tsne.astype(np.float32)
                embedding_group['tsne'].attrs['embedding'] = 'spectral'
                embedding_group['tsne'].attrs['index'] = np.array([0, 1])

                # Adds the uMap embedding to the analysis database
                embedding_group['umap'] = umap.astype(np.float32)
                embedding_group['umap'].attrs['embedding'] = 'spectral'
                embedding_group['umap'].attrs['index'] = np.array([0, 1])

                # Adds the k-means clustering of the embeddings to the analysis database
                cluster_group = analysis_group.require_group('cluster')
                for number_of_clusters, clustering in zip(number_of_clusters_list, kmeans):
                    clustering_dataset_name = f'kmeans-{number_of_clusters:02d}'
                    cluster_group[clustering_dataset_name] = clustering
                    cluster_group[clustering_dataset_name].attrs['embedding'] = 'spectral'
                    cluster_group[clustering_dataset_name].attrs['k'] = number_of_clusters
                    cluster_group[clustering_dataset_name].attrs['index'] = np.arange(
                        embedding.shape[1],
                        dtype=np.uint32
                    )

                # Adds the DBSCAN epsilon clustering of the embeddings to the analysis database
                for number_of_clusters, clustering in zip(number_of_clusters_list, dbscan):
                    clustering_dataset_name = f'dbscan-eps={number_of_clusters / 10.0:.1f}'
                    cluster_group[clustering_dataset_name] = clustering
                    cluster_group[clustering_dataset_name].attrs['embedding'] = 'spectral'
                    cluster_group[clustering_dataset_name].attrs['index'] = np.arange(
                        embedding.shape[1],
                        dtype=np.uint32
                    )

                # Adds the HDBSCAN clustering of the embeddings to the analysis database
                clustering_dataset_name = 'hdbscan'
                cluster_group[clustering_dataset_name] = hdbscan
                cluster_group[clustering_dataset_name].attrs['embedding'] = 'spectral'
                cluster_group[clustering_dataset_name].attrs['index'] = np.arange(
                    embedding.shape[1],
                    dtype=np.uint32
                )

                # Adds the Agglomerative clustering of the embeddings to the analysis database
                for number_of_clusters, clustering in zip(number_of_clusters_list, agglomerative):
                    clustering_dataset_name = f'agglomerative-{number_of_clusters:02d}'
                    cluster_group[clustering_dataset_name] = clustering
                    cluster_group[clustering_dataset_name].attrs['embedding'] = 'spectral'
                    cluster_group[clustering_dataset_name].attrs['k'] = number_of_clusters
                    cluster_group[clustering_dataset_name].attrs['index'] = np.arange(
                        embedding.shape[1],
                        dtype=np.uint32
                    )

                # If the attributions were computed on the training split of the dataset, then the training flag is set
                if train_flag is not None:
                    cluster_group['train_split'] = train_flag


    #create project file
    def make_project_file(self,
            label_index_regex = "^data\/(\\d)\/(.+)\\.jpg$", #data/{class idx}/img.jpg
            project_name = "project",
            dataset_name = "unknown dataset",
            dataset_down_sampling_method = "none",
            dataset_up_sampling_method = "same",
            model_name = "model",
            strategy = "true_label") -> None:
        """Generates a ViRelAy project file.

        Parameters
        ----------
            dataset_file_path: str
                The path to the dataset HDF5 file.
            attribution_file_path: str
                The path to the attribution HDF5 file.
            analysis_file_path: str
                The path to the analysis HDF5 file.
            label_map_file_path: str
                The path to the label map YAML file.
            project_name: str
                The name of the project.
            dataset_name: str
                The name of the dataset that the classifier was trained on.
            dataset_down_sampling_method: str
                The method that is to be used to down-sample images from the dataset that are larger than the input to the
                model. Must be one of "none", "center_crop", or "resize".
            dataset_up_sampling_method: str
                The method that is to be used to up-sample images from the dataset that are smaller than the input to the
                model. Must be one of "none", "fill_zeros", "fill_ones", "edge_repeat", "mirror_edge", "wrap_around", or
                "resize".
            model_name: str
                The name of the classifier model on which the project is based.
            attribution_name: str
                The name of the method that was used to compute the attributions.
            analysis_name: str
                The name of the analysis that was performed on the attributions.
            output_file_path: str
                The path to the YAML file into which the project will be saved.
        """

        # Determines the root path of the project, which is needed to make all paths stored in the project file relative to
        # the project file
        if dataset_up_sampling_method == "same":
            dataset_up_sampling_method = dataset_down_sampling_method


        self.check_attribution_path()
        
        # Determines the shape of the dataset samples
        #with h5py.File(dataset_file_path, 'r') as dataset_file:
        #    input_shape = dataset_file['data'].shape  # pylint: disable=no-member
        analyses = []
        for i in os.listdir(self.analysis_folder):
            source = "analyses/"+i
            method = i.split("/")[-1][:-3]
            tmp_dict = [{'analysis_method': method, "sources": [source]}]
            analyses+=tmp_dict
        # Generates the information, which will be stored in the project file
        project = {
            'project': {
                'name': project_name,
                'model': model_name,
                'label_map': os.path.relpath(self.label_map_file, start=self.project_folder),
                'dataset': {
                    'name': dataset_name,
                    'type': 'image_directory',
                    'path': os.path.relpath(self.dataset_path, start=self.project_folder),
                    'input_width': 256,
                    'input_height': 256,
                    'down_sampling_method': dataset_down_sampling_method,
                    'up_sampling_method': dataset_up_sampling_method,
                    'label_index_regex' : label_index_regex,
                    'label_word_net_id_regex' : None
                },
                'attributions': {
                    'attribution_method': self.attribution_name,
                    'attribution_strategy': strategy,
                    'sources': [os.path.relpath(self.attribution_file_path, start=self.project_folder)],
                },
                'analyses': analyses
            }
        }

        # If an output file path was specified, then the project is saved into the specified file, otherwise, the project
        # information is written to the standard output

        self.project = os.path.join(self.project_folder, project_name+".yaml")

        if self.project_folder is None:
            print(yaml.dump(project, default_flow_style=False))
        else:
            with open(self.project, 'w', encoding='utf-8') as project_file:
                yaml.dump(project, project_file, default_flow_style=False)
        

    @staticmethod
    def start_virelay(project_file, host="localhost", port="8080", debug_mode : bool = False):
        """
        Starts the virelay service using the specified project YAML file.

        Args:
            project_file (str, optional): Path to the project YAML file. If not provided, the function
                will attempt to use the project YAML file associated with the current instance.
            host (str, optional): The hostname or IP address where the virelay service will run. Defaults to "localhost".
            port (str, optional): The port number on which the virelay service will listen. Defaults to "5051".
            debug_mode (bool, optional): Set to True to enable debug mode, False otherwise. Defaults to False.

        Raises:
            FileNotFoundError: If `project_file` is not provided or the associated project YAML file cannot be found.

        Returns:
            None
        """
        import subprocess
        cmd = ["python", "virelay", project_file, "-H", host, "-p", str(port)]
        if debug_mode:
            cmd += ["-d"]
        print(" ".join(cmd))
        subprocess.call(cmd)
