from nltk.tokenize import WordPunctTokenizer, PunktSentenceTokenizer
from flair.models import SequenceTagger

word_tokenizer = WordPunctTokenizer()
tagger = SequenceTagger.load('fr-ner')
sent_tokenizer = PunktSentenceTokenizer("nltk_data/tokenizers/punkt/french.pickle")