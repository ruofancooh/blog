import datetime
import logging
import time
from enum import Enum

import geopandas as gpd
import pandas as pd
from pymongo import MongoClient
from shapely.geometry import Polygon

from amap_poi_spider import search_poi
from utils import plot_rectangles_on_geo, rectangle_str_to_polygon, split_rectangle

logging.basicConfig(
    filename=f"{datetime.date.today()}.log",
    filemode="a+",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


client = MongoClient("mongodb://localhost:27017/")
db = client["武汉市餐饮店POI数据"]
pois_db = db["POI数据"]
FOOD = "050000"


class SearchAreaStatus(Enum):
    B = {"是否搜索完": False, "到第几页没有数据": 9}
    C = {
        "是否搜索完": False,
        "$or": [{"到第几页没有数据": {"$lt": 9}}, {"到第几页没有数据": ""}],
    }


API_KEYS = []


def a_search_in_a_round(round: str):
    """某轮的某次搜索"""
    search_ranges = db[f"第{round}轮筛的搜索范围"]
    key_index = 0
    for doc in search_ranges.find(SearchAreaStatus.C.value):
        while key_index < len(API_KEYS):
            range_str = doc["_id"]
            time.sleep(1)
            result = search_poi(FOOD, range_str, API_KEYS[key_index])
            search_ranges.update_one(
                {"_id": range_str},
                {
                    "$set": {
                        "是否搜索完": result["is_end"],
                        "到第几页没有数据": result["page"],
                    }
                },
                upsert=True,
            )
            for poi in result["pois"]:
                _id = poi.pop("id")
                pois_db.update_one({"_id": _id}, {"$set": poi}, upsert=True)
            if result["api_is_full"]:
                key_index += 1
            else:
                break


def search_areas_remaining_in_a_round(round: str, status: SearchAreaStatus):
    """某轮某次搜索后剩余某个状态的搜索区域的数量"""
    search_ranges = db[f"第{round}轮筛的搜索范围"]
    i = 0
    for _ in search_ranges.find(status.value):
        i += 1
    print(i)


def after_a_search_round(round: str):
    """把本轮未搜索完，需要进一步划分的区域的写到文件里"""
    search_ranges = db[f"第{round}轮筛的搜索范围"]
    f = search_ranges.find(SearchAreaStatus.B.value)
    unfinished_range = [doc["_id"] for doc in f]
    df = pd.DataFrame({"s_range": unfinished_range})
    df.to_csv(f"第{round}轮筛之后未搜索完的.csv", index=False)


def show_unfinished(old_round_csv_file: str, geojson_file: str):
    """展示上一轮里未搜索完的区域"""
    df = pd.read_csv(old_round_csv_file)
    old_rectangles = [rectangle_str_to_polygon(s) for s in df["s_range"]]
    print(f"上一轮里未搜索完的区域有{len(old_rectangles)}个")
    plot_rectangles_on_geo(geojson_file, old_rectangles)


def divide_search_area(
    old_rectangles: list[Polygon], geojson_file: str, num_parts: int
) -> list[Polygon]:
    """划分一系列矩形为整数的平方份，并确保与行政区有交"""
    new_rectangles: list[Polygon] = []
    for r in old_rectangles:
        new_rs = split_rectangle(r, num_parts=num_parts)
        assert len(new_rs) == num_parts
        new_rectangles.extend(new_rs)
    gdf: gpd.GeoDataFrame = gpd.read_file(geojson_file)
    polygons = [geom for geom in gdf.geometry if isinstance(geom, Polygon)]
    new_search_ranges: list[Polygon] = []
    for r in new_rectangles:
        for p in polygons:
            if r.intersects(p):
                new_search_ranges.append(r)
    plot_rectangles_on_geo(geojson_file, new_search_ranges)
    return new_search_ranges


def before_a_search_round(new_round: str, new_search_ranges: list[Polygon]):
    """写新的搜索区域到数据库里，注意保留小数的位数"""
    collection = db[f"第{new_round}轮筛的搜索范围"]
    for r in new_search_ranges:
        minx, miny, maxx, maxy = r.bounds
        s = f"{minx:.3f},{miny:.3f}|{maxx:.3f},{maxy:.3f}"
        collection.update_one(
            {"_id": s},
            {
                "$set": {
                    "到第几页没有数据": "",
                    "是否搜索完": False,
                }
            },
            upsert=True,
        )


# show_unfinished("第二轮筛之后未搜索完的.csv", "武汉市13个区.geojson")
# df = pd.read_csv("第二轮筛之后未搜索完的.csv")
# old_rectangles = [rectangle_str_to_polygon(s) for s in df["s_range"]]
# new_search_ranges = divide_search_area(old_rectangles, "武汉市13个区.geojson", 25)
# before_a_search_round("三", new_search_ranges)
# search_areas_remaining_in_a_round("三", SearchAreaStatus.C)

a_search_in_a_round("三")

# after_a_search_round("二")