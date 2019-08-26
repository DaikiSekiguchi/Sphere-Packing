# coding: utf-8
import Rhino.Geometry
import scriptcontext
import rhinoscriptsyntax as rs
import Sphere
from voronoi_module import Point
from voronoi_module import Tetrahedron
import copy
import random

class Space:
    """Spaceクラスに空間にまつわる情報を格納する。ゆくゆくは木材情報なども？"""
    def __init__(self, id_number):
        self.area = None          # 体積を保持
        self.space_outlines = []  # 空間を形作る外形線を保持
        self.space_edges = []     # 空間の辺
        self.space_faces = []     # 空間の面

        # Add by 関口
        self.inner_sphere = None             # 自身の空間を構成するための球体
        self.sphere_outer_lists = []         # 相互関係を決定するための球体のリスト
        self.divide_tetrahedron_list = None  # 分割した四面体を格納するためのリスト
        self.neighbor_info = []              # 隣接関係
        self.points_list_from_sphere = []    # 自身の球体の中心点＋外部球体の中心点を含めた点リスト-->2次元配列
        self.space_id = id_number            # space空間のid番号

        self.previous_inner_sphere = None
        self.voronoi_point_list = []


    def create_spatial_domain_by_sphere(self):
        """自空間の領域を構成する球体の母点を生成、周辺に外部空間(外部とのつながり)の母点を生成"""
        global coordinate

        # 自空間がGLに設置するか否かを判定
        gl_flag = False
        gl_value = rs.GetInteger('Input 1(from GL) or 2(not from GL)')

        if gl_value == 1:
            gl_flag = True
        elif gl_value == 2:
            pass
        else:
            raise Exception('not intended num selected, please retry')

        # 自空間の大まかな領域を構成する球体の半径を決定
        radius = rs.GetInteger('Enter the radius of sphere to create space')  # sphere of radius

        # ユーザによる空間領域の位置を母点(球体)の取得によって決定 --> 重要
        coordinate = Rhino.Geometry.Point3d(0, 0, 1000)
        # sphere_center_coordinate = rs.GetPointCoordinates()  # TODO ゆくゆくは自動生成にしたい
        # coordinate = sphere_center_coordinate[0]  # [int, int ,int]の値を取得。あとで改善

        # 自身の空間を構成する球体のID番号
        inner_id = self.space_id

        # 他の空間領域との相互関係を決定するための外部球体を生成 --> この外部球が次の空間につながる
        temp_coordinate_list = []
        coordinate_1 = Rhino.Geometry.Point3d(coordinate[0] + 90, coordinate[1] + 20, coordinate[2])
        coordinate_2 = Rhino.Geometry.Point3d(coordinate[0] - 100, coordinate[1] - 5, coordinate[2])
        coordinate_3 = Rhino.Geometry.Point3d(coordinate[0] + 1, coordinate[1] + 90, coordinate[2])
        coordinate_4 = Rhino.Geometry.Point3d(coordinate[0] - 1, coordinate[1] - 100, coordinate[2])
        coordinate_5 = Rhino.Geometry.Point3d(coordinate[0] - 2, coordinate[1] - 1, coordinate[2] + 100)
        coordinate_6 = Rhino.Geometry.Point3d(coordinate[0] + 3, coordinate[1] + 10, coordinate[2] - 100)
        coordinate_7 = Rhino.Geometry.Point3d(coordinate[0] + 50, coordinate[1] + 10, coordinate[2] + 50)

        temp_coordinate_list.append(coordinate_1)
        temp_coordinate_list.append(coordinate_2)
        temp_coordinate_list.append(coordinate_3)
        temp_coordinate_list.append(coordinate_4)
        temp_coordinate_list.append(coordinate_5)
        temp_coordinate_list.append(coordinate_6)
        temp_coordinate_list.append(coordinate_7)

        # 隣接関係を示すリストを作成 --> 内部球からみた外部球のID
        neighbor_ids = []
        for i in range(len(temp_coordinate_list)):     # 外部球のID
            outer_id = str(inner_id) + '-' + str(i+1)    # outer_id_name = space_id_outer_num --> ex. 1_1
            neighbor_ids.append(outer_id)

        # 空間領域を決定するための内部球を生成(インスタンス)
        original_id = inner_id
        outer_ids = neighbor_ids
        self.inner_sphere = Sphere.Sphere(original_id, inner_id, outer_ids, neighbor_ids, gl_flag, coordinate, radius)

        # 外部球を生成(インスタンス)
        temp_neighbor_ids = []
        for i in range(len(temp_coordinate_list)):
            original_id = neighbor_ids[i]
            outer_ids = []
            radius = radius + random.randint(-50, 50)    # radius TODO 変更の余地あり
            temp_neighbor_ids = [inner_id]    # 外部球は内部球とのみ隣接関係をもつように設定 TODO 変更の余地あり
            gl_flag = False

            outer_sphere = Sphere.Sphere(original_id, inner_id, outer_ids, temp_neighbor_ids,
                                         gl_flag, temp_coordinate_list[i], radius)

            self.sphere_outer_lists.append(outer_sphere)

        # 不必要なオブジェクトを削除
        del temp_coordinate_list
        del temp_neighbor_ids

    def create_spatial_domain_by_previous_info(self, new_inner_sphere, new_outer_sphere):
        global coordinate

        # 自空間がGLに設置するか否かを判定
        gl_flag = False
        gl_value = rs.GetInteger('Input 1(from GL) or 2(not from GL)')

        if gl_value == 1:
            gl_flag = True
        elif gl_value == 2:
            pass
        else:
            raise Exception('not intended num selected, please retry')

        # 選択された外部球の半径を用いる
        radius = new_inner_sphere.radius

        # 選択された外部球の中心点を用いる
        coordinate = new_inner_sphere.center_coordinate

        # 自身の空間を構成する球体のID番号
        inner_id = self.space_id

        # 前の外部球情報を更新する
        for sphere in new_outer_sphere:
            if sphere in self.sphere_outer_lists:
                continue
            sphere.switch_fixed_flag_true()
            self.sphere_outer_lists.append(sphere)

        # 他の空間領域との相互関係を決定するための外部球体を生成 --> この外部球が次の空間につながる
        temp_coordinate_list = []
        temp_vector_list = []
        center_coordinate = rs.CreateVector(coordinate)

        for sphere in self.sphere_outer_lists:
            start = rs.CreateVector(sphere.center_coordinate)
            end = center_coordinate
            move_vector = end - start
            temp_vector_list.append(move_vector)

        for i in range(len(temp_vector_list)):
            new_coordinate = rs.VectorAdd(center_coordinate, temp_vector_list[i])
            new_coordinate = Rhino.Geometry.Point3d(new_coordinate[0], new_coordinate[1], new_coordinate[2])
            temp_coordinate_list.append(new_coordinate)



        # 球体の中心点情報を更新(微調整)する
        # GLにフラットな面を構成するための調整
        # move_p = rs.CreateVector(coordinate[0], coordinate[1], coordinate[2] - 100)
        # flat_vec_coordinate = Rhino.Geometry.Point3d(move_p)



        # temp_select_point = []
        # for index, point in enumerate(temp_coordinate_list):
        #     if index == 0:
        #         temp_select_point = [point, index]
        #     else:
        #         if temp_select_point[0].Z > point.Z:
        #             temp_select_point = [point, index]
        #         else:
        #             continue

        # # 更新
        # del temp_coordinate_list[temp_select_point[1]]
        # temp_coordinate_list.append(flat_vec_coordinate)





        # 前世代の内部球
        self.previous_inner_sphere = new_outer_sphere[0]

        # 共通の面を構成している球体リスト(previous_inner + new outer sphere)
        self.voronoi_point_list.append(self.previous_inner_sphere)

        # 隣接関係を示すリストを作成 --> 内部球からみた外部球のID
        neighbor_ids = []
        for i in range(len(temp_coordinate_list)):  # 外部球のID
            outer_id = str(inner_id) + '-' + str(i+1)  # outer_id_name = space_id_outer_num --> ex. 1_1
            neighbor_ids.append(outer_id)

        # 空間領域を決定するための内部球を生成(インスタンス)
        original_id = inner_id
        outer_ids = neighbor_ids
        self.inner_sphere = Sphere.Sphere(original_id, inner_id, outer_ids, neighbor_ids, gl_flag, coordinate, radius)

        # 隣接関係を代入
        self.inner_sphere.neighbor_ids = new_inner_sphere.neighbor_ids

        # 外部球を生成(インスタンス)
        for i in range(len(temp_coordinate_list)):
            original_id = neighbor_ids[i]
            outer_ids = []
            radius = radius + random.randint(-100, 100)    # TODO 変更の余地あり
            gl_flag = False
            temp_neighbor_ids = [inner_id]    # 外部球は内部球とのみ隣接関係をもつように設定 TODO 変更の余地あり

            outer_sphere = Sphere.Sphere(original_id, inner_id, outer_ids, temp_neighbor_ids, gl_flag,
                                         temp_coordinate_list[i], radius)

            self.sphere_outer_lists.append(outer_sphere)
            self.voronoi_point_list.append(outer_sphere)

        # debug
        # self.sphere_outer_lists = self.voronoi_point_list


        # 不必要なオブジェクトを削除
        del temp_coordinate_list
        # del temp_neighbor_ids

    def sphere_packing(self):
        # 球体パッキングをするための球体リストを作成
        temp_sphere_list = []
        temp_sphere_list.extend(self.sphere_outer_lists)
        temp_sphere_list.append(self.inner_sphere)

        # 球体パッキングアルゴリズム
        for _ in range(1000):
            # 内部球 + 外部球のリストから1つずつ球体を取り出す
            for index, sphere in enumerate(temp_sphere_list):
                # 合成ベクトル計算
                unit_move_vector, flag = sphere.cul_move_vector(temp_sphere_list)

                # flagがTrueであれば、実際にベクトルを計算し動かす
                if flag is True:
                    # Vectorをk倍する kは第二引数
                    move_vector = rs.VectorScale(unit_move_vector, 30)

                    # 着目している球体の中心点の更新
                    sphere.update_center_coordinate(move_vector)

                elif flag is False:
                    continue
                else:
                    raise Exception('Flag return Error')

        # デバック用-draw-
        # self.inner_sphere.draw_sphere(outer_sphere=False)
        # for sphere in self.sphere_outer_lists:
        #     sphere.draw_sphere(outer_sphere=True)

        # 保持しているとメモリを圧迫するので廃棄
        del temp_sphere_list

    def delaunay_3d(self):

        # ドロネー分割をするための点群リストを作成
        self.points_list_from_sphere = []   # 球体の中心点のリスト [[x1, y1, z1], [x2, y2, z2], ...]
        self.divide_tetrahedron_list = []   # 分割された四面体のリスト

        # 自身の球体の中心点＋外部球体の中心点情報をリストに格納 --> [x, y, z]の形式で
        self.points_list_from_sphere.append(self.inner_sphere.center_coordinate)    # 内部球
        for sphere in self.sphere_outer_lists:                                      # 外部球
            self.points_list_from_sphere.append(sphere.center_coordinate)

        # ドロネー分割用に中心点リストのtemp_listを生成
        temp_points_list_from_sphere = copy.deepcopy(self.points_list_from_sphere)

        # 外部四面体を構成する点座標
        p1 = Point.Point([0, 0, 800000])
        p2 = Point.Point([0, 1000000, -200000])
        p3 = Point.Point([866000.025, -500000, -200000])
        p4 = Point.Point([-866000.025, -500000, -200000])

        # 四面体インスタンスを生成し、外部四面体の外接球とその半径を求める
        tetrahedron = Tetrahedron.Tetrahedron(p1, p2, p3, p4)
        tetrahedron.cul_center_p_and_radius()
        self.divide_tetrahedron_list.append(tetrahedron)

        # ドロネー分割のメインアルゴリズム
        for p in range(len(self.points_list_from_sphere)):    # 球体の中心点(点群)の数だけループさせる

            # 追加するポイントの選択 --> 点群リストから１つずつ取り出し、削除する
            select_point = self.points_list_from_sphere.pop(0)    # [x, y, z]でありPointインスタンスでない
            select_point = Point.Point(select_point)              # Pointインスタンスに変換

            # 外部四面体の外接球内に追加したポイントが内包されていないか判定。内包されている場合はindexを保存。
            temp_divide_tetrahedron = []
            count = 0

            # # debug
            # debug_parent_name = "gen" + str(p)
            # debug_parent_layer = rs.AddLayer(debug_parent_name, [0, 0, 0])
            #
            # print("draw num divide_tetra: {0}".format(len(self.divide_tetrahedron_list)))
            # temp_draw_objs = copy.deepcopy(self.divide_tetrahedron_list)
            #
            # for index, tetra in enumerate(temp_draw_objs):
            #     tetra.draw_divide_tetrahedron(p, index, debug_parent_layer)

            for i in range(len(self.divide_tetrahedron_list)):
                tetra = self.divide_tetrahedron_list[i + count]

                check = tetra.check_point_include_circumsphere(select_point)

                # 選択された点が外部四面体に接する外接球内に内包されている場合
                if check:
                    # 内包していた三角形の頂点を使用して再分割する。 --> 再分割された四面体を生成する
                    new_tetrahedron1 = Tetrahedron.Tetrahedron(tetra.p1, tetra.p2, tetra.p3, select_point)
                    new_tetrahedron2 = Tetrahedron.Tetrahedron(tetra.p1, tetra.p2, tetra.p4, select_point)
                    new_tetrahedron3 = Tetrahedron.Tetrahedron(tetra.p1, tetra.p3, tetra.p4, select_point)
                    new_tetrahedron4 = Tetrahedron.Tetrahedron(tetra.p2, tetra.p3, tetra.p4, select_point)

                    # 新たに生成された四面体の外接球、その半径を求める。
                    new_tetrahedron1.cul_center_p_and_radius()
                    new_tetrahedron2.cul_center_p_and_radius()
                    new_tetrahedron3.cul_center_p_and_radius()
                    new_tetrahedron4.cul_center_p_and_radius()

                    # 一時的に新たに生成された四面体をリストに格納しておく
                    temp_divide_tetrahedron.append(new_tetrahedron1)
                    temp_divide_tetrahedron.append(new_tetrahedron2)
                    temp_divide_tetrahedron.append(new_tetrahedron3)
                    temp_divide_tetrahedron.append(new_tetrahedron4)

                    # 分割するのに使用した元の四面体を削除する
                    del self.divide_tetrahedron_list[i + count]

                    # 変数を更新  --> 上記で元の四面体を削除するためself.divide_tetrahedron_listの大きさが小さくなるので
                    count = count - 1

                # 選択された点が外部四面体に接する外接球内に内包されていない場合
                else:
                    pass  # passは「何もしない」ということを明示的に書き記す

            # 重複している四面体を削除
            del_instances = []
            for tetra in temp_divide_tetrahedron:
                for tetra_check in temp_divide_tetrahedron:
                    if tetra == tetra_check:
                        continue
                    if tetra.radius == tetra_check.radius and tetra.center_p == tetra_check.center_p:
                        del_instances.append(tetra_check)
                        del_instances.append(tetra)

            for del_instance in del_instances:
                if del_instance in temp_divide_tetrahedron:
                    del temp_divide_tetrahedron[temp_divide_tetrahedron.index(del_instance)]

            # 重複三角形を削除した後に3次元ドロネー分割を行い生成された四面体をリストに格納
            self.divide_tetrahedron_list.extend(temp_divide_tetrahedron)

        # self.points_list_from_sphereの情報を復活させる --> あとで廃棄
        self.points_list_from_sphere = temp_points_list_from_sphere
        del temp_points_list_from_sphere

        # 各四面体のエッジの長さを取得
        for tetra in self.divide_tetrahedron_list:
            tetra.draw_divide_tetrahedron()

    def voronoi_3d_from_delaunay_3d(self, flag=False):

        # 自身の球体＋外部球体の中心点を取得
        if flag:
            sphere_center_point_list = self.points_list_from_sphere
        else:
            temp_sphere_center_point_list = []
            for sphere in self.voronoi_point_list:
                point = sphere.center_coordinate
                temp_sphere_center_point_list.append(point)

            sphere_center_point_list = temp_sphere_center_point_list

        # 母点(球体の中心点)ごとにボロノイ分割を行う
        for index, select_point in enumerate(sphere_center_point_list):

            # debug
            # parent_layer_name = "point" + str(index)
            # parent_layer = rs.AddLayer(parent_layer_name, [0, 0, 0])
            # sel_p = rs.AddPoint(select_point)
            # set_layer(sel_p, "select_point", 0, 0, 0, parent_layer)

            tetrahedron_have_common_p = []
            for tetrahedron in self.divide_tetrahedron_list:
                # 選択された球体の中心点と選択された四面体を構成する4頂点のいずれかが同じ点である場合
                if tetrahedron.p1.coordinate == select_point or \
                   tetrahedron.p2.coordinate == select_point or \
                   tetrahedron.p3.coordinate == select_point or \
                   tetrahedron.p4.coordinate == select_point:

                    # 四面体をリストに追加
                    tetrahedron_have_common_p.append(tetrahedron)

            # debug
            # print("num divide_tetra:{0} ".format(len(self.divide_tetrahedron_list)))
            # print("num tetrahedron_have_common_p:{0} ".format(len(tetrahedron_have_common_p)))
            # print("\n")

            # 共有点を持つ四面体を使用してボロノイ図形を作成する
            for i in range(len(tetrahedron_have_common_p)):
                tetra1 = tetrahedron_have_common_p.pop(0)

                # デバック
                # tetra1.draw_sphere(parent_layer)
                # tetra1.draw_divide_tetrahedron(parent_layer)

                for tetra2 in tetrahedron_have_common_p:
                    if tetra1 == tetra2:
                        continue

                    count = 0
                    if tetra1.p1 == tetra2.p1 or tetra1.p1 == tetra2.p2 or tetra1.p1 == tetra2.p3 or tetra1.p1 == tetra2.p4:
                        count += 1
                    if tetra1.p2 == tetra2.p1 or tetra1.p2 == tetra2.p2 or tetra1.p2 == tetra2.p3 or tetra1.p2 == tetra2.p4:
                        count += 1
                    if tetra1.p3 == tetra2.p1 or tetra1.p3 == tetra2.p2 or tetra1.p3 == tetra2.p3 or tetra1.p3 == tetra2.p4:
                        count += 1
                    if tetra1.p4 == tetra2.p1 or tetra1.p4 == tetra2.p2 or tetra1.p4 == tetra2.p3 or tetra1.p4 == tetra2.p4:
                        count += 1

                    # 共通点が3つ以上ある場合
                    if count == 3:
                        voronoi_line = Rhino.Geometry.Line(tetra1.center_p[0], tetra1.center_p[1], tetra1.center_p[2],
                                                           tetra2.center_p[0], tetra2.center_p[1], tetra2.center_p[2])

                        # Sphereクラスにボロノイエッジ情報を割り当てる
                        # 内部球
                        if self.inner_sphere.center_coordinate == select_point:
                            self.inner_sphere.voronoi_edge.append(voronoi_line)
                        else:
                            # 外部球
                            for sphere in self.sphere_outer_lists:
                                if sphere.center_coordinate == select_point:
                                    sphere.voronoi_edge.append(voronoi_line)

                                else:
                                    continue

                        # デバック用-draw-
                        # voronoi_line = scriptcontext.doc.Objects.AddLine(voronoi_line)
                        # layer_name = "voronoi_line" + str(i)
                        # set_layer(voronoi_line, layer_name, 0, 0, 255, parent_layer)

    def draw_all(self):
        parent_layer_name = "Space" + str(self.space_id)
        parent_layer = rs.AddLayer(parent_layer_name, [0, 0, 0])

        self.draw_voronoi_edge(parent_layer)
        self.draw_delaunay_edge(parent_layer)
        self.draw_inner_sphere(parent_layer)
        self.draw_outer_sphere(parent_layer)
        self.draw_dot_text(parent_layer)

    def draw_voronoi_edge(self, parent_layer=None):
        # ボロノイ領域を構成するボロノイエッジのみを描画
        for edge in self.inner_sphere.voronoi_edge:
            line = scriptcontext.doc.Objects.AddLine(edge)
            set_layer(line, "voronoi_edge", 0, 0, 255, parent_layer)

    def draw_delaunay_edge(self, parent_layer=None):
        self.get_relationship_from_delaunay_edge(parent_layer)

    def draw_inner_sphere(self, parent_layer=None):
        self.inner_sphere.draw_sphere(False, parent_layer)

    def draw_outer_sphere(self, parent_layer=None):
        for sphere in self.sphere_outer_lists:
            sphere.draw_sphere(True, parent_layer)

    def draw_dot_text(self, parent_layer=None):

        dot = rs.AddTextDot(str(self.inner_sphere.original_id), self.inner_sphere.center_coordinate)
        set_layer(dot, "ID", 0, 0, 0, parent_layer)

        for sphere in self.sphere_outer_lists:
            dot = rs.AddTextDot(str(sphere.original_id), sphere.center_coordinate)
            set_layer(dot, "ID", 0, 0, 0, parent_layer)

    def select_sphere_by_id_number(self, selected_sphere_id):
        new_sphere_instance = None

        if self.inner_sphere.original_id == selected_sphere_id:
            new_sphere_instance = copy.deepcopy(self.inner_sphere)
            return new_sphere_instance
        else:
            for sphere in self.sphere_outer_lists:
                if sphere.original_id == selected_sphere_id:
                    new_sphere_instance = copy.deepcopy(sphere)
                    return new_sphere_instance

        print("There is no sphere")
        return new_sphere_instance

    def get_relationship_from_delaunay_edge(self, parent=None):

        temp_delaunay_edge_list = []
        temp_get_delaunay_edge_list = []
        get_delaunay_edge_list = []

        # ドロネー分割により取得したドロネー辺を1つのリストにまとめる
        for tetra in self.divide_tetrahedron_list:
            for edge in tetra.edge_lines:
                temp_delaunay_edge_list.append(edge)

        # ある長さより長いドロネー辺は削除する(インデックスを取得し、保持)
        upper_limit_length = 10000
        del_instance_index_list = []

        for index, edge in enumerate(temp_delaunay_edge_list):
            length = edge.Length
            if length > upper_limit_length:
                del_instance_index_list.append(index)

        # ある長さより短いドロネー辺のみを取得する
        for index, edge in enumerate(temp_delaunay_edge_list):
            if index in del_instance_index_list:
                continue
            else:
                temp_get_delaunay_edge_list.append(edge)

        # 重複を解消する
        count = 0
        while count != len(temp_get_delaunay_edge_list):
            a_edge = temp_get_delaunay_edge_list[count]
            a_start_coordinate = a_edge.From
            a_end_coordinate = a_edge.To
            del_index_list = []

            for b_index in range(count+1, len(temp_get_delaunay_edge_list)):
                b_edge = temp_get_delaunay_edge_list[b_index]
                b_start_coordinate = b_edge.From
                b_end_coordinate = b_edge.To
                if a_start_coordinate == b_start_coordinate or a_start_coordinate == b_end_coordinate:
                    if a_end_coordinate == b_start_coordinate or a_end_coordinate == b_end_coordinate:
                        del_index_list.append(b_index)

            del_count = 0
            for b_index in range(count+1, len(temp_get_delaunay_edge_list)):
                if b_index in del_index_list:
                    del temp_get_delaunay_edge_list[b_index + del_count]
                    del_count -= 1

            count += 1

        # Rhino空間上に描画 --> 母点ごとに
        for edge in temp_get_delaunay_edge_list:
            get_delaunay_edge_list.append(scriptcontext.doc.Objects.AddLine(edge))

        self.assign_delaunay_edge_to_sphere(get_delaunay_edge_list)

        temp_sphere_list = [self.inner_sphere]    # 内部球
        for sphere in self.sphere_outer_lists:    # 外部球
            temp_sphere_list.append(sphere)

        for sphere in temp_sphere_list:
            parent_layer_name = "delaunay_edge"
            parent_layer = rs.AddLayer(parent_layer_name, [0, 0, 0], False, False, parent)
            sphere.draw_delaunay_line(parent_layer)

        # del
        del temp_get_delaunay_edge_list
        del temp_delaunay_edge_list
        for edge in get_delaunay_edge_list:
            rs.DeleteObject(edge)

    def assign_delaunay_edge_to_sphere(self, delaunay_edge_list):
        temp_sphere_list = [self.inner_sphere]    # 内部球
        for sphere in self.sphere_outer_lists:    # 外部球
            temp_sphere_list.append(sphere)

        for sphere in temp_sphere_list:
            start_point = sphere.center_coordinate
            for temp_sphere in temp_sphere_list:
                end_point = temp_sphere.center_coordinate
                if start_point == end_point:
                    continue
                for edge in delaunay_edge_list:
                    delaunay_start_point = rs.CurveStartPoint(edge)
                    delaunay_end_point = rs.CurveEndPoint(edge)

                    if start_point == delaunay_start_point or start_point == delaunay_end_point:
                        if end_point == delaunay_start_point or end_point == delaunay_end_point:
                            line = rs.AddLine(start_point, end_point)
                            sphere.delaunay_lines.append(line)

                            # neighbor_ids
                            relation_id = temp_sphere.original_id
                            sphere.neighbor_ids.append(relation_id)

        # debug
        # for sphere in temp_sphere_list:
        #     print("Original_id: {0}".format(sphere.original_id))
        #     for sphere_id in sphere.neighbor_ids:
        #         print(sphere_id)
        # print("\n")

        # del
        del temp_sphere_list

    def assign_neighbor_ids_to_packing_ids(self):
        self.inner_sphere.neighbor_ids_packing = self.inner_sphere.neighbor_ids
        for sphere in self.sphere_outer_lists:
            sphere.neighbor_ids_packing = sphere.neighbor_ids

    # 以下触れていないメソッド
    def draw_faces(self):
        for line in self.space_edges[0]:
            scriptcontext.doc.Objects.AddLine(line)

        for line in self.space_edges[1]:
            scriptcontext.doc.Objects.AddLine(line)

        for line in self.space_edges[2]:
            scriptcontext.doc.Objects.AddLine(line)
        # tolerance = scriptcontext.doc.ModelAbsoluteTolerance
        # for curves in self.space_face:
        #     breps = Rhino.Geometry.Brep.CreatePlanarBreps(curves, tolerance)
        #     scriptcontext.doc.Objects.AddBrep(breps)
            # if breps:
            #     rc = [scriptcontext.doc.Objects.AddBrep(brep) for brep in breps]
                # scriptcontext.doc.Views.Redraw()
                # return rc

    def construct_face(self):  # TODO  重なりが生まれてしまうので調整が必要。
        # lineを二重に複製
        temp_line_obj_list = []
        temp_voronoi_lines = []

        # ボロノイエッジを取得し、リストに格納
        for edge in self.inner_sphere.voronoi_edge:
            temp_voronoi_lines.append(edge)

        for sphere in self.sphere_outer_lists:
            for edge in sphere.voronoi_edge:
                temp_voronoi_lines.append(edge)

        temp_line_obj_list.extend(temp_voronoi_lines)
        temp_line_obj_list.extend(temp_voronoi_lines)

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

        # self.already_make_face_flag = True
        self.space_edges_final.extend(face_lines)

    def make_surface(self):
        """pointからサーフェスを作成する"""

        # pointを循環順に取り出す。
        # print(self.space_edges)
        # print(len(self.space_edges))

        for loop in range(len(self.space_edges)):
            space_edge = self.space_edges[loop]

            points = []
            for index, line in enumerate(space_edge):
                if index == 0:
                    start = line.PointAt(0)
                    end = line.PointAt(1)
                    points.append(start)
                    points.append(end)
                else:
                    if end == line.PointAt(0):
                        start = line.PointAt(0)
                        end = line.PointAt(1)
                    elif end == line.PointAt(1):
                        start = line.PointAt(1)
                        end = line.PointAt(0)
                    elif start == line.PointAt(0):
                        start = line.PointAt(0)
                        end = line.PointAt(1)
                    elif start == line.PointAt(1):
                        start = line.PointAt(1)
                        end = line.PointAt(0)
                    else:
                        raise Exception('Error')

                    if index == 1:
                        points.append(end)
                    elif end == points[0]:
                        break
                    else:
                        points.append(end)

            origin_p = points[0]
            tolerance = scriptcontext.doc.ModelAbsoluteTolerance

            surfaces = []
            for i in range(len(points) - 2):
                p1 = points[i + 1]
                p2 = points[i + 2]
                surface = Rhino.Geometry.Brep.CreateFromCornerPoints(origin_p, p1, p2, tolerance)
                # scriptcontext.doc.Objects.AddBrep(surface)

                surfaces.append(surface)

            tol = scriptcontext.doc.ModelAbsoluteTolerance * 2.1
            joinedbreps = Rhino.Geometry.Brep.JoinBreps(surfaces, tol)
            # scriptcontext.doc.Objects.AddBrep(joinedbreps[0])

            # print(joinedbreps)
            if joinedbreps is None:
                continue

            self.space_faces.append(joinedbreps[0])  # Message: 'NoneType' object is not subscriptable

# Global Method
def set_layer(obj, name, r, g, b, parent_layer, visible=True):
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
