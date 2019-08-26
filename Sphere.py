# coding: utf-8
import rhinoscriptsyntax as rs
import math
import scriptcontext
import Rhino.Geometry
import Space
import System.Guid, System.Array, System.Enum


class Sphere:
    def __init__(self, original_id, inner_id, outer_ids, neighbor_ids, gl_flag, center_coordinate, radius):
        self.original_id = original_id    # 球体独自のID番号
        self.inner_id = inner_id          # オリジナル球体が所属する内部球のID --> original_id == 外部球の場合
        self.outer_ids = outer_ids        # オリジナル球体が保持する外部球のID --> original_id == 内部球の場合
        self.neighbor_ids_packing = neighbor_ids  # 球の隣接関係を保持、これにより、球体パッキングを行う。
        self.neighbor_ids = []

        self.sphere = None  # 球のオブジェト　Rhino.Geometry.Sphereを保持。
        self.center_coordinate = center_coordinate  # 球の中心座標  Rhino.Geometry.Point3d
        self.outer_space_flag = False  # 自身が外部球で有るかどうかのフラグ
        self.radius = radius  # 球の半径
        self.fixed_flag = False  # 固定する球かどうかのフラグ。
        self.gl_flag = gl_flag  # GLに接する球かのフラグ
        self.under_gl_sphere = False  # GLを作成するための球かどうか
        self.gl_sphere_partner_id = None  # GLを作成する球ならば、相手のIDを保持させる。
        self.already_make_face_flag = False
        self.prev_obj = None  # sphere Packing の際に使用する
        # self.space_instance = Space.Space()  # Spaceクラスを関連付ける。

        # Add by 関口
        self.voronoi_edge = []
        self.delaunay_lines = []
        

    def switch_outer_flag_true(self):
        self.outer_space_flag = True

    def switch_outer_flag_false(self):
        self.outer_space_flag = False

    def switch_fixed_flag_true(self):
        self.fixed_flag = True

    def switch_fixed_flag_false(self):
        self.fixed_flag = False

    def set_gl_sphere(self, partner_id):
        '''GLを作成するために特殊な動きをさせる球体を作成するメソッド'''
        self.gl_sphere_partner_id = partner_id
        self.under_gl_sphere = True

    def draw_sphere(self, outer_sphere, parent):
        sphere = rs.AddSphere(self.center_coordinate, self.radius)

        # Layer割り当て
        if outer_sphere:
            set_layer(sphere, "outer_sphere", 0, 0, 0, parent, False)
        else:
            set_layer(sphere, "inner_sphere", 255, 0, 0, parent, False)

    def draw_delaunay_line(self, parent):
        for line in self.delaunay_lines:
            layer_name = "Center Point" + str(self.original_id)
            set_layer(line, layer_name, 0, 0, 0, parent)

    def cul_move_vector(self, other_sphere_list):
        """
        引力と斥力の設計が謎。
        :return vector, Boolean(動かすかそうでないか？)
        """

        # fixed_flagがTrueの場合は動かさない。 --> 内部球体である場合
        if self.fixed_flag is True:
            composited_vector = None
            return composited_vector, False

        vectors = []
        for other_sphere in other_sphere_list:
            # 選択した球体 == other_sphere(選択した球体)である場合
            if self == other_sphere:
                continue

            # 両者の半径を比較し、ベクトルの方向を決定する。引力か斥力か。
            if (other_sphere.radius + self.radius) >= distance(self.center_coordinate, other_sphere.center_coordinate):
                # 斥力
                vector = [(self.center_coordinate[0] - other_sphere.center_coordinate[0]),
                          (self.center_coordinate[1] - other_sphere.center_coordinate[1]),
                          (self.center_coordinate[2] - other_sphere.center_coordinate[2])]

                vector = vector_scale(vector, 2)
                vectors.append(vector)

            else:
                # 隣接関係をもつ個体の間のみ引力を働かさせる
                if other_sphere.original_id is None:
                    pass
                else:
                    if other_sphere.original_id in self.neighbor_ids_packing:
                        # 引力
                        vector = [(other_sphere.center_coordinate[0] - self.center_coordinate[0]),
                                  (other_sphere.center_coordinate[1] - self.center_coordinate[1]),
                                  (other_sphere.center_coordinate[2] - self.center_coordinate[2])]

                        vectors.append(vector)

        # self.sphereとother_sphereとの相対ベクトルをすべて合成する。
        composited_vector = vector_composite(vectors)

        # 合成ベクトルが0ならば、自身は動かさない。
        # if vector_composite[0] == 0 and vector_composite[1] == 0 and vector_composite[2] == 0:
        if rs.VectorLength(composited_vector) == 0:
            return composited_vector, False
        else:
            return vector_unit(composited_vector), True

    def move_center_point(self, move_vector):
        """ベクトルの移動"""

        self.center_coordinate[0] = self.center_coordinate[0] + move_vector[0]
        self.center_coordinate[1] = self.center_coordinate[1] + move_vector[1]
        self.center_coordinate[2] = self.center_coordinate[2] + move_vector[2]

    def update_center_coordinate(self, move_vector):
        """前のオブジェクトを削除し、合成ベクトルを使用し、中心座標位置を更新。後に描画する。"""

        # if self.prev_obj is None:
        #     pass
        # else:
        #     # rs.DeleteObject(self.prev_obj)
        #     pass

        # 球体の中心点の更新
        self.move_center_point(move_vector)

        # 球体(RhinoGeometry)をモデル空間上に生成する --> draw
        # sphere = Rhino.Geometry.Sphere(self.center_coordinate, self.radius)
        # self.prev_obj = scriptcontext.doc.Objects.AddSphere(sphere)

    def construct_face(self):  # TODO  重なりが生まれてしまうので調整が必要。
        # lineを二重に複製
        temp_line_obj_list = []
        temp_line_obj_list.extend(self.space_instance.space_outlines)
        temp_line_obj_list.extend(self.space_instance.space_outlines)

        face_lines = []
        for i in range(len(temp_line_obj_list)):

            if len(temp_line_obj_list) == 0:
                break

            standard_line = temp_line_obj_list[0]

            temp_face_lines = []
            temp_face_lines.append(standard_line)
            temp_face_index = []
            temp_face_index.append(0)

            space_line_1 = standard_line

            avoid_infinite_loop = 0
            count = 0
            while True:
                avoid_infinite_loop += 1
                if avoid_infinite_loop > 200:
                    # raise Exception('infinite loop')
                    break

                if len(temp_face_lines) <= 2:
                    pass
                else:
                    first_line = temp_face_lines[0]
                    check_line = temp_face_lines[-1]

                    if first_line.PointAt(0) == check_line.PointAt(0) or first_line.PointAt(0) == check_line.PointAt(1) or \
                            first_line.PointAt(1) == check_line.PointAt(0) or first_line.PointAt(1) == check_line.PointAt(1):
                        break

                if len(temp_line_obj_list) <= count:
                    count = 0

                space_line_2 = temp_line_obj_list[count]

                # 同じラインの場合。
                if space_line_2.PointAt(0) == space_line_1.PointAt(0) and space_line_2.PointAt(1) == space_line_1.PointAt(1):
                    count += 1
                    continue

                # 端点のどっちかが一致していた場合。
                if space_line_1.PointAt(0) == space_line_2.PointAt(0) or space_line_1.PointAt(0) == space_line_2.PointAt(1) or \
                    space_line_1.PointAt(1) == space_line_2.PointAt(0) or space_line_1.PointAt(1) == space_line_2.PointAt(1):

                    # リスト内にすでにappendされていないか確認。
                    list_in_flag = False
                    for line in temp_face_lines:
                        if line.PointAt(0) == space_line_2.PointAt(0) and line.PointAt(1) == space_line_2.PointAt(1):
                            list_in_flag = True
                            break

                    # すでに指定されていた場合、スキップ
                    if list_in_flag is True:
                        count += 1
                        continue

                    # 初期は外積に関係なくappend
                    if len(temp_face_lines) == 1:
                        temp_face_lines.append(space_line_2)

                        space_line_1 = space_line_2
                        temp_face_index.append(count)

                        # print('temp_origin_line', space_line_1)
                        count += 1
                        continue

                    # ベクトル作成
                    vec1 = temp_face_lines[0].PointAt(0) - temp_face_lines[0].PointAt(1)
                    vec2 = temp_face_lines[1].PointAt(0) - temp_face_lines[1].PointAt(1)
                    vec3 = space_line_2.PointAt(0) - space_line_2.PointAt(1)

                    # 外積計算
                    cross_vec1 = Rhino.Geometry.Vector3d.CrossProduct(vec1, vec2)
                    cross_vec2 = Rhino.Geometry.Vector3d.CrossProduct(vec1, vec3)

                    # 単位ベクトルに変換
                    cross_vec1.Unitize()
                    cross_vec2.Unitize()

                    # ふたつの外積から計算されたベクトルを比較。
                    # print('cross_vec1', round(cross_vec1[0], 4))
                    # print('cross_vec2', round(cross_vec2[0], 4))

                    if round(cross_vec1[0], 4) == round(cross_vec2[0], 4):
                        temp_face_lines.append(space_line_2)
                        space_line_1 = space_line_2
                        temp_face_index.append(count)

                        count += 1
                        # print('cross append1')
                        continue

                    cross_vec2.Reverse()
                    # print('cross_vec3', cross_vec1[0])
                    # print('cross_vec4', cross_vec2[0])
                    if round(cross_vec1[0], 4) == round(cross_vec2[0], 4):
                        temp_face_lines.append(space_line_2)
                        space_line_1 = space_line_2
                        temp_face_index.append(count)

                        count += 1
                        # print('cross append2')
                        continue

                count += 1

            face_lines.append(temp_face_lines)
            # temp_line_obj_listからdelする。
            temp_face_index.sort()
            for count, del_index in enumerate(temp_face_index):
                del temp_line_obj_list[del_index - count]

                # # temp_line_obj_listの中身がなくなった場合、終了。
                # if len(temp_line_obj_list) == 0:
                #     break

        self.already_make_face_flag = True
        self.space_instance.space_edges.extend(face_lines)

    def judge_point_inside_voronoi_area(self, point):
        # strictly_in = False
        # tolerance = Rhino.RhinoMath.SqrtEpsilon
        # p = rs.coerce3dpoint(point, True)
        #
        # brep.IsPointInside(p, tolerance, strictly_in)
        knotstyle = 0
        degree = 3

        # p1 = Rhino.Geometry.Point3d(self.center_coordinate[0], self.center_coordinate[1], self.center_coordinate[2])
        p1 = point
        p2 = Rhino.Geometry.Point3d(self.center_coordinate[0] + 5000000, self.center_coordinate[1] + 5000000, self.center_coordinate[2] + 5000000)
        points = [p1, p2]

        # interpolate Curveを作成。Lineで作成したいが、LineにはBrepとのIntersectが存在しないため。
        start_tangent = Rhino.Geometry.Vector3d.Unset
        end_tangent = Rhino.Geometry.Vector3d.Unset
        knotstyle = System.Enum.ToObject(Rhino.Geometry.CurveKnotStyle, knotstyle)
        curve = Rhino.Geometry.Curve.CreateInterpolatedCurve(points, degree, knotstyle, start_tangent, end_tangent)

        # scriptcontext.doc.Objects.AddCurve(curve)

        # 直線とボロノイの面がインターセクトしているか確認。
        intersect_point = []
        for brep in self.space_instance.space_faces:
            tolerance = scriptcontext.doc.ModelAbsoluteTolerance
            rc, out_curves, out_points = Rhino.Geometry.Intersect.Intersection.CurveBrep(curve, brep, tolerance)

            for point in out_points:
                if point and point.IsValid:
                    intersect_point.append(point)
                    # rc = scriptcontext.doc.Objects.AddPoint(point)

        # インターセクトの回数で内部か外部を判定。
        if len(intersect_point) == 1:
            return True
        elif len(intersect_point) == 2 or len(intersect_point) == 0:
            return False
        else:
            raise Exception('Error')

# Global Method
def set_layer(obj, name, r, g, b, parent, visible=True):
    if not rs.IsLayer(name):
        layer = rs.AddLayer(name, [r, g, b], visible, False, parent)
    else:
        layer = rs.LayerId(name)
        if not layer:
            layer = rs.AddLayer(name, [r, g, b], visible, False, parent)

    # オブジェクトをライヤーに割り当て
    rs.ObjectLayer(obj, layer)

def distance(p1, p2):
    """ユークリッド距離計算"""
    distance = math.sqrt(pow((p1[0] - p2[0]), 2) + pow((p1[1] - p2[1]), 2) + pow((p1[2] - p2[2]), 2))

    distance = abs(distance)

    return distance

def vector_scale(vector, value):
    return [vector[0] * value, vector[1] * value, vector[2] * value]

def vector_composite(vectors):
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

def vector_unit(vector):
    """単位ベクトル計算"""
    vector_length = abs(math.sqrt(pow(vector[0], 2) + pow(vector[1], 2) + pow(vector[2], 2)))
    vector_unit = [vector[0] / vector_length, vector[1] / vector_length, vector[2] / vector_length]
    return vector_unit