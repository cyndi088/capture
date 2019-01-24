# -*- coding: utf-8 -*-
import os

from PIL import Image


class CompareImage(object):

    def calculate(self, image1, image2):
        g = image1.histogram()
        s = image2.histogram()
        assert len(g) == len(s), "error"

        data = []

        for index in range(0, len(g)):
            if g[index] != s[index]:
                data.append(1 - abs(g[index] - s[index]) / max(g[index], s[index]))
            else:
                data.append(1)

        return sum(data) / len(g)

    def split_image(self, image, part_size):
        pw, ph = part_size
        w, h = image.size

        sub_image_list = []

        assert w % pw == h % ph == 0, "error"

        for i in range(0, w, pw):
            for j in range(0, h, ph):
                sub_image = image.crop((i, j, i + pw, j + ph)).copy()
                sub_image_list.append(sub_image)

        return sub_image_list

    def compare_image(self, file_image1, file_image2, size=(256, 256), part_size=(64, 64)):

        if os.path.getsize(file_image2) == 0:
            print('获得一个空文件!!!')
            return 1.0

        image1 = Image.open(file_image1)
        image2 = Image.open(file_image2)

        img1 = image1.resize(size).convert("RGB")
        sub_image1 = self.split_image(img1, part_size)

        img2 = image2.resize(size).convert("RGB")
        sub_image2 = self.split_image(img2, part_size)

        sub_data = 0
        for im1, im2 in zip(sub_image1, sub_image2):
            sub_data += self.calculate(im1, im2)

        x = size[0] / part_size[0]
        y = size[1] / part_size[1]

        pre = round((sub_data / (x * y)), 6)
        # print(str(pre * 100) + '%')
        # print('Compare the image result is: ' + str(pre))
        return pre

# compare_image = CompareImage()
# compare_image.compare_image("./img/15.jpg", "./img/16.jpg")
