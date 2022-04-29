"""Generates a ViRelAy project file from a database file, an attribution file, an analysis file, and a label map file.
"""

from os.path import dirname, relpath

import h5py
import yaml
import click


@click.command()
@click.argument('dataset-file-path', type=click.Path(exists=True, dir_okay=False))
@click.argument('attribution-file-path', type=click.Path(exists=True, dir_okay=False))
@click.argument('analysis-file-path', type=click.Path(exists=True, dir_okay=False))
@click.argument('label-map-file-path', type=click.Path(exists=True, dir_okay=False))
@click.option('--project-name', default='Unknown Project')
@click.option('--dataset-name', default='Unknown Dataset')
@click.option('--model-name', default='Unknown Model')
@click.option('--attribution-name', default='Unknown Attribution')
@click.option('--analysis-name', default='Unknown Analysis')
@click.option('--output-file-path', type=click.Path(writable=True, dir_okay=False))
def main(
        dataset_file_path,
        attribution_file_path,
        analysis_file_path,
        label_map_file_path,
        project_name,
        dataset_name,
        model_name,
        attribution_name,
        analysis_name,
        output_file_path):
    """The entrypoint to the make_project script, which generates a ViRelAy project file.

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
            The name of the project. Defaults to "Unknown Project".
        dataset_name: str
            The name of the dataset that the classifier was trained on. Defaults to "Unknown Dataset".
        model_name: str
            The name of the classifier model on which the project is based. Defaults to "Unknown Model".
        attribution_name: str
            The name of the method that was used to compute the attributions. Defaults to "Unknown Attribution".
        analysis_name: str
            The name of the analysis that was performed on the attributions. Defaults to "Unknown Analysis".
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
                'down_sampling_method': 'none',
                'up_sampling_method': 'none',
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


# If the script is directly invoked, then the main function is called
if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
