# coding: utf-8
import SequentialAdding
import Space
import rhinoscriptsyntax as rs

# global value
num_space = 4
sequential = SequentialAdding.SequentialAdding()

# ここはのちのち前回データをインポートする
#

# main loop -start-

for i in range(1, num_space+1):
    if i == 1:

        # 01_空間領域を構成するSpaceインスタンスを取得
        spatial_domain_space = Space.Space(i)

        # 空間相互の関係性を保持するSequentialAddingクラスに追加
        sequential.add_spatial_domain_space(spatial_domain_space)

        # 02_空間領域(Space)を構成するための球体を生成する --> ここで球体の中心点を選択する。重要
        spatial_domain_space.create_spatial_domain_by_sphere()

        rs.EnableRedraw(False)

        # 03_空間領域を決定する球体を球体パッキングする際に固定する。 --> 着目している球を固定
        spatial_domain_space.inner_sphere.switch_fixed_flag_true()

        # 04_既存の球体を使用して球体パッキングを実行 --> パッキングによってドロネー、ボロノイを行う際の母点の位置を調整する
        spatial_domain_space.sphere_packing()

        # 05_ドロネー分割の後にボロノイ分割を行う。 --> ボロノイ分割によって領域を決定
        spatial_domain_space.delaunay_3d()
        spatial_domain_space.voronoi_3d_from_delaunay_3d(True)

        # 06_外部空間に関して、まだ面が作成されていないボロノイ空間に面を作成する
        # --> 外部空間とは？
        # spatial_domain_space.construct_face()
        # spatial_domain_space.space_instance.make_surface()

        # 情報空間に描画する
        spatial_domain_space.draw_all()

        rs.EnableRedraw(True)

    else:

        # 01_空間領域を構成するSpaceインスタンスを取得
        spatial_domain_space = Space.Space(i)

        # 空間相互の関係性を保持するSequentialAddingクラスに追加
        sequential.add_spatial_domain_space(spatial_domain_space)

        # 次のボロノイ空間のつながりを外部球のID番号で選択する
        select_space_id = rs.GetString("Input select space id")
        sphere_list = sequential.select_inner_sphere_from_previous_space(int(select_space_id))

        rs.EnableRedraw(False)

        # 02_空間領域(Space)を構成するための球体を生成する --> ここで球体の中心点を選択する。重要
        spatial_domain_space.create_spatial_domain_by_previous_info(sphere_list[0], sphere_list[1])

        # 03_空間領域を決定する球体を球体パッキングする際に固定する。 --> 着目している球を固定
        spatial_domain_space.inner_sphere.switch_fixed_flag_true()

        # 04_既存の球体を使用して球体パッキングを実行 --> パッキングによってドロネー、ボロノイを行う際の母点の位置を調整する
        spatial_domain_space.sphere_packing()

        # 05_ドロネー分割の後にボロノイ分割を行う。 --> ボロノイ分割によって領域を決定
        spatial_domain_space.delaunay_3d()
        spatial_domain_space.voronoi_3d_from_delaunay_3d(True)

        # 06_外部空間に関して、まだ面が作成されていないボロノイ空間に面を作成する

        # 要求されるボロノイ空間のエッジのみ取得する(描画する)
        spatial_domain_space.draw_all()

        del sphere_list

        rs.EnableRedraw(True)

# main loop -end-

