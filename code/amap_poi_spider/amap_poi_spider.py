import logging
import datetime
import time

import requests

logging.basicConfig(
    filename=f"{datetime.date.today()}.log",
    filemode="a+",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def search_poi(poi_typecode: str, search_range: str,api_key:str) -> dict:
    """
    在单个矩形范围内搜索POI，仅适用于中国境内，东经，北纬
    对于一个多边形区域，每次最多搜索出200条，所以需要划分成多个多边形区域
    “多边形区域搜索”接口每天限制调用100次，3次/秒
    https://lbs.amap.com/api/webservice/guide/api-advanced/newpoisearch
    返回
    page：终止的页数
    pois：list[dict] 可能为空
    is_end：是否该区域已经搜索完
    api_is_full：是否调用量超限
    """
    logging.info(f"黄若凡地理数据爬取矩形范围搜索模块")
    ret = {"page": 1, "pois": [], "is_end": False,"api_is_full":False}
    
    while not ret["api_is_full"]:  # 每一页
        time.sleep(4)
        response = requests.get(
            url="https://restapi.amap.com/v5/place/polygon",
            params={
                "key": api_key,
                "polygon": search_range,  # 多个坐标对集合，坐标对用 | 分割。多边形为矩形时，可传入左上右下两顶点坐标对；其他情况下首尾坐标对需相同。
                "types": poi_typecode,  # 可以传入多个poi typecode，相互之间用 | 分隔
                "page_size": 25,  # 当前分页展示的数据条数，取值1到25
                "page_num": ret[
                    "page"
                ],  # 请求第几分页，取值1到100，如果上面指定25条，这里实际只有前8页
                "show_fields": "business",  # 返回结果控制
            },
        )
        logging.info(f"GET {search_range}")
        response = response.json()
        if response["status"] == "1":
            count = int(response["count"])
            pois: list[dict] = response["pois"]
            logging.info(f"爬取到第{ret["page"]}页，有{count}条")
            if ret["page"] <= 8 and count < 25:  # 说明是最后一页
                ret["pois"].extend(pois)
                ret["is_end"] = True
                break
            elif ret["page"] == 8 and count == 25:  # 说明需要进一步划分搜索范围
                ret["page"] += 1
                ret["pois"].extend(pois)
                break
            else:# 搜索下一页
                ret["page"] += 1
                ret["pois"].extend(pois)
        else:
            logging.error("搜索失败" + str(response))
            ret["api_is_full"] = True # 一天的量用完了
    return ret