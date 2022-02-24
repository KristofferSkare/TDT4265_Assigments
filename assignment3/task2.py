import pathlib
import matplotlib.pyplot as plt
import torch
import utils
from torch import nn
from dataloaders import load_cifar10
from trainer import Trainer
import numpy as np


class ExampleModel(nn.Module):

    def __init__(self,
                 image_channels,
                 num_classes):
        """
            Is called when model is initialized.
            Args:
                image_channels. Number of color channels in image (3)
                num_classes: Number of classes we want to predict (10)
        """
        super().__init__()

        input_image_size = 32 * 32
        # TODO: Implement this function (Task  2a)
        num_conv_filters = [32, 64, 128]  # Set number of filters in first conv layer
        fully_hidden_layers = [64]

        self.num_classes = num_classes
        # Define the convolutional layers
        layer_depth = image_channels

        conv_layers = []
        for num_filters in num_conv_filters:
            conv_layers.append(
                nn.Conv2d(
                    in_channels=layer_depth,
                    out_channels=num_filters,
                    kernel_size=5,
                    stride=1,
                    padding=2
                )
            )
            conv_layers.append(nn.ReLU())
            conv_layers.append(nn.MaxPool2d(kernel_size=2, stride=2))
            layer_depth = num_filters

        self.feature_extractor = nn.Sequential(*conv_layers)

        num_flattened_nodes = int(np.floor(input_image_size / 4**(len(num_conv_filters)) * layer_depth))

        hidden_layers = []
        num_input_nodes = num_flattened_nodes
        for num_nodes in fully_hidden_layers:
            hidden_layers.append(nn.Linear(num_input_nodes, num_nodes))
            hidden_layers.append(nn.ReLU())
            num_input_nodes = num_nodes

        self.num_output_features = num_flattened_nodes
        # Initialize our last fully connected layer
        # Inputs all extracted features from the convolutional layers
        # Outputs num_classes predictions, 1 for each class.
        # There is no need for softmax activation function, as this is
        # included with nn.CrossEntropyLoss
        self.classifier = nn.Sequential(
            nn.Flatten(start_dim=1),
            *hidden_layers, 
            nn.Linear(fully_hidden_layers[-1], num_classes)
        )

    def forward(self, x):
        """
        Performs a forward pass through the model
        Args:
            x: Input image, shape: [batch_size, 3, 32, 32]
        """
        # TODO: Implement this function (Task  2a)
        batch_size = x.shape[0]
        expected_shape = (batch_size, self.num_classes)

        out = self.classifier(self.feature_extractor(x))

        assert out.shape == (batch_size, self.num_classes),\
            f"Expected output of forward pass to be: {expected_shape}, but got: {out.shape}"
        return out


def create_plots(trainer: Trainer, name: str):
    plot_path = pathlib.Path("plots")
    plot_path.mkdir(exist_ok=True)
    # Save plots and show them
    plt.figure(figsize=(20, 8))
    plt.subplot(1, 2, 1)
    plt.title("Cross Entropy Loss")
    utils.plot_loss(trainer.train_history["loss"], label="Training loss", npoints_to_average=10)
    utils.plot_loss(trainer.validation_history["loss"], label="Validation loss")
    plt.legend()
    plt.subplot(1, 2, 2)
    plt.title("Accuracy")
    utils.plot_loss(trainer.validation_history["accuracy"], label="Validation Accuracy")
    plt.legend()
    plt.savefig(plot_path.joinpath(f"{name}_plot.png"))
    plt.show()


def main():
    # Set the random generator seed (parameters, shuffling etc).
    # You can try to change this and check if you still get the same result! 
    utils.set_seed(0)
    epochs = 10
    batch_size = 64
    learning_rate = 5e-2
    early_stop_count = 4
    dataloaders = load_cifar10(batch_size)
    model = ExampleModel(image_channels=3, num_classes=10)
    trainer = Trainer(
        batch_size,
        learning_rate,
        early_stop_count,
        epochs,
        model,
        dataloaders
    )
    trainer.train()
    create_plots(trainer, "task2")

if __name__ == "__main__":
    main()