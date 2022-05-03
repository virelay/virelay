"""Generates a ViRelAy project file from a database file, an attribution file, an analysis file, and a label map file.
"""

import argparse
from os.path import dirname, relpath

import h5py
import yaml


def make_project(
        dataset_file_path: str,
        attribution_file_path: str,
        analysis_file_path: str,
        label_map_file_path: str,
        project_name: str,
        dataset_name: str,
        dataset_down_sampling_method: str,
        dataset_up_sampling_method: str,
        model_name: str,
        attribution_name: str,
        analysis_name: str,
        output_file_path: str) -> None:
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
    if output_file_path is not None:
        project_root_path = dirname(output_file_path)
    else:
        project_root_path = '.'

    # Determines the shape of the dataset samples
    with h5py.File(dataset_file_path, 'r') as dataset_file:
        input_shape = dataset_file['data'].shape  # pylint: disable=no-member

    # Generates the information, which will be stored in the project file
    project = {
        'project': {
            'name': project_name,
            'model': model_name,
            'label_map': relpath(label_map_file_path, start=project_root_path),
            'dataset': {
                'name': dataset_name,
                'type': 'hdf5',
                'path': relpath(dataset_file_path, start=project_root_path),
                'input_width': input_shape[2],
                'input_height': input_shape[3],
                'down_sampling_method': dataset_down_sampling_method,
                'up_sampling_method': dataset_up_sampling_method,
            },
            'attributions': {
                'attribution_method': attribution_name,
                'attribution_strategy': 'true_label',
                'sources': [relpath(attribution_file_path, start=project_root_path)],
            },
            'analyses': [
                {
                    'analysis_method': analysis_name,
                    'sources': [relpath(analysis_file_path, start=project_root_path)]
                }
            ]
        }
    }

    # If an output file path was specified, then the project is saved into the specified file, otherwise, the project
    # information is written to the standard output
    if output_file_path is None:
        print(yaml.dump(project, default_flow_style=False))
    else:
        with open(output_file_path, 'w', encoding='utf-8') as project_file:
            yaml.dump(project, project_file, default_flow_style=False)


def main() -> None:
    """The entrypoint to the make_project script."""

    argument_parser = argparse.ArgumentParser(
        prog='make_project',
        description='''Generates a ViRelAy project file from a database file, an attribution file, an analysis file, and
            a label map file.
        '''
    )
    argument_parser.add_argument(
        'dataset_file_path',
        type=str,
        help='The path to the dataset HDF5 file.'
    )
    argument_parser.add_argument(
        'attribution_file_path',
        type=str,
        help='The path to the attribution HDF5 file.'
    )
    argument_parser.add_argument(
        'analysis_file_path',
        type=str,
        help='The path to the analysis HDF5 file.'
    )
    argument_parser.add_argument(
        'label_map_file_path',
        type=str,
        help='The path to the label map YAML file.'
    )
    argument_parser.add_argument(
        '-p',
        '--project-name',
        dest='project_name',
        type=str,
        default='Unknown Project',
        help='The name of the project. Defaults to "Unknown Project".'
    )
    argument_parser.add_argument(
        '-d',
        '--dataset-name',
        dest='dataset_name',
        type=str,
        default='Unknown Dataset',
        help='The name of the dataset that the classifier was trained on. Defaults to "Unknown Dataset".'
    )
    argument_parser.add_argument(
        '-s',
        '--dataset-down-sampling-method',
        dest='dataset_down_sampling_method',
        type=str,
        choices=['none', 'center_crop', 'resize'],
        default='none',
        help='''The method that is to be used to down-sample images from the dataset that are larger than the input to
            the model. Defaults to "none".
        '''
    )
    argument_parser.add_argument(
        '-S',
        '--dataset-up-sampling-method',
        dest='dataset_up_sampling_method',
        type=str,
        choices=['none', 'fill_zeros', 'fill_ones', 'edge_repeat', 'mirror_edge', 'wrap_around', 'resize'],
        default='none',
        help='''The method that is to be used to up-sample images from the dataset that are smaller than the input to
            the model. Defaults to "none".
        '''
    )
    argument_parser.add_argument(
        '-m',
        '--model-name',
        dest='model_name',
        type=str,
        default='Unknown Model',
        help='The name of the classifier model on which the project is based. Defaults to "Unknown Model".'
    )
    argument_parser.add_argument(
        '-a',
        '--attribution-name',
        dest='attribution_name',
        type=str,
        default='Unknown Attribution',
        help='The name of the method that was used to compute the attributions. Defaults to "Unknown Attribution".'
    )
    argument_parser.add_argument(
        '-A',
        '--analysis-name',
        dest='analysis_name',
        type=str,
        default='Unknown Analysis',
        help='The name of the analysis that was performed on the attributions. Defaults to "Unknown Analysis".'
    )
    argument_parser.add_argument(
        '-o',
        '--output-file-path',
        dest='output_file_path',
        type=str,
        help='The path to the YAML file into which the project will be saved.'
    )
    arguments = argument_parser.parse_args()

    make_project(
        arguments.dataset_file_path,
        arguments.attribution_file_path,
        arguments.analysis_file_path,
        arguments.label_map_file_path,
        arguments.project_name,
        arguments.dataset_name,
        arguments.dataset_down_sampling_method,
        arguments.dataset_up_sampling_method,
        arguments.model_name,
        arguments.attribution_name,
        arguments.analysis_name,
        arguments.output_file_path
    )


if __name__ == '__main__':
    main()
