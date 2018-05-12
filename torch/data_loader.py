import os

import torch
from PIL import Image
from torch.utils import data
from torchvision import transforms


class ImageFolder(data.Dataset):
    """Custom Dataset compatible with prebuilt DataLoader.
    
    This is just for tutorial. You can use the prebuilt torchvision.datasets.ImageFolder.
    """

    def __init__(self, root,
                 transform=None,
                 images_dim=(128, 128),
                 features_length=18):
        """Initializes image paths and preprocessing module."""
        self.images_dim = images_dim
        self.features_length = features_length
        self.image_paths = list(map(lambda x: os.path.join(root, x), os.listdir(root)))
        self.transform = transform

    def __getitem__(self, index):
        """Reads an image from a file and preprocesses it and returns."""
        image_path = self.image_paths[index]
        image = Image.open(image_path).convert('RGB')
        if self.transform is not None:
            image = self.transform(image)
        return (image, torch.ones(self.features_length))

    def __len__(self):
        """Returns the total number of image files."""
        return len(self.image_paths)


def get_loader(image_path, image_size, batch_size, features_length, num_workers=2):
    """Builds and returns Dataloader."""

    transform = transforms.Compose([
        transforms.Resize(image_size),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(contrast=0.5, saturation=0.5, hue=0.5),
        transforms.ToTensor()
    ])

    dataset = ImageFolder(root=image_path,
                          transform=transform,
                          images_dim=image_size,
                          features_length=features_length)

    data_loader = data.DataLoader(dataset=dataset,
                                  batch_size=batch_size,
                                  shuffle=True,
                                  num_workers=num_workers)
    return data_loader


if __name__ == '__main__':
    size = 64
    path = './resize_black'
    transform = transforms.Compose([
        transforms.Resize(size, interpolation=Image.HAMMING),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(contrast=0.5, saturation=0.5, hue=0.5),
        transforms.ToTensor(),
        transforms.ToPILImage()
    ])

    dataset = ImageFolder(path, transform)
    test_item = dataset.__getitem__(150)
    test_item[0].save("test.jpg")
