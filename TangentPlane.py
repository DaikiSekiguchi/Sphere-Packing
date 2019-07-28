# coding:utf-8

import Rhino.Geometry
import scriptcontext
import math
import rhinoscriptsyntax as rs


def coordinate_transform(coordinate, origin_point, theta):
    '''二次元の回転移動'''
    x = coordinate[0] - origin_point[0]
    y = coordinate[1] - origin_point[1]

    theta = math.radians(theta)

    destination_x = (x * math.cos(theta)) - (y * math.sin(theta))
    destination_y = (x * math.sin(theta)) + (y * math.cos(theta))

    destination_x = destination_x + origin_point[0]
    destination_y = destination_y + origin_point[1]

    return [destination_x, destination_y, coordinate[2]]


def coordinate_transform_3d(coordinate, origin_point, theta, rotate_axis):
    '''３次元の回転運動'''
    point = Rhino.Geometry.Point3d(coordinate[0], coordinate[1], coordinate[2])
    origin_point = Rhino.Geometry.Point3d(origin_point[0], origin_point[1], origin_point[2])

    radian = math.radians(theta)

    xf = Rhino.Geometry.Transform.Rotation(radian, rotate_axis, origin_point)
    point.Transform(xf)

    return point


def extend_point(p1, p2, value):
    '''与えられた２点を両方向に延長させる'''
    vec_1 = p2 - p1
    vec_2 = p1 - p2
    new_vec_1 = [vec_1[0]*value, vec_1[1]*value, vec_1[2]*value]
    new_vec_2 = [vec_2[0]*value, vec_2[1]*value, vec_2[2]*value]

    new_p1 = [p1[0] + new_vec_1[0], p1[1] + new_vec_1[1], p1[2] + new_vec_1[2]]
    new_p2 = [p2[0] + new_vec_2[0], p2[1] + new_vec_2[1], p2[2] + new_vec_2[2]]

    return new_p1, new_p2


def change_rhino_point(point):
    point = Rhino.Geometry.Point3d(point[0], point[1], point[2])

    return point


def line_center(line):
    '''直線の中点を求める'''
    p1 = line[0]
    p2 = line[1]

    add_x = (p2[0] - p1[0]) / 2
    add_y = (p2[1] - p1[1]) / 2
    add_z = (p2[2] - p1[2]) / 2

    center_p = [p1[0] + add_x, p1[1] + add_y, p1[2] + add_z]

    return center_p


def area_point(lines):
    '''多角形のエリア内の点をリターンする'''
    center_p = line_center(lines[0])
    p1 = lines[2][0]

    # rs.AddPoint(center_p[0], center_p[1], center_p[2])
    new_line = [center_p, p1]
    area_point = line_center(new_line)

    return area_point


def intersection(crv1, crv2):

    # 傾きが０の場合分岐が必要。
    flag_x_1 = False
    flag_x_2 = False
    if (crv1[1][0] - crv1[0][0]) == 0:
        x_1 = crv1[0][0]
        x_2 = crv1[1][0]

        if crv1[0][1] > crv1[1][1]:
            y_1 = crv1[1][1]
            y_2 = crv1[0][1]
        else:
            y_1 = crv1[0][1]
            y_2 = crv1[1][1]

        a_1 = 0
        b_1 = 0

        flag_x_1 = True

    else:
        a_1 = (crv1[1][1] - crv1[0][1]) / (crv1[1][0] - crv1[0][0])  # 傾き
        b_1 = ((crv1[0][1] * crv1[1][0]) - (crv1[1][1] * crv1[0][0])) / (crv1[1][0] - crv1[0][0])

        if crv1[0][0] > crv1[1][0]:
            x_1 = crv1[1][0]
            x_2 = crv1[0][0]
        else:
            x_1 = crv1[0][0]
            x_2 = crv1[1][0]

        if crv1[0][1] > crv1[1][1]:
            y_1 = crv1[1][1]
            y_2 = crv1[0][1]
        else:
            y_1 = crv1[0][1]
            y_2 = crv1[1][1]

    if (crv2[1][0] - crv2[0][0]) == 0:
        x_3 = crv2[0][0]
        x_4 = crv2[1][0]

        if crv2[0][1] > crv2[1][1]:
            y_3 = crv2[1][1]
            y_4 = crv2[0][1]
        else:
            y_3 = crv2[0][1]
            y_4 = crv2[1][1]

        a_2 = 0
        b_2 = 0

        flag_x_2 = True

    else:

        a_2 = (crv2[1][1] - crv2[0][1]) / (crv2[1][0] - crv2[0][0])
        b_2 = ((crv2[0][1] * crv2[1][0]) - (crv2[1][1] * crv2[0][0])) / (crv2[1][0] - crv2[0][0])

        if crv2[0][0] > crv2[1][0]:
            x_3 = crv2[1][0]
            x_4 = crv2[0][0]
        else:
            x_3 = crv2[0][0]
            x_4 = crv2[1][0]

        if crv2[0][1] > crv2[1][1]:
            y_3 = crv2[1][1]
            y_4 = crv2[0][1]
        else:
            y_3 = crv2[0][1]
            y_4 = crv2[1][1]

    if flag_x_1 is True:
        intersect_point_x = x_1
    elif flag_x_2 is True:
        intersect_point_x = x_3
    else:
        intersect_point_x = (b_2 - b_1) / (a_1 - a_2)

    intersect_point_y = ((a_1 * b_2) - (a_2 * b_1)) / (a_1 - a_2)

    intersection_flag = False
    intersect_flag_count = 0
    if (x_1 <= intersect_point_x) and (intersect_point_x <= x_2):
        intersect_flag_count += 1

    if (x_3 <= intersect_point_x) and (intersect_point_x <= x_4):
        intersect_flag_count += 1

    if (y_1 <= intersect_point_y) and (intersect_point_y <= y_2):
        intersect_flag_count += 1

    if (y_3 <= intersect_point_y) and (intersect_point_y <= y_4):
        intersect_flag_count += 1

    if intersect_flag_count == 4:
        intersection_flag = True
        intersection_point = [intersect_point_x, intersect_point_y, 0]
    else:
        intersection_point = []

    return intersection_flag, intersection_point


def rotate_surface_to_sphere(sphere, surface, rotate_axis, rotate_point):
    '''球とサーフェスを接させる。'''
    tolerance = 0.0
    # brep1 = rs.coercebrep(surface, True)
    # sphere = rs.coercebrep(sphere, True)
    sphere = sphere.ToBrep()
    surface = surface.ToBrep()

    while True:
        # rotate_axisを中心にsurfaceを回転させる。

        rotate_angle = math.radians(2)
        xf = Rhino.Geometry.Transform.Rotation(rotate_angle, rotate_axis, rotate_point)
        surface.Transform(xf)

        rc = Rhino.Geometry.Intersect.Intersection.BrepBrep(surface, sphere, tolerance)

        print(rc)

        if len(rc[1]) == 0:
            continue
        elif not len(rc[1]) == 0:
            break
        else:
            raise Exception('Error')

    return surface


def add_surface_from_edge(edge_line, other_edge_line, voronoi_face):
    # Tangent Plane メインアルゴリズム
    new_p1, new_p2 = extend_point(edge_line[0], edge_line[1], 2)

    if other_edge_line[0] == edge_line[1] or other_edge_line[0] == edge_line[0]:
        other_p = other_edge_line[1]
    else:
        other_p = other_edge_line[0]

    # 外積計算をおこない回転ベクトルを取得する。
    vec_1 = edge_line[1] - edge_line[0]
    vec_2 = other_p - edge_line[0]

    rotate_axis = Rhino.Geometry.Vector3d.CrossProduct(vec_1, vec_2)

    # ボロノイ面の中心点を利用intersectionで90度か－90度か決定する。
    rotate_angle = 90

    # ボロノイの中心点計算
    area_center = area_point(voronoi_face)

    new_p3 = coordinate_transform_3d(new_p1, new_p2, rotate_angle, rotate_axis)

    flag = intersection([new_p1, new_p2], [area_center, new_p3])
    if flag[0] is True:
        pass
    elif flag[0] is False:
        new_p3 = coordinate_transform_3d(new_p1, new_p2, -rotate_angle, rotate_axis)
    else:
        raise Exception('Error')

    new_p4 = coordinate_transform_3d(new_p2, new_p1, rotate_angle, rotate_axis)
    flag = intersection([new_p1, new_p2], [area_center, new_p4])
    if flag[0] is True:
        pass
    elif flag[0] is False:
        new_p4 = coordinate_transform_3d(new_p2, new_p1, -rotate_angle, rotate_axis)
    else:
        raise Exception('Error')

    new_p1 = Rhino.Geometry.Point3d(new_p1[0], new_p1[1], new_p1[2])
    new_p2 = Rhino.Geometry.Point3d(new_p2[0], new_p2[1], new_p2[2])
    new_p3 = Rhino.Geometry.Point3d(new_p3[0], new_p3[1], new_p3[2])
    new_p4 = Rhino.Geometry.Point3d(new_p4[0], new_p4[1], new_p4[2])

    rotate_axis = new_p2 - new_p1
    rotate_point = new_p1

    surface = Rhino.Geometry.NurbsSurface.CreateFromCorners(new_p1, new_p2, new_p3, new_p4)
    scriptcontext.doc.Objects.AddSurface(surface)

    surface = rotate_surface_to_sphere(sphere, surface, rotate_axis, rotate_point)
    scriptcontext.doc.Objects.AddBrep(surface)

    return surface


# 基本的には既存ボロノイの一面と球を入力
# 作成されたサーフェスをリターン

p1 = [0, 0, -30]
p2 = [100, 50, 0]
p3 = [0, 100, 20]

p1 = Rhino.Geometry.Point3d(p1[0], p1[1], p1[2])
p2 = Rhino.Geometry.Point3d(p2[0], p2[1], p2[2])
p3 = Rhino.Geometry.Point3d(p3[0], p3[1], p3[2])


line1 = Rhino.Geometry.Line(p1[0], p1[1], p1[2], p2[0], p2[1], p2[2])
line2 = Rhino.Geometry.Line(p2[0], p2[1], p2[2], p3[0], p3[1], p3[2])
line3 = Rhino.Geometry.Line(p3[0], p3[1], p3[2], p1[0], p1[1], p1[2])

voronoi_face = [line1, line2, line3]

scriptcontext.doc.Objects.AddLine(line1)
scriptcontext.doc.Objects.AddLine(line2)
scriptcontext.doc.Objects.AddLine(line3)

center = Rhino.Geometry.Point3d(50, 50, 50)
radius = 50
sphere = Rhino.Geometry.Sphere(center, 50)

scriptcontext.doc.Objects.AddSphere(sphere)

surface1 = add_surface_from_edge(line1, line2, voronoi_face)
surface2 = add_surface_from_edge(line2, line3, voronoi_face)
surface3 = add_surface_from_edge(line3, line1, voronoi_face)

# このリスト内にボロノイで作成されるサーフェスも入れ込むと良い。多分。
surface_lists = [surface1, surface2, surface3]
