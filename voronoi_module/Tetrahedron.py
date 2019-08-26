# coding: utf-8
import math
import scriptcontext
import Rhino.Geometry
import rhinoscriptsyntax as rs

class Tetrahedron:

    def __init__(self, p1, p2, p3, p4):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.radius = None  # 外接球の半径
        self.center_p = None  # 外接球の中心
        self.edge_lines = []

        # Add by 関口
        self.delaunay_lines = []


    # Class Method
    def cul_center_p_and_radius(self):  # 垂直方向に母点が並んでしまうとaの値が０になり計算できなくなってしまう。多少のノイズが必要
        """外接球の中心点と半径を計算"""

        a = [
            [self.p1.x, self.p1.y, self.p1.z, 1],
            [self.p2.x, self.p2.y, self.p2.z, 1],
            [self.p3.x, self.p3.y, self.p3.z, 1],
            [self.p4.x, self.p4.y, self.p4.z, 1]
        ]

        d_x = [
            [pow(self.p1.x, 2) + pow(self.p1.y, 2) + pow(self.p1.z, 2), self.p1.y, self.p1.z, 1],
            [pow(self.p2.x, 2) + pow(self.p2.y, 2) + pow(self.p2.z, 2), self.p2.y, self.p2.z, 1],
            [pow(self.p3.x, 2) + pow(self.p3.y, 2) + pow(self.p3.z, 2), self.p3.y, self.p3.z, 1],
            [pow(self.p4.x, 2) + pow(self.p4.y, 2) + pow(self.p4.z, 2), self.p4.y, self.p4.z, 1]
        ]

        d_y = [
            [pow(self.p1.x, 2) + pow(self.p1.y, 2) + pow(self.p1.z, 2), self.p1.x, self.p1.z, 1],
            [pow(self.p2.x, 2) + pow(self.p2.y, 2) + pow(self.p2.z, 2), self.p2.x, self.p2.z, 1],
            [pow(self.p3.x, 2) + pow(self.p3.y, 2) + pow(self.p3.z, 2), self.p3.x, self.p3.z, 1],
            [pow(self.p4.x, 2) + pow(self.p4.y, 2) + pow(self.p4.z, 2), self.p4.x, self.p4.z, 1]
        ]

        d_z = [
            [pow(self.p1.x, 2) + pow(self.p1.y, 2) + pow(self.p1.z, 2), self.p1.x, self.p1.y, 1],
            [pow(self.p2.x, 2) + pow(self.p2.y, 2) + pow(self.p2.z, 2), self.p2.x, self.p2.y, 1],
            [pow(self.p3.x, 2) + pow(self.p3.y, 2) + pow(self.p3.z, 2), self.p3.x, self.p3.y, 1],
            [pow(self.p4.x, 2) + pow(self.p4.y, 2) + pow(self.p4.z, 2), self.p4.x, self.p4.y, 1]
        ]

        a = dit_4(a)

        if a == 0:
            a = [
                [self.p1.x + 0.1, self.p1.y + 0.1, self.p1.z + 0.2, 1],
                [self.p2.x - 0.1, self.p2.y - 0.1, self.p2.z, 1],
                [self.p3.x + 0.2, self.p3.y + 0.2, self.p3.z, 1],
                [self.p4.x - 0.2, self.p4.y - 0.2, self.p4.z, 1]
            ]
            a = dit_4(a)

        d_x = dit_4(d_x)
        d_y = -(dit_4(d_y))
        d_z = dit_4(d_z)

        center_p_x = d_x / (2 * a)  # Message: Attempted to divide by zero.
        center_p_y = d_y / (2 * a)
        center_p_z = d_z / (2 * a)

        self.center_p = [float(center_p_x), float(center_p_y), float(center_p_z)]

        distance = math.sqrt(
            pow((self.p1.x - self.center_p[0]), 2) + pow((self.p1.y - self.center_p[1]), 2) + pow((self.p1.z - self.center_p[2]), 2))

        self.radius = float(distance)

    def draw_divide_tetrahedron(self, move_scale=0, index=0, parent_layer=None):
        """分割四面体をRhinoに描画するためのメソッド"""
        line1 = Rhino.Geometry.Line(self.p1.x, self.p1.y, self.p1.z, self.p2.x, self.p2.y, self.p2.z)
        line2 = Rhino.Geometry.Line(self.p1.x, self.p1.y, self.p1.z, self.p3.x, self.p3.y, self.p3.z)
        line3 = Rhino.Geometry.Line(self.p1.x, self.p1.y, self.p1.z, self.p4.x, self.p4.y, self.p4.z)
        line4 = Rhino.Geometry.Line(self.p2.x, self.p2.y, self.p2.z, self.p3.x, self.p3.y, self.p3.z)
        line5 = Rhino.Geometry.Line(self.p2.x, self.p2.y, self.p2.z, self.p4.x, self.p4.y, self.p4.z)
        line6 = Rhino.Geometry.Line(self.p3.x, self.p3.y, self.p3.z, self.p4.x, self.p4.y, self.p4.z)

        # Rhino空間上に描画
        # line1 = scriptcontext.doc.Objects.AddLine(line1)
        # line2 = scriptcontext.doc.Objects.AddLine(line2)
        # line3 = scriptcontext.doc.Objects.AddLine(line3)
        # line4 = scriptcontext.doc.Objects.AddLine(line4)
        # line5 = scriptcontext.doc.Objects.AddLine(line5)
        # line6 = scriptcontext.doc.Objects.AddLine(line6)

        self.edge_lines.append(line1)
        self.edge_lines.append(line2)
        self.edge_lines.append(line3)
        self.edge_lines.append(line4)
        self.edge_lines.append(line5)
        self.edge_lines.append(line6)

        # debug
        # Layer分け
        # for i, edge in enumerate(self.edge_lines):
        #     # debug
        #     move_obj(edge, move_scale)
        #
        #     # layer
        #     layer_name = "tetra_edge" + str(index)
        #     set_layer(edge, layer_name, 0, 0, 0, parent_layer)

    def check_point_include_circumsphere(self, check_p):
        """外接球に任意の点が内包されているかどうか判定"""

        distance = math.sqrt(pow((check_p.x - self.center_p[0]), 2) + pow(
            (check_p.y - self.center_p[1]), 2) + pow((check_p.z - self.center_p[2]), 2))

        if distance < self.radius:
            return True
        else:
            return False

    def create_tetrahedron_face_from_edge_lines(self):
        pass

    def create_delaunay_line_from_sphere_point(self):
        pass

    def divide_layer(self, num):
        for edge in self.edge_lines:
            layer_name = "tetra_edge" + str(num)
            set_layer(edge, layer_name, 0, 255, 255)

    def draw_sphere(self, parent_layer=None):
        sphere = rs.AddSphere(self.center_p, self.radius)
        set_layer(sphere, "tetra_sphere", 128, 128, 0, parent_layer)

# Method
def dit_2(dit):
    '''二次元行列の計算'''
    cul = (dit[0][0] * dit[1][1]) - (dit[0][1] * dit[1][0])

    return cul

def dit_3(dit):
    '''三次行列の計算'''
    a = [
        [dit[1][1], dit[1][2]],
        [dit[2][1], dit[2][2]]
    ]

    b = [
        [dit[0][1], dit[0][2]],
        [dit[2][1], dit[2][2]]
    ]

    c = [
        [dit[0][1], dit[0][2]],
        [dit[1][1], dit[1][2]]
    ]

    cul = (dit[0][0] * dit_2(a)) - (dit[1][0] * dit_2(b)) + (dit[2][0] * dit_2(c))

    return cul

def dit_4(dit):
    '''4次元の行列'''
    a = [
        [dit[1][1], dit[1][2], dit[1][3]],
        [dit[2][1], dit[2][2], dit[2][3]],
        [dit[3][1], dit[3][2], dit[3][3]]
    ]

    b = [
        [dit[0][1], dit[0][2], dit[0][3]],
        [dit[2][1], dit[2][2], dit[2][3]],
        [dit[3][1], dit[3][2], dit[3][3]]
    ]

    c = [
        [dit[0][1], dit[0][2], dit[0][3]],
        [dit[1][1], dit[1][2], dit[1][3]],
        [dit[3][1], dit[3][2], dit[3][3]]
    ]

    d = [
        [dit[0][1], dit[0][2], dit[0][3]],
        [dit[1][1], dit[1][2], dit[1][3]],
        [dit[2][1], dit[2][2], dit[2][3]]
    ]

    cul = (dit[0][0] * dit_3(a)) - (dit[1][0] * dit_3(b)) + (dit[2][0] * dit_3(c)) - (dit[3][0] * dit_3(d))

    return cul

def set_layer(obj, name, r, g, b, parent_layer=None, visible=True):
    if not rs.IsLayer(name):
        layer = rs.AddLayer(name, [r, g, b], visible, False, parent_layer)
    else:
        layer = rs.LayerId(name)
        if not layer:
            layer = rs.AddLayer(name, [r, g, b], visible, False, parent_layer)

    # オブジェクトをライヤーに割り当て
    rs.ObjectLayer(obj, layer)

def move_obj(obj, scale):
    start = rs.CreateVector(0, 0, 0)
    end = rs.CreateVector(2000000 * scale, 0, 0)
    translation = end - start
    rs.MoveObject(obj, translation)