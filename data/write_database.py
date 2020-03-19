import config


def write_data(text, entities, id_, sent_tokenizer, word_tokenizer):
    tagged_elements = {}
    tokenized_text = tokenize_text(text, sent_tokenizer, word_tokenizer)

    for entity in entities:
        for occurence in entities[entity]:
            offset = occurence[0]
            elements = word_tokenizer.span_tokenize(text[occurence[0]:occurence[1]])
            tag = occurence[2]
            first = True
            for element in elements:
                if first:
                    tagged_elements[(offset + element[0], offset + element[1])] = "B-" + tag
                    first = False
                else:
                    tagged_elements[(offset + element[0], offset + element[1])] = "I-" + tag


    with open(config.paths["CoNLL_folder"] + "{}.CoNLL".format(id_), "w") as out_file:
        for sentence in tokenized_text:
            for token in sentence:
                out_file.write("{}\t{}\n".format(text[token[0]:token[1]], get_label(token, tagged_elements)))
            #out_file.write("\n")


def get_label(token, tagged_elements):
    if token in tagged_elements:
        return tagged_elements[token]
    else:
        return "O"


def split_sentences(sent_tokenizer):
    # return [(sent.start_char, sent.end_char) for sent in sent_tokenizer.sents]
    return [span for span in sent_tokenizer]


def extra_sent_split(sentence, max_length=128):
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


def tokenize_sentence(tokenizer, sentence, offset):
    span_generator = tokenizer.span_tokenize(sentence)
    spans = [(span[0] + offset, span[1] + offset) for span in span_generator]
    return extra_sent_split(spans)


def tokenize_text(text, sent_tokenizer, word_tokenizer):
    offsets = split_sentences(sent_tokenizer.span_tokenize(text))

    sentences = []
    for offset in offsets:
        added_sentences = tokenize_sentence(word_tokenizer, text[offset[0]: offset[1]], offset[0])
        for sentence in added_sentences:
            sentences.append(sentence)

    return sentences
