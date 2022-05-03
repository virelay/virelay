"""Trains a VGG16 model on the CIFAR-10 dataset."""

import argparse

import torch
from torchvision import transforms
from torchvision.models import vgg16
from torchvision.datasets import CIFAR10


def train_vgg(
        dataset_path: str,
        model_path: str,
        learning_rate: float,
        batch_size: int,
        number_of_epochs: int) -> None:
    """Trains a VGG16 model on CIFAR-10.

    Parameters
    ----------
        dataset_path: str
            The path to the CIFAR-10 dataset. If it does not exist, it is automatically downloaded.
        model_path: str
            The path to the file into which the trained model will be stored.
        learning_rate. float
            The learning rate that is to be used during training.
        batch_size: int
            The batch size that is to be used during training.
        number_of_epochs: int
            The number of epochs for which the model is to be trained.
    """

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')  # pylint: disable=no-member
    model = vgg16(num_classes=10).to(device)

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
    ])
    train_dataset = CIFAR10(root=dataset_path, train=True, download=True, transform=transform)
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    loss_function = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9, weight_decay=5e-4)

    number_of_batches = len(train_loader)
    for epoch in range(1, number_of_epochs + 1):
        for index, (batch, labels) in enumerate(train_loader):
            batch = batch.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            prediction = model(batch)  # pylint: disable=not-callable
            loss = loss_function(prediction, labels)
            loss.backward()
            optimizer.step()

            current_batch = index + 1
            if current_batch % 250 == 0:
                number_of_correct_predictions = (prediction.argmax(axis=1) == labels).sum().item()
                accuracy = 100 * (number_of_correct_predictions / batch.size(0))
                print(
                    f'Epoch {epoch}/{number_of_epochs}, '
                    f'batch {current_batch}/{number_of_batches}, '
                    f'loss = {loss:.5f}, '
                    f'accuracy = {accuracy:.2f}%'
                )

    torch.save(model.state_dict(), model_path)


def main() -> None:
    """The entrypoint to the train_vgg script."""

    argument_parser = argparse.ArgumentParser(
        prog='train_vgg',
        description='Trains a VGG16 model on CIFAR-10.'
    )
    argument_parser.add_argument(
        'dataset_path',
        type=str,
        help='The path to the CIFAR-10 dataset. If it does not exist, it is automatically downloaded.'
    )
    argument_parser.add_argument(
        'model_path',
        type=str,
        help='The path to the file into which the trained model will be stored.'
    )
    argument_parser.add_argument(
        '-l',
        '--learning-rate',
        dest='learning_rate',
        type=float,
        default=0.001,
        help='The learning rate that is to be used during training. Defaults to 0.001.'
    )
    argument_parser.add_argument(
        '-b',
        '--batch-size',
        dest='batch_size',
        type=int,
        default=64,
        help='The batch size that is to be used during training. Defaults to 64.'
    )
    argument_parser.add_argument(
        '-e',
        '--number-of-epochs',
        dest='number_of_epochs',
        type=int,
        default=10,
        help='The number of epochs for which the model is to be trained. Defaults to 10.'
    )
    arguments = argument_parser.parse_args()

    train_vgg(
        arguments.dataset_path,
        arguments.model_path,
        arguments.learning_rate,
        arguments.batch_size,
        arguments.number_of_epochs
    )


if __name__ == '__main__':
    main()
