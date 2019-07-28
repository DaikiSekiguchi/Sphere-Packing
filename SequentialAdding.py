# coding: utf-8
import Sphere
import Space
from voronoi_module import Point
from voronoi_module import Tetrahedron
import rhinoscriptsyntax as rs
import Rhino.Geometry
import scriptcontext


class SequentialAdding:
    def __init__(self):
        self.neighbor_info = []            # 隣接関係
        self.sphere_lists = []             #
        self.sphere_outer_lists = []       #

        self.divide_tetrahedron_list = []  # 更新するときに一度破棄する必要あり。
        self.points_obj_list = []          # 更新するときに一度破棄する必要あり。

        # Add by 関口
        self.space_list = []

    def add_spatial_domain_space(self, spatial_domain):
        """空間領域を追加する"""
        self.space_list.append(spatial_domain)

    # 以下触れていないメソッド
    def tangent_plane(self):
        pass

    def draw_result(self):
        """最終結果をRhinoに描画"""
        for sphere in self.sphere_lists:
            for line in sphere.space_instance.space_outlines:
                scriptcontext.doc.Objects.AddLine(line)

    def draw_sphere(self):
        for sphere_origin in self.sphere_lists:
            print('draw')
            sphere_origin.draw_sphere()

        for sphere in self.sphere_outer_lists:
            sphere.draw_sphere()

    def set_outer_sphere(self, center_coordinate):
        self_id = None
        radius = 500
        neighbor_ids = []
        gl_flag = False

        outer_id = len(self.sphere_outer_lists) + 1
        outer_sphere = Sphere.Sphere(self_id, gl_flag, center_coordinate, radius, neighbor_ids, outer_id)
        self.sphere_outer_lists.append(outer_sphere)

    def judge_point_space_in_or_out(self, point):
        """ボロノイが作成する空間内に追加した点が有るか判定。有る場合はSphereインスタンスのIDをreturn"""
        for outer_sphere in self.sphere_outer_lists:
            judge_flag = outer_sphere.judge_point_inside_voronoi_area(point)
            if judge_flag is True:
                return outer_sphere.outer_id
            elif judge_flag is False:
                continue
            else:
                raise Exception('Error')

        raise Exception('Error')

    def delete_outer_sphere_instance(self, instance_id):
        """指定されたIDのSphereインスタンスを削除する。"""
        for index, outer_sphere in enumerate(self.sphere_outer_lists):
            if outer_sphere.outer_id == instance_id:
                del self.sphere_outer_lists[index]
                return True
            else:
                continue

        raise Exception('can not delete')

    def all_exist_sphere_fixed(self):
        """すべてのすでに存在しているSphereインスタンスを球体パッキングにおいて固定する。"""
        for sphere in self.sphere_lists:
            sphere.switch_fixed_flag_true()

        for outer_sphere in self.sphere_outer_lists:
            outer_sphere.switch_fixed_flag_true()

