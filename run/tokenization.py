"""
Specific module for tokenization
"""


def nltk_word_punk_tokenize(text, tokenizer):
    """ Tokenization function for nltk word punct tokenizer """
    span_generator = tokenizer.span_tokenize(text)
    spans = [span for span in span_generator]

    return spans


def generate_pseudo_text(text, spans):
    pseudo_text = " ".join([text[span[0]:span[1]].lower() for span in spans])

    return pseudo_text

def nltk_sentence_tokenize(tokenizer, sentence, offset):
    """ Tokenize sentence using nltk sentence tokenizer """
    span_generator = tokenizer.span_tokenize(sentence)
    spans = [(span[0] + offset, span[1] + offset) for span in span_generator]
    return extra_sent_split(spans)


def tokenize_text(text, sent_tokenizer, word_tokenizer):
    """
    Tokenize text according to chosen tokenizers
    :param text: Original text
    :param sent_tokenizer: Sentence tokenizer
    :param word_tokenizer: Word tokenizer
    :return: list of tokenized sentences
    # TODO : Allow addition of other tokenizers, only nltk supported
    """
    offsets = split_sentences(sent_tokenizer.span_tokenize(text))

    sentences = []
    for offset in offsets:
        added_sentences = nltk_sentence_tokenize(word_tokenizer, text[offset[0]: offset[1]], offset[0])
        for sentence in added_sentences:
            sentences.append(sentence)

    return sentences


def split_sentences(sent_tokenizer):
    return [span for span in sent_tokenizer]


def extra_sent_split(sentence, max_length=128):
    """
    Do extra split if sentence is longer than max_length tokens. Splits are chosen automatically in order to :
        - Have as few splits as possible
        - Havce equal length splited sentences
    :param sentence: orignal sentence
    :param max_length: maximum number of tokens
    :return: list: list of splited sentences
    """
    # TODO:split un peu hacky à refaire
    if len(sentence) < max_length:
        return [sentence]
    else:
        splitted_sentences = []
        nb_chunks = len(sentence) // max_length + 1
        len_chunks = len(sentence) // nb_chunks + 1
        for i in range(0, len(sentence), len_chunks):
            splitted_sentences.append(sentence[i:i + len_chunks])

        return splitted_sentences
