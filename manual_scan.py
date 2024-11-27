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

def clear_screen():
    os.system('cls||clear')


# interactive
def ask_commit(word, pair):
    while True:
        clear_screen()
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
        clear_screen()
        print(f"processed: \033[93m{processed}\033[0m")
        word, cnt = pair
        print("misspelled:", word, cnt)
        for i, r in enumerate(results):
            if russian.is_added(r):
                print(f"{i}) \033[92m{r}\033[0m ({word_freq(r)})")
            else:
                print(f"{i}) \033[94m{r}\033[0m ({word_freq(r)})")
        print("*) custom")
        print("+) keep")
        print("-) drop")
        print("w) google in w3m")
        print("f) google in firefox")

        resolve = input("your decision: ").strip()
        if resolve == 'w':
            run(f"w3m https://google.com/search?q={word}")
        elif resolve == "f":
            run(f"firefox https://google.com/search?q={word}")
        elif resolve == '*':
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

for word in good:
    russian.add_to_session(word)
for _, r in word_map:
    for word in r.split():
        russian.add_to_session(word)

failureOCV = str.maketrans("ykehxapocmtb", "укенхаросмтв")
try:
    for word, cnt in lines:
        clear_screen()
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
            russian.add_to_session(word)
        elif russian.check(ocv := word.translate(failureOCV)):
            word_map.append((word, ocv))
        else:
            suggested = russian.suggest(word) 
            prefixed = [*set(
                [wrd for wrd in good if wrd.startswith(word)] +
                [wrd for _, r in word_map 
                     for wrd in r.split() 
                     if wrd.startswith(word)]
            )]
            
            for wrd in prefixed:
                if wrd not in suggested:
                    suggested.append(wrd)

            word, repl = resolve(
                (word, cnt), 
                suggested
            )
            if word == repl:
                good.append(word)
                russian.add_to_session(word)
            elif repl is not None:
                word_map.append((word, repl))
                for wrd in repl.split():
                    russian.add_to_session(wrd)

        processed += 1
except KeyboardInterrupt:
    clear_screen()
    print(f"Done: \033[5;93m{processed}\033[0m")
    pass
