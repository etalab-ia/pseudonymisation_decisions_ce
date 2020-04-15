import flair
import torch
from flair.models import SequenceTagger
from nltk.tokenize import WordPunctTokenizer, PunktSentenceTokenizer

flair.device = torch.device('cpu')

word_tokenizer = WordPunctTokenizer()
tagger = SequenceTagger.load('fr-ner')
sent_tokenizer = PunktSentenceTokenizer("nltk_data/tokenizers/punkt/french.pickle")
