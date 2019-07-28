# coding: utf-8
import SequentialAdding
import Space
import rhinoscriptsyntax as rs

# global value
num_space = 1
sequential = SequentialAdding.SequentialAdding()

# sequentialAddingインスタンス生成
for i in range(num_space):
    # Spaceインスタンスを生成
    spatial_domain_space = Space.Space()

    # 空間相互の関係性を保持するSequentialAddingクラスに追加。
    sequential.add_spatial_domain_space(spatial_domain_space)

rs.EnableRedraw(False)

# main loop -start-
for i in range(num_space):

    # 01_空間領域を構成するSpaceインスタンスを取得
    spatial_domain_space = sequential.space_list[i]

    # 02_空間領域(Space)を構成するための球体を生成する --> ここで球体の中心点を選択する。重要
    spatial_domain_space.create_spatial_domain_by_sphere()

    # 03_空間領域を決定する球体を球体パッキングする際に固定する。 --> 着目している球を固定
    spatial_domain_space.spatial_domain_sphere.switch_fixed_flag_true()

    # 04_既存の球体を使用して球体パッキングを実行 --> パッキングによってドロネー、ボロノイを行う際の母点の位置を調整する
    spatial_domain_space.sphere_packing()

    # 05_ドロネー分割の後にボロノイ分割を行う。 --> ボロノイ分割によって領域を決定
    spatial_domain_space.delaunay_3d()
    spatial_domain_space.voronoi_3d_from_delaunay_3d()

    # 外部空間に関して、まだ面が作成されていないボロノイ空間に面を作成する。
    # --> 外部空間とは？
    for outer_sphere in spatial_domain_space.sphere_outer_lists:
        if outer_sphere.already_make_face_flag is True:
            continue
        else:
            outer_sphere.construct_face()
            outer_sphere.space_instance.make_surface()

# main loop -end-

rs.EnableRedraw(True)
