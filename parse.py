from bs4 import BeautifulSoup
import requests
from pathlib import Path
from time import sleep, time
from random import random
import string
import re
import os

from collections import Counter 

from nlp import get_words, after_manual_scan

get_words = after_manual_scan(get_words)


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
    """
    Iterates over categories and their names
    """
    for cat in page.select("a.products-slider__header"):
        if not cat.has_attr('href'):
            print("cannot find link to the category")
            breakpoint()
        h2 = cat.find("h2")
        if not h2:
            print("cannot find name of the category")
            breakpoint()
        yield cat['href'], h2.text

def products(page):
    """
    Iterates over products in a category.

    Each product will contain raw data found on product-card for:
        title, price, size, link
    """
    for title in page.select(".catalog-content-group__title"):
        group = title.find_parent("div")
        if not group:
            print("cannot find group")
            breakpoint()
        group_title = title.text

        for card in group.select(".product-card-wrapper"):
            s = {
                'link': ".product-card__link",
                'title': ".product-card__title",
                'size': ".product-card__size",
                'price': ".product-card__pricing"
            }
            select = lambda name: card.select_one(s[name])
            # grap href
            # must not fail
            a = select('link')
            if not a:
                print("link not found")
                breakpoint()
            if not a.has_attr('href'):
                print("href property is not present in anchor")
                breakpoint()
            href = a['href']

            # grap title
            # must not fail
            title = select('title')
            if not title:
                print("cannot find product title")
                breakpoint()
            title = title.text

            # size can be absent
            if size:=select('size'):
                size = size.text 
                try:
                    size = parse_size(size)
                except ValueError:
                    print("unexpected size format")
                    breakpoint()

            
            # price can be absent
            if price:=select('price'):
                price = price.text
                try:
                    price = parse_price(price)
                except ValueError:
                    print("unexpected price format")
                    breakpoint()

            yield {
               "href" : href, 
               "title" : title, 
               "group" : group_title, 
               "size" : size, 
               "price" : price
            }

def product_info(page):
    """ grab data for product """

    info = {}

    calories = ".product-calories-item"

    for item in page.select(calories):
        value_elem = item.select_one(f"{calories}__value")
        if not value_elem:
            print(
            """
            cannot find value 
            for nutrition description
            """)
            breakpoint()

        title_elem = item.select_one(f"{calories}__title")
        if not title_elem:
            print(
            """
            cannot find title of 
            nutrition description
            """)
            breakpoint()

        value = value_elem.text.strip()
        title = normalize_name(title_elem.text)
        
        if "калории" in title:
            try:
                info['cal'] = float(value)
            except ValueError:
                print("unexpected format for calories")
                breakpoint()
        else:
            table = {
                "белки" : "p",
                "жиры" : "f",
                "углеводы" : "c"
            }
            if title not in table:
                print("unxpected title")
                breakpoint()
            try:
                info[table[title]] = parse_pfc(value)  
            except ValueError:
                print(f"unexpected format for {title}")
                breakpoint()
    
    info['contains'] = None
    info['words'] = Counter()
    
    contains_sel = 'h2:-soup-contains("Состав:")'
    
    if h2:=page.select_one(contains_sel):
        if p:=h2.find_next("p"):
            info['contains'] = p.text
            info['words'] = Counter(get_words(info['contains'])) 
    return info 

def normalize_name(name):
    tr = {x : "" for x in string.punctuation}
    tr[" "] = "-"
    tr = str.maketrans(tr)
    return name.strip().translate(tr).lower()

def grab_data():

    already_collected = []
    frequencies = Counter() 

    def dump(c_name=None, i=None):
        os.system('cls||clear')
        print("—————————— DONE ———————————")
        print(len(frequencies))
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
            
            p_html = load_html(product['href'])
            info = product_info(p_html)
            
            product['info'] = info
            frequencies += info['words']

            result[c_name].append(
                product
            )
        already_collected.append((c_name, i))

    dump()
    return frequencies, result

def extract_float(price):
    result = []
    for c in price.replace(",", "."):
        if c.isdigit() or c == '.':
            result.append(c)
    return float("".join(result))

def parse_pfc(value):
    if "гр" in value or "г" in value:
        return extract_float(value), "гр"
    raise ValueError


def parse_size(size):
    if "гр" in size:
        return extract_float(size), "гр"
    elif "мл" in size:
        return extract_float(size), "мл"
    raise ValueError

def parse_price(price):
    if "шт" in price:
        return extract_float(price), "шт"
    elif "кг" in price:
        return extract_float(price), "кг"
    raise ValueError

elems, data = grab_data()
with open("word_freq", "w") as file:
    file.write("\n".join([f"{noun} {elems[noun]}" for noun in elems]))
with open("raw_data", "w") as file:
    file.write(str(data))
