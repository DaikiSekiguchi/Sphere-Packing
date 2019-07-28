# coding: utf-8
import math

def vector_cross(self, vector, value):
    return [vector[0] * value, vector[1] * value, vector[2] * value]

def vector_composite(self, vectors):
    """
    ベクトルを合成し合成ベクトルを計算する。
    :param vectors: ベクトルを格納しているリスト。
    :return: 合成ベクトル
    """
    vector_x = 0
    vector_y = 0
    vector_z = 0

    for vector in vectors:
        vector_x = vector_x + vector[0]
        vector_y = vector_y + vector[1]
        vector_z = vector_z + vector[2]

    return [vector_x, vector_y, vector_z]


def vector_unit(self, vector):
    """単位ベクトル計算"""
    vector_length = abs(math.sqrt(pow(vector[0], 2) + pow(vector[1], 2) + pow(vector[2], 2)))
    vector_unit = [vector[0] / vector_length, vector[1] / vector_length, vector[2] / vector_length]

    return vector_unit