from bs4 import BeautifulSoup
import requests
from pathlib import Path
from time import sleep, time
from random import random
import string
import re
import os

from nlp import get_words 


root = 'https://www.perekrestok.ru'
sweeties = '/cat/mc/187/sokolad-konfety-sladosti'

def part_name(url):
    return url.rsplit('/', 1)[-1] + ".html"

LAST_HIT = time()

def load(part, verbose=True):
    global LAST_HIT

    def log(*args, **kwargs):
        if verbose:
            print(*args, **kwargs)

    log(f"loading page: {part}")
    cache = Path("cache")
    part_dir = cache / part.lstrip('/') 
    part_file = part_dir / part_name(part)
    if part_file.exists():
        log("[done] found in cache")
        with open(part_file) as cached:
            return cached.read()
    else:
        log("downloading...")
        while True:
            if time() - LAST_HIT < 3:
                sleep(3 + random())
            LAST_HIT = time()
            try:
                result = requests.get(root + part)
                if result.status_code == 200:
                    text = result.text
                    part_dir.mkdir(
                        parents=True, exist_ok=True
                    )
                    with open(part_file, "w") as file:
                        file.write(text)
                    log("[done] downloaded")
                    return text 
            except requests.exceptions.RequestException as err:
                print(f"failed to grab {part}")
                print("falling into debugger")
                breakpoint()

def load_html(part):
    return BeautifulSoup(load(part), features="lxml")

page = load_html(sweeties)

def categories(page):
    for x in page.select("a.products-slider__header"):
        yield x['href'], x.find("h2").text

def products(page):
    for title in page.select(".catalog-content-group__title"):
        group = title.find_parent("div")
        group_title = title.text
        for card in group.select(".product-card-wrapper"):
            a = card.select_one(
                ".product-card__link"
            )
            div = card.select_one(
                ".product-card__title"
            )
            size = card.select_one(
                ".product-card__size"
            )
            if size:
                size = size.text
            price = card.select_one(
                ".product-card__pricing"
            )
            if price:
                price = price.text
            href = a['href']
            title = div.text

            yield {
               "href" : href, 
               "title" : title, 
               "group" : group_title, 
               "size" : size, 
               "price" : price
            }

def parse_grams(str):
    str = str.strip()
    for suffix in ["г", "г.", "грамм"]:
        try:
            return float(str.removesuffix(suffix))
        except ValueError:
            pass
    return None

def parse_kilograms(str):
    str = str.strip()
    for suffix in ["кг", "кг.", "килограмм"]:
        try:
            return float(str.removesuffix(suffix)) * 1000
        except ValueError:
            pass
    return None

def product_info(result):
    page = load_html(result["href"])

    calories = ".product-calories-item"

    for item in page.select(calories):
        value_elem = item.select_one(f"{calories}__value")
        title_elem = item.select_one(f"{calories}__title")
        value = value_elem.text.strip()
        title = normalize_name(title_elem.text)
        if title == "калории":
            result['cal'] = float(value)
        else:
            table = {
                "белки" : "p",
                "жиры" : "f",
                "углеводы" : "c"
            }
                
            title = table[title]

            result[title] = parse_grams(value)
            assert result[title] is not None
    
    h2 = page.select_one(
        'h2:-soup-contains("Состав:")'
    )
    if h2 is None:
        result["contains"] = None
    else:
        p = h2.find_next("p")
        if p is None:
            result["contains"] = None
        else:
            result["contains"] = p.text

    return result

def normalize_name(name):
    tr = {x : "" for x in string.punctuation}
    tr[" "] = "-"
    tr = str.maketrans(tr)
    return name.strip().translate(tr).lower()

def grab_data():

    already_collected = []
    elems = {} 

    def dump(c_name=None, i=None):
        os.system('cls||clear')
        print("—————————— DONE ———————————")
        print(len(elems))
        print(already_collected)
        print("———————————————————————————")
        print(c_name, i)
        print("—————————— INFO ———————————")

    result = {}
    for c_href, c_name in categories(page):
        dump(c_name)
        c_html = load_html(c_href)
        result[c_name] = []
        for i, product in enumerate(products(c_html)):
            dump(c_name, i)
            product_info(product)
            if product["contains"] is not None: 
                for noun in get_words(product["contains"]):
                    if noun in elems:
                        elems[noun] += 1
                    else:
                        elems[noun] = 1
            result[c_name].append(
                product
            )
        already_collected.append((c_name, i))

    dump()
    return elems, result

elems, data = grab_data()

with open("freq", "w") as file:
    file.write("\n".join([f"{noun} {elems[noun]}" for noun in elems]))

from nltk.metrics.distance import edit_distance

elems = {
    x : elems[x] 
    for x in elems if len(x) > 1
}

def sieve(elems):
    map = {}
    result = {}
    for i, elem in enumerate(elems):
        max_root = elem
        for root in elems:
            bigger = elems[root] >= elems[max_root] 
            if bigger and ((root in elem and edit_distance(root, elem) <= len(elem) / 2) or (edit_distance(root, elem) <= 2)):
                max_root = root
        map[elem] = max_root
        print(i, len(elems), end="\r")
    return map

def combine(map, elems):
    result = {}
    for elem in elems:
        root = elem
        while map[root] != root: 
            root = map[root]
        if root not in result:
            result[root] = elems[root]
        if root == elem:
            continue
        result[root] += elems[elem]
    return result
