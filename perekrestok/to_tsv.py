from collections import Counter

with open("raw_data", "r") as file:
    data = eval(file.read())

def make_row(category, item):
    result = {}
    
    result['category'] = category
    result['group']    = item['group']
    result['title']    = item['title']
    result['href']     = item['href']
    
    info = item['info']
    result['contains'] = info['contains']
    # parse calories and proteins, fats, etc
    if 'cal' in info:
        result['cal (gr)'] = info['cal']
        for type in ('f', 'p', 'c'):
            if type not in info:
                result[f'{type} (gr)'] = 0
            else:
                if info[type][1] != 'гр':
                    print(f"expected grams in {type}")
                    breakpoint()
                result[f'{type} (gr)'] = info[type][0]
    
    if item['size']:
        value, kind = item['size']
        if kind == "гр":
            result['size (gr)'] = value
        elif kind == "мл":
            result['size (gr)'] = value
        else:
            print("unexected size format")
            breakpoint()

    if item['price']:
        value, kind = item['price']
        if kind == "шт":
            result['price (rub/kg)'] = round(1000 * (value / result['size (gr)']), 2)
        elif kind == "кг":
            result['price (rub/kg)'] = value
        else:
            print("unexpected kind of price")
            breakpoint()

    result |= info['words']

    return result


rows = []
for category in data:
    for item in data[category]:
        rows.append(make_row(category, item))


headers = [ 'title'           
           ,'category'
           ,'group'   
           ,'price (rub/kg)'
           ,'size (gr)'
           ,'cal (gr)'
           ,'f (gr)'
           ,'p (gr)'
           ,'c (gr)'
           ,'href'    
           ,'contains']
words = []
for row in rows:
    for header in row:
        if header not in headers and header not in words:
            words.append(header)
def nl_tab(str):
    return str.replace("\t", " ").replace("\n", " ")

merged = headers + words

with open("data.tsv", "w") as file:
    file.write("\t".join(map(nl_tab, map(str, merged))))
    file.write("\n")

    for row in rows:
        result = []
        for header in merged:
            if header in row:
                result.append(row[header]) # there exist value
            elif header in headers:
                result.append(None) # headers
            else:
                result.append(0) # words
        file.write("\t".join(map(nl_tab, map(str, result))))
        file.write("\n")
