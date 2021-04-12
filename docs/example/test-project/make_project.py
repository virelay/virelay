from os.path import dirname, relpath

import click
import h5py
import yaml


@click.command()
@click.argument('input-file', type=click.Path(exists=True, dir_okay=False))
@click.argument('attribution-file', type=click.Path(exists=True, dir_okay=False))
@click.argument('analysis-file', type=click.Path(exists=True, dir_okay=False))
@click.argument('label-map-file', type=click.Path(exists=True, dir_okay=False))
@click.option('--project-name', default='Unknown Project')
@click.option('--dataset-name', default='Unknown Dataset')
@click.option('--model-name', default='Unknown Model')
@click.option('--attribution-name', default='Unknown Attribution')
@click.option('--analysis-name', default='Unknown Analysis')
@click.option('--output', type=click.Path(writable=True, dir_okay=False))
def main(
    input_file,
    attribution_file,
    analysis_file,
    label_map_file,
    project_name,
    dataset_name,
    model_name,
    attribution_name,
    analysis_name,
    output
):
    with h5py.File(input_file, 'r') as fd:
        input_shape = fd['data'].shape

    if output is not None:
        root = dirname(output)
    else:
        root = '.'

    project = {
        'project': {
            'name': project_name,
            'model': model_name,
            'label_map': relpath(label_map_file, start=root),
            'dataset': {
                'name': dataset_name,
                'type': 'hdf5',
                'path': relpath(input_file, start=root),
                'input_width': input_shape[2],
                'input_height': input_shape[3],
                'down_sampling_method': 'none',
                'up_sampling_method': 'none',
            },
            'attributions': {
                'attribution_method': attribution_name,
                'attribution_strategy': 'true_label',
                'sources': [relpath(attribution_file, start=root)],
            },
            'analyses': [
                {
                    'analysis_method': analysis_name,
                    'sources': [relpath(analysis_file, start=root)]
                }
            ]
        }
    }

    if output is None:
        print(yaml.dump(project, default_flow_style=False))
    else:
        with open(output, 'w') as fd:
            yaml.dump(project, fd, default_flow_style=False)


if __name__ == '__main__':
    main()
