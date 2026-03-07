import math

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Polygon, box


def rectangle_str_to_polygon(r: str) -> list[Polygon]:
    """把类似 114.30,30.60|114.35,30.65 的矩形字符串转换为 Polygon 对象"""
    left_top, right_bottom = r.split("|")
    left, top = map(float, left_top.split(","))
    right, bottom = map(float, right_bottom.split(","))
    return Polygon([(left, top), (right, top), (right, bottom), (left, bottom)])


def plot_rectangles_on_geo(geojson_file_path: str, rectangles: list[Polygon]):
    gdf: gpd.GeoDataFrame = gpd.read_file(geojson_file_path)
    sub_gdf = gpd.GeoDataFrame({"geometry": rectangles})
    new_gdf: gpd.GeoDataFrame = pd.concat([gdf, sub_gdf], ignore_index=True)
    new_gdf.plot(facecolor="none", edgecolor="black", linewidth=1)
    plt.show()


def split_rectangle(rectangle: Polygon, num_parts: int) -> list[Polygon]:
    """把一个Polygon的矩形切分成指定数量、长宽固定的小矩形，确保与原矩形有交"""
    minx, miny, maxx, maxy = rectangle.bounds
    # 计算每边应分割成的部分数量
    side_parts = int(math.sqrt(num_parts))
    # 计算每个小矩形的宽度和高度
    width = (maxx - minx) / side_parts
    height = (maxy - miny) / side_parts
    sub_rectangles = []
    for i in range(side_parts):
        for j in range(side_parts):
            left = minx + i * width
            bottom = miny + j * height
            right = left + width
            top = bottom + height
            small_rectangle = box(left, bottom, right, top)
            if rectangle.intersects(small_rectangle):
                sub_rectangles.append(small_rectangle)

    return sub_rectangles


if __name__ == "__main__":
    r: Polygon = rectangle_str_to_polygon("114.35,30.85|114.40,30.90")

    def print_b(p: Polygon):
        print(f"左上：{p.bounds[0],p.bounds[1]}，右下：{p.bounds[2],p.bounds[3]}")

    new_rs = split_rectangle(r, 25)
    assert len(new_rs) == 25

    print_b(r)
    print_b(new_rs[0])
    print_b(new_rs[-1])