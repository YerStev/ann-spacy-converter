import spacy
import nltk

def lower_text(text):
    return text.lower()


def replace_special_chars_with_space(text):
    removal_list = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+',
    '[', ']', '{', '}', '\\', '|', ';', ':', '\'', '\"', ',', '.', '<', '>',
    '/', '?', '`', '~', '§', '±', '©', '®', '™', 'µ', '¢', '£', '¥', '€', '₹',
    '°', '∆', '∞', '∑', 'π', '≠', '≤', '≥', '√', '±', '×', '÷', '¼', '½', '¾',
    '∫', '∂', '∇', '∈', '∉', '⊆', '⊂', '⊇', '⊃', '∪', '∩', '∅', '∀', '∃',
    '∴', '∵', '¬', '∨', '∧']

    for r in removal_list:
        text = text.replace(r, ' ')
    return text


def remove_line(text):
    return text.replace('\n', ' ')
     

def replace_umlauts(text):
    text = text.replace("ü", "ue")
    text = text.replace("Ü", "Ue")
    text = text.replace("ä", "ae")
    text = text.replace("Ä", "Ae")
    text = text.replace("ö", "oe")
    text = text.replace("Ö", "Oe")
    text = text.replace("ß", "ss")
    return text


def remove_tab(text):
    text = text.replace('\t', ' ')
    return ' '.join(text.split())


def lemmatize_text(text):
    nlp = spacy.load('de_core_news_sm')
    doc = nlp(text)
    lemmas = []
    for token in doc:
        if not token.is_punct:
            lemmas.append(token.lemma_)
    text = ' '.join(lemmas).lower()
    return text


def stem_text(text):
    porter = nltk.PorterStemmer()
    words = text.lower().split(' ')
    stemmas = [porter.stem(w) for w in words]
    return ' '.join(stemmas)


def remove_stopwords(text):
    # nltk.download('stopwords')
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('german'))
    tokens = text.split()
    tokens_filtered = [word for word in tokens if not word in stop_words]
    return (" ").join(tokens_filtered)


