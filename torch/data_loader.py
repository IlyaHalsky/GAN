import os

import torch
from PIL import Image
from torch.utils import data
from torchvision import transforms
import numpy as np


class ImageFolder(data.Dataset):
    """Custom Dataset compatible with prebuilt DataLoader.
    
    This is just for tutorial. You can use the prebuilt torchvision.datasets.ImageFolder.
    """

    def __init__(self, root, label_root,
                 transform=None,
                 images_dim=(128, 128),
                 features_length=15):
        """Initializes image paths and preprocessing module."""
        self.root = root
        self.label_root = label_root
        self.images_dim = images_dim
        self.features_length = features_length
        self.image_paths = list(map(lambda x: os.path.join(root, x), os.listdir(root)))
        self.image_names = list(map(lambda x: x.split('.')[0], os.listdir(root)))
        self.transform = transform

    def __getitem__(self, index):
        """Reads an image from a file and preprocesses it and returns."""
        image_path = self.image_paths[index]
        image = Image.open(image_path).convert('RGB')
        card_name = self.image_names[index]
        file = open(self.label_root + card_name + '.txt', 'r')
        labels = list(map(int, file.read().split(',')))
        if self.transform is not None:
            image = self.transform(image)
        return (image, torch.from_numpy(np.array(labels)).float())

    def __len__(self):
        """Returns the total number of image files."""
        return len(self.image_paths)


def get_loader(image_path, label_path, image_size, batch_size, features_length, num_workers=2):
    """Builds and returns Dataloader."""

    transform = transforms.Compose([
        transforms.Resize(image_size),
        transforms.ToTensor()
    ])

    dataset = ImageFolder(root=image_path,
                          label_root=label_path,
                          transform=transform,
                          images_dim=image_size,
                          features_length=features_length)

    data_loader = data.DataLoader(dataset=dataset,
                                  batch_size=batch_size,
                                  shuffle=True,
                                  num_workers=num_workers)
    return data_loader


if __name__ == '__main__':
    size = 256
    path = './resize_cards'
    labels = './features/'
    transform = transforms.Compose([
        transforms.Resize(size, interpolation=Image.HAMMING),
        transforms.ToTensor(),
        transforms.ToPILImage()
    ])

    dataset = ImageFolder(path, labels, transform)
    test_item = dataset.__getitem__(150)
    print(test_item)
    test_item[0].save("test.jpg")
