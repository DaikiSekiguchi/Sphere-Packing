# coding: utf-8
import rhinoscriptsyntax as rs

class Point:
    def __init__(self, point):
        """

        :param point: [x, y,z]の配列情報を引数に指定
        """
        self.point = None  # objectだということか？
        self.x = point[0]
        self.y = point[1]
        self.z = point[2]
        self.coordinate = point

    def system_guid_obj_to_coordinate(self):
        """System.GuidObjectをRhino.Objectに変換。クラス変数に座標値を保持させる"""

        p = rs.coerce3dpoint(self.point)
        self.x = p[0]
        self.y = p[1]
        self.z = p[2]
        self.coordinate = [p[0], p[1], p[2]]

    def change_coordinate(self):
        """はじめの外接円を構成する点を変換するメソッド"""

        p = self.point  # [x, y, z]
        self.x = p[0]   # x
        self.y = p[1]   # y
        self.z = p[2]   # z
        self.coordinate = [p[0], p[1], p[2]]  # [x, y, z]
