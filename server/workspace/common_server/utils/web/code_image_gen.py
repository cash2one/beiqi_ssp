# coding=utf-8
"""
Created on '2015-10-12'

@author = Jay
"""
import random
import os
from PIL import Image, ImageFont, ImageDraw


FontWidth = 80
FontHeight = 120

def _random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

class _CodeImageFont(object):
    def __init__(self, char):
        self.image = Image.new('RGB', (FontWidth, FontHeight), color="#fff")
        cambria_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static', 'fonts', 'cambria.ttc')
        self.font = ImageFont.truetype(cambria_path, 80)
        ctx = ImageDraw.Draw(self.image)
        ctx.text((10, 0), char, fill="#000", font=self.font,)

class VerifyCode(object):
    def __init__(self, string, dot=0, line=0, line_length=0):
        """
        Verify_code generator Class
        :param string:
        :param dot:
        :param line:
        :param line_length:
        :return:
        """
        self._string = string
        self._length = len(self._string)
        self._clip = Image.new('RGB', (self._length*FontWidth, FontHeight), color="#fff")
        self.width = self._clip.size[0]
        self.height = self._clip.size[1]
        self._gen_code_image()
        if dot:
            self._gen_dot(dot)
        if line:
            self._gen_lines(line, line_length)

    def _gen_code_image(self):
        """
        generate code image
        :return:
        """
        temp = []
        for char in self._string:
            temp.append(_CodeImageFont(char))

        for index, _ in enumerate(self._string):
            box = (0+index*FontWidth, 0, FontWidth*(1+index), FontHeight)
            self._clip.paste(temp[index].image, box)

    def _random_line_points(self, num):
        """
        generate random line points
        :param num: points num
        :return:
        """
        points = []
        origin_x = random.randint(0, 100)
        origin_y = random.randint(self.height/10, self.height/10*9)
        origin = (origin_x, origin_y)
        points.append(origin)
        for _ in range(num):
            origin_x += random.randint(0, 5)
            origin_y += random.randint(-5, 5)
            if origin_x > self.width or origin_y > self.height:
                break
            origin = (origin_x, origin_y)
            points.append(origin)
        return points

    def _random_dot_points(self, num):
        """
        generate random dot points
        :param num: points num
        :return:
        """
        points = []
        for _ in range(num):
            point = (random.randint(0, self.width), random.randint(0, self.height))
            points.append(point)
        return points

    def _gen_lines(self, num, length):
        """
        generate image line
        :param num: line number
        :return:
        """
        ctx = ImageDraw.Draw(self._clip)
        for _ in range(num):
            ctx.line(self._random_line_points(length), fill=_random_color(), width=3)

    def _gen_dot(self, num):
        """
        generate image dot
        :param num: dot num
        :return:
        """
        ctx = ImageDraw.Draw(self._clip)
        ctx.point(self._random_dot_points(num), fill=_random_color())

    def get_clip(self):
        """
        :return: PIL.Image object (image code)
        """
        return self._clip

    def get_string(self):
        """
        :return: VerifyCode string
        """
        return self._string



