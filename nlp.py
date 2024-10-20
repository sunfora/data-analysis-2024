import nltk
from nltk.tokenize import word_tokenize
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

def remove_symbols(text):
    text = text.lower()
    return "".join(
        e if '0' <= e <= '9' 
          or 'a' <= e <= 'z' 
          or 'а' <= e <= 'я'
          else " " for e in text)

def get_words(text):
    text = remove_symbols(text) 
    tokens = word_tokenize(text, language='russian')
    tagged = nltk.pos_tag(tokens, lang='rus')
    words = [
        word for (word, tag) in tagged if 
        'S' in tag or 'A' in tag
    ]
    second_pass = [morph.parse(x)[0] for x in words] 
    normalized = [x.normal_form for x in second_pass]
    return set(normalized)

def food_codes(text):
    text.lower()

if __name__ == "__main__":
    print(get_words("""
Мука пшеничная общего назначения, сахар, жир кондитерский (рафинированные дезодорированные растительные масла: пальмовое, подсолнечное: антиокислители: Е319, лимонная кислота), какао-порошок, крахмал кукурузный, эмульгатор: лецитин соевый, продукты яичные сухие: меланж, какао-масло, соль, разрыхлители: карбонаты натрия, карбонаты аммония, ароматизатор: шоколад молочный, вода.
"""))
