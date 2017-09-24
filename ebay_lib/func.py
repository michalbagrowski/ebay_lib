import time
from chalice import Chalice, Response
from chalicelib import config
import chalicelib
import operator
from pymemcache.client.base import Client
import os
import json

from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection as Finding
import urllib
import boto3
def get_keywords(items):
    keywords = []
    count_keys = {}
    for i in items:
        keywords = keywords + i["title"].split()

    for keyword in keywords:
        if keyword not in count_keys:
            count_keys[keyword] = 0
        count_keys[keyword] =count_keys[keyword] +1
    count_keys = sorted(count_keys.items(), key=operator.itemgetter(0))

    keywords = []

    for aaa in count_keys:
        print(aaa)
        if aaa[1] > 1:
            keywords.append(aaa[0])

    return keywords

def search(query, page = 1):
    page = int(page)
    limit = 51

    rows = 3
    print(config.cats[0])
    items = get_search_items(query, config.cats[0], 51, page)

    if limit  == len(items["searchResult"]["item"]):
        in_rows = int(limit/rows)
    else:
        in_rows = int(len(items["searchResult"]["item"])/rows)

    keywords = get_keywords(items["searchResult"]["item"])
    return {
            "keywords": ", ".join(keywords),
            "title": config.title,
            "description": config.description,

            "items":  items,
            "pages": get_pages(page, int(items["paginationOutput"]["totalPages"])),
            "query": query,
            "current_page": page,
            "total_pages": int(items["paginationOutput"]["totalPages"]),
            "limit": limit,
            "in_rows": in_rows
        }


def index():
    start = time.time()

    page = 1
    limit = 51
    rows = 3

    items = get_items(config.cats[0], limit)

    keywords = get_keywords(items["searchResult"]["item"])

    return {
            "keywords": ", ".join(keywords),
            "title":  config.title,
            "description": config.description,
            "items": items,
            "pages":  get_pages(page, int(items["paginationOutput"]["totalPages"])),
            "category": config.cats[0],
            "current_page": page,
            "total_pages":  int(items["paginationOutput"]["totalPages"]),
            "limit": limit,
            "in_rows": int(limit/rows)+1
        }



def category(category, page):
    page = int(page)
    limit = 51
    items = get_items(category, 50, page)
    rows = 3
    if limit  == len(items["searchResult"]["item"]):
        in_rows = int(limit/rows)
    else:
        in_rows = int(len(items["searchResult"]["item"])/rows)

    keywords = get_keywords(items["searchResult"]["item"])
    return {
        "keywords": ", ".join(keywords),
        "title":  config.title,
        "description":  config.description,

        "items": items,
        "pages": get_pages(page, int(items["paginationOutput"]["totalPages"])),

        "category": category,
        "current_page": page,
        "total_pages":  int(items["paginationOutput"]["totalPages"]),
        "in_rows" : in_rows
        }

def get_items(cat, limit = 10, page = 1):
    key_name = "items_" + str(cat) + "_" + str(limit) + "_" + str(page)
    result = get_cache(key_name)
    if(result):
        return json.loads(result)
    else:
        start = time.time()
        api = init_finding_api()
        callData = {
            "categoryId": cat,
            "outputSelector": ["GalleryInfo","PictureURLLarge"],
            "paginationInput": {
                "entriesPerPage": limit,
                "pageNumber": page
            }
        }

        items = api.execute('findItemsByCategory', callData).dict()

        send_metric("get_items", time.time() - start)
        set_cache(key_name, json.dumps(items))

    return items


cache_client = None

def get_client():
    global cache_client
    if cache_client is None:
        cache_client = Client((os.environ["MEMCACHED_HOST"], int(os.environ["MEMCACHED_PORT"])))
    return cache_client

def get_cache(key_name):
    client = get_client()
    result = client.get(key_name)
    print(key_name)
    return result

def set_cache(key_name, value):
    client = get_client()
    client.set(key_name, value)

def get_pages(page, total):
    pages = list(range(total))

    pages_first = pages[1:5];
    if page - 3 < 1:
        pages_current = pages[page:page+5]
    else:
        pages_current = pages[page-3:page+5]


    return list(set(pages_first+pages_current))
def get_search_items(query, cat, limit = 10, page = 1):
    key_name = "search_"+ query + "_query_"+ str(cat) + "_" + str(limit) + "_" + str(page)
    result = get_cache(key_name)
    if result:
        items = json.loads(result)
    else:
        start = time.time()
        api = Finding(
            domain = 'svcs.ebay.com',
            appid=config.app_id,
            config_file=None,
            siteid="EBAY-US"
        )

        callData = {
            "categoryId": cat,
            "outputSelector": ["GalleryInfo","PictureURLLarge"],
            "paginationInput": {
                "entriesPerPage": limit,
                "pageNumber": page
            },
            "keywords": urllib.request.unquote(query)

        }

        items = api.execute('findItemsAdvanced', callData).dict()
        send_metric("search_items", time.time() - start)
        set_cache(key_name, json.dumps(items))
    return items

def send_metric(name, value):
    cw = boto3.client('cloudwatch')
    metric =  [
            {
                'MetricName': name,
                'Value': value,
                'Unit': 'Milliseconds',
                'StorageResolution': 60
            },
        ]
    response = cw.put_metric_data(
        Namespace='ebay',
        MetricData=metric
    )
    print(metric)
    return {}

find_api = None;

def init_finding_api():
    global find_api
    if find_api  is  None:
        print("init")
        find_api = Finding(
            domain = 'svcs.ebay.com',
            appid=config.app_id,
            config_file=None,
            siteid="EBAY-US"
        )

    return find_api
