import os

import torch
import torchvision
from model import Discriminator
from model import Generator
from torch import optim
from torch.autograd import Variable


class Solver(object):
    def __init__(self, config, data_loader):
        self.generator = None
        self.discriminator = None
        self.g_optimizer = None
        self.d_optimizer = None
        self.g_conv_dim = config.g_conv_dim
        self.d_conv_dim = config.d_conv_dim
        self.z_dim = config.z_dim
        self.label_dim = config.label_dim
        self.beta1 = config.beta1
        self.beta2 = config.beta2
        self.image_size = config.image_size
        self.data_loader = data_loader
        self.num_epochs = config.num_epochs
        self.batch_size = config.batch_size
        self.sample_size = config.sample_size
        self.lr = config.lr
        self.log_step = config.log_step
        self.sample_step = config.sample_step
        self.sample_path = config.sample_path
        self.model_path = config.model_path
        self.build_model()

    def build_model(self):
        """Build generator and discriminator."""
        self.generator = Generator(z_dim=self.z_dim,
                                   image_size=self.image_size,
                                   label_dim=self.label_dim,
                                   conv_dim=self.d_conv_dim)
        self.discriminator = Discriminator(z_dim=self.z_dim,
                                           image_size=self.image_size,
                                           label_dim=self.label_dim,
                                           conv_dim=self.d_conv_dim)
        self.g_optimizer = optim.Adam(self.generator.parameters(),
                                      self.lr, [self.beta1, self.beta2])
        self.d_optimizer = optim.Adam(self.discriminator.parameters(),
                                      self.lr, [self.beta1, self.beta2])

        if torch.cuda.is_available():
            self.generator.cuda()
            self.discriminator.cuda()

    def to_variable(self, x):
        """Convert tensor to variable."""
        if torch.cuda.is_available():
            x = x.cuda()
        return Variable(x)

    def to_data(self, x):
        """Convert variable to tensor."""
        if torch.cuda.is_available():
            x = x.cpu()
        return x.data

    def reset_grad(self):
        """Zero the gradient buffers."""
        self.discriminator.zero_grad()
        self.generator.zero_grad()

    def denorm(self, x):
        """Convert range (-1, 1) to (0, 1)"""
        out = (x + 1) / 2
        return out.clamp(0, 1)

    def denorm_2(self, x):
        out = (x + 0.1)
        return out.clamp(0, 1)

    def get_fixed_label(self):
        for i, data in enumerate(self.data_loader):
            value = data[1]
            return value

    def train(self):
        """Train generator and discriminator."""
        fixed_noise = self.to_variable(torch.randn(self.batch_size, self.z_dim))
        fixed_label = self.get_fixed_label()

        total_step = len(self.data_loader)
        for epoch in range(self.num_epochs):
            for i, data in enumerate(self.data_loader):
                # ===================== Train D =====================#
                images = self.to_variable(data[0])
                batch_size = data[0].size(0)
                labels = self.to_variable(data[1]
                                          .unsqueeze(-1)
                                          .unsqueeze(-1)
                                          .expand(batch_size, data[1].size(1), images.size(2), images.size(3)))

                noise = self.to_variable(torch.randn(batch_size, self.z_dim))

                # Train D to recognize real images as real.
                outputs = self.discriminator(images, labels)
                real_loss = torch.mean((
                                               outputs - 1) ** 2)  # L2 loss instead of Binary cross entropy loss (this is optional for stable training)

                # Train D to recognize fake images as fake.
                fake_features = self.generator(noise, data[1])
                outputs = self.discriminator(fake_features, labels)
                fake_loss = torch.mean(outputs ** 2)

                # Backprop + optimize
                d_loss = real_loss + fake_loss
                self.reset_grad()
                d_loss.backward()
                self.d_optimizer.step()

                # ===================== Train G =====================#
                noise = self.to_variable(torch.randn(batch_size, self.z_dim))

                # Train G so that D recognizes G(z) as real.
                fake_features = self.generator(noise, data[1])
                outputs = self.discriminator(fake_features, labels)
                g_loss = torch.mean((outputs - 1) ** 2)

                # Backprop + optimize
                self.reset_grad()
                g_loss.backward()
                self.g_optimizer.step()

                # print the log info
                if (i + 1) % self.log_step == 0:
                    print('Epoch [%d/%d], Step[%d/%d], d_real_loss: %.4f, '
                          'd_fake_loss: %.4f, g_loss: %.4f'
                          % (epoch + 1, self.num_epochs, i + 1, total_step,
                             real_loss.data[0], fake_loss.data[0], g_loss.data[0]))

                # save the sampled images
                if (i + 1) % self.sample_step == 0:
                    fake_features = self.generator(fixed_noise, fixed_label)
                    torchvision.utils.save_image(self.denorm(fake_features.data),
                                                 os.path.join(self.sample_path,
                                                              'fake_samples-%d-%d.png' % (epoch + 1, i + 1)))

            # save the model parameters for each epoch
            if epoch % 10 == 0:
                g_path = os.path.join(self.model_path, 'generator-%d.pkl' % (epoch + 1))
                d_path = os.path.join(self.model_path, 'discriminator-%d.pkl' % (epoch + 1))
                torch.save(self.generator.state_dict(), g_path)
                torch.save(self.discriminator.state_dict(), d_path)

    def sample(self):
        import numpy as np
        # Load trained parameters 
        g_path = os.path.join(self.model_path, 'generator-%d.pkl' % (241))
        d_path = os.path.join(self.model_path, 'discriminator-%d.pkl' % (241))
        self.generator.load_state_dict(torch.load(g_path))
        self.discriminator.load_state_dict(torch.load(d_path))
        self.generator.eval()
        self.discriminator.eval()
        if not os.path.exists('./final'):
            os.makedirs('./final')

        labels = [[0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]]
        label = torch.from_numpy(np.array(labels)).float()
        noise = self.to_variable(torch.randn(1, self.z_dim))
        fake = self.generator(noise, label)
        for i, data in enumerate(fake):
            sample_path = os.path.join('./final', 'filter' + str(i) + '.png')
            data2 = data.data.cpu().numpy()
            print(np.shape(data2))
            a = np.shape(data2)[1]
            b = np.shape(data2)[2]
            print(a, b)
            data3 = np.zeros((a, 3, b, b))
            print(np.shape(data3))
            for j in range(a):
                data3[j] = [data2[0][j], data2[0][j], data2[0][j]]
            print(np.shape(data3))
            import math
            torchvision.utils.save_image(torch.from_numpy(data3), sample_path, nrow=int(math.sqrt(a)), pad_value=1)

        '''
        labels = [[0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]]
        label = torch.from_numpy(np.array(labels)).float()

        labels_full = list()
        for i in range(0, 6):
            for j in range(0, 6):
                class_label_1 = 1.0 - (j / 6.0)
                class_label_2 = (j / 6.0)
                rarity_label_1 = 1.0 - (i / 6.0)
                rarity_label_2 = (i / 6.0)
                labels = [rarity_label_1, 0, 0, 0, rarity_label_2, 0, 0, 0, 0, 0, class_label_1, 0, class_label_2, 0, 0]
                labels_full.append(labels)
                # label = torch.from_numpy(np.array(labels)).float()

        labels_full_torch = torch.from_numpy(np.array(labels_full)).float()
        noise = self.to_variable(torch.randn(36, self.z_dim))
        fake_images = self.generator(noise, labels_full_torch)
        sample_path = os.path.join('./final', 'common_to_legendary_priest_to_shaman' + '.png')
        torchvision.utils.save_image(self.denorm_2(fake_images.data), sample_path, nrow=6)

        for i in range(10):
            noise = self.to_variable(torch.randn(1, self.z_dim))
            fake_images = self.generator(noise, label)
            sample_path = os.path.join('./final', 'fake_priest_legendary' + str(i) + '.png')
            torchvision.utils.save_image(self.denorm_2(fake_images.data), sample_path, nrow=1)

        label = torch.from_numpy(np.random.uniform(size=(100, 15))).float()
        noise = self.to_variable(torch.randn(100, self.z_dim))
        fake_images = self.generator(noise, label)
        sample_path = os.path.join('./final', 'random' + '.png')
        torchvision.utils.save_image(self.denorm_2(fake_images.data), sample_path, nrow=10)

        labels = [[0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0]]
        label = torch.from_numpy(np.array(labels)).float()
        for i in range(10):
            noise = self.to_variable(torch.randn(1, self.z_dim))
            fake_images = self.generator(noise, label)
            sample_path = os.path.join('./final', 'pal_pr_comm_legen' + str(i) + '.png')
            torchvision.utils.save_image(self.denorm_2(fake_images.data), sample_path, nrow=1)

        label_grad = []
        for j in range(0, 10):
            rarity_label_1 = 1.0 - (j / 10.0)
            rarity_label_2 = (j / 10.0)
            labels = [0, 0, 0, 0, 1, rarity_label_1, rarity_label_2, 0, 0, 0, 0, 0, 0, 0, 0]
            label_grad.append(labels)

        for j in range(0, 10):
            rarity_label_1 = 1.0 - (j / 10.0)
            rarity_label_2 = (j / 10.0)
            labels = [0, 0, 0, 0, 1, rarity_label_1, 0, rarity_label_2, 0, 0, 0, 0, 0, 0, 0]
            label_grad.append(labels)
        for j in range(0, 10):
            rarity_label_1 = 1.0 - (j / 10.0)
            rarity_label_2 = (j / 10.0)
            labels = [0, 0, 0, 0, 1, rarity_label_1, 0,0,rarity_label_2, 0, 0, 0, 0, 0, 0]
            label_grad.append(labels)

        for j in range(0, 10):
            rarity_label_1 = 1.0 - (j / 10.0)
            rarity_label_2 = (j / 10.0)
            labels = [0, 0, 0, 0, 1, rarity_label_1, 0,0,0,rarity_label_2, 0, 0, 0, 0, 0]
            label_grad.append(labels)

        for j in range(0, 10):
            rarity_label_1 = 1.0 - (j / 10.0)
            rarity_label_2 = (j / 10.0)
            labels = [0, 0, 0, 0, 1, rarity_label_1, 0,0,0,0,rarity_label_2, 0, 0, 0, 0]
            label_grad.append(labels)
        for j in range(0, 10):
            rarity_label_1 = 1.0 - (j / 10.0)
            rarity_label_2 = (j / 10.0)
            labels = [0, 0, 0, 0, 1, rarity_label_1, 0,0,0,0,0,rarity_label_2, 0, 0, 0]
            label_grad.append(labels)
        for j in range(0, 10):
            rarity_label_1 = 1.0 - (j / 10.0)
            rarity_label_2 = (j / 10.0)
            labels = [0, 0, 0, 0, 1, rarity_label_1, 0,0,0,0,0,0,rarity_label_2, 0, 0]
            label_grad.append(labels)
        for j in range(0, 10):
            rarity_label_1 = 1.0 - (j / 10.0)
            rarity_label_2 = (j / 10.0)
            labels = [0, 0, 0, 0, 1, rarity_label_1, 0,0,0,0,0,0,0,rarity_label_2, 0]
            label_grad.append(labels)
        for j in range(0, 10):
            rarity_label_1 = 1.0 - (j / 10.0)
            rarity_label_2 = (j / 10.0)
            labels = [0, 0, 0, 0, 1, rarity_label_1, 0,0,0,0,0,0,0,0,rarity_label_2]
            label_grad.append(labels)

        label = torch.from_numpy(np.array(label_grad)).float()
        noise = self.to_variable(torch.randn(90, self.z_dim))
        fake_images = self.generator(noise, label)
        sample_path = os.path.join('./final', 'big_grad' + '.png')
        torchvision.utils.save_image(self.denorm_2(fake_images.data), sample_path, nrow=10)
        '''

        '''
        # Sample the images
        for i in range(self.sample_size):
            noise = self.to_variable(torch.randn(1, self.z_dim))
            label = self.to_variable(torch.ones(1, 15))
            fake_images = self.generator(noise, label)
            sample_path = os.path.join('./final', 'fake_samples-final' + str(i) + '.png')
            torchvision.utils.save_image(self.denorm(fake_images.data), sample_path, nrow=1)

        for i in range(10):
            noise = self.to_variable(torch.randn(self.sample_size, self.z_dim))
            label = self.to_variable(torch.ones(self.sample_size, 15))
            fake_images = self.generator(noise, label)
            sample_path = os.path.join('./final', 'fake_samples-final-full' + str(i) + '.png')
            torchvision.utils.save_image(self.denorm(fake_images.data), sample_path, nrow=10)
        '''
        print("Saved sampled images to '%s'" % 'asas')
