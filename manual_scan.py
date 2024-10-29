import os
from pathlib import Path
from itertools import islice
import enchant

# bunch of global state values
good = []
word_map = []
processed = 0

# state managing
save = Path("manual").with_suffix('.save')
temp = save.with_suffix(".temp")

def load_from_lines(lines):
    global good
    global word_map
    global processed

    a, b, c = lines
    
    good = eval(a)
    word_map = eval(b)
    processed = eval(c)

    types = (isinstance(good, list)
        and  isinstance(word_map, list)
        and  isinstance(processed, int))

    if not types:
        raise TypeError
    
    return good, word_map, processed

def load_state(path):
    with open(path) as file:
        lines = file.readlines()
    load_from_lines(lines)
    return True

def load():
    def load_save():
        if save.exists():
            print("loading from save")
            try:
                return load_state(save)
            except Exception:
                print("corrupted save")
            if temp.exists():
                print("found temp")
                print("loading from temp")
                try:
                    return load_state(temp)
                except Exception:
                    print("corrupted save at temp")
            raise ValueError("corrupted unrecoverable save")
        return False

    load_save()

    with open("freq") as file:
        lines = [*map(parse_line, file.readlines())]
        freq = { word : cnt for (word, cnt) in lines }
        # skip to where we ended
        lines = islice(iter(lines), processed, None)
    return freq, lines

def dump(file):
    file.seek(0)
    file.write(
            str(good)      + "\n" 
        +   str(word_map)  + "\n" 
        +   str(processed) + "\n"
    )
    file.truncate()
    file.flush()
    
def save_progress():
    # first dump to temporary
    with open(temp, "w") as file:
        dump(file)
    # so if data is lost here
    # we can revert back
    with open(save, "w") as file:
        dump(file)

def word_freq(word):
    global freq
    return 0 if word not in freq else freq[word]

# interactive
def ask_commit(word, pair):
    while True:
        os.system('cls||clear')
        if word == pair:
            print(f"keep {word}")
        elif pair is None:
            print(f"drop {word}")
        else:
            words = pair.split()
            print(f"{word} ({word_freq(word)}) ->", end="")
            for x in words:
                print(f" {x} ({word_freq(x)})", end="")
            print()
        result = input("Y/N: ").strip().lower()
        if result == "y":
            return True
        elif result == "n":
            return False

def resolve(pair, results):
    global freq
    while True:
        os.system('cls||clear')
        print(f"processed: {processed}")
        word, cnt = pair
        print("misspelled:", word, cnt)
        for i, r in enumerate(results):
            print(f"{i})", r, f"({word_freq(r)})")
        print("*) custom")
        print("+) keep")
        print("-) drop")

        resolve = input("your decision: ").strip()

        if resolve == '*':
            custom = input().strip()
            if ask_commit(word, custom):
                return word, custom 
        elif resolve == "+":
            if ask_commit(word, word):
                return word, word
        elif resolve == "-":
            if ask_commit(word, None):
                return word, None
        elif resolve.isdigit() and int(resolve) < len(results):
            chosen_word = results[int(resolve)]
            if ask_commit(word, chosen_word):
                return word, chosen_word 

# load parsed words
def parse_line(line):
    word, cnt = line.strip().split()
    return word, int(cnt)

# create spellchecker
russian = enchant.Dict("ru_RU")
freq, lines = load()

for word, cnt in lines:
    os.system('cls||clear')
    print(f"processed: {processed}")

    save_progress()

    if russian.check(word):
        good.append(word)
    elif word.startswith("е") and word.removeprefix("е").isdigit(): 
        # autoresolve most of foodcodes
        # here е is russian
        word_map.append((word, word.replace("е", "e")))
    elif word.startswith("e") and word.removeprefix("e").isdigit(): 
        # autoresolve most of foodcodes
        # here e is english (proper one)
        good.append(word)
    else:
        word, repl = resolve(
            (word, cnt), russian.suggest(word)
        )
        if word == repl:
            good.append(word)
        elif repl is not None:
            word_map.append((word, repl))

    processed += 1
