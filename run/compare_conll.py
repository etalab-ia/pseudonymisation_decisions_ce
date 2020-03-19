"""
Routine function comparing CoNLL, output discrepencies and preparing for Doccano upload
"""


def compare_conll(path_1, path_2):
    """
    Return compared CoNLL object : two compared CoNLL as a list of tuples (token, label) with label as string where
    matching and as tuple (label_file1, label_file2) where not matching
    """
    file_1 = load_conll(path_1)
    file_2 = load_conll(path_2)

    if assert_matching_conll(file_1, file_2):
        matched_conll = []
        for i, j in zip(file_1, file_2):
            if i.split()[1] == j.split()[1]:
                matched_conll.append((i.split()[0], i.split()[1]))
            else:
                matched_conll.append((i.split()[0], (i.split()[1], j.split()[1])))

        return matched_conll


def create_compared_conll_file(path_1, path_2, target_path):
    """
    Write results of two compared CoNLL as a new CoNLL file with newly created labels label_file1_vs_label_file2
    where not matching for doccano upload
    """
    file_1 = load_conll(path_1)
    file_2 = load_conll(path_2)

    if assert_matching_conll(file_1, file_2):
        with open(target_path, "w") as fout:
            for i, j in zip(file_1, file_2):
                if i.split()[1] == j.split()[1]:
                    fout.write(i)
                else:
                    fout.write(i.split()[0] + "\t" + "{}_vs_{}\n".format(i.split()[1], j.split()[1]))

        return None


def score_conll(matched_conll):
    """
    Create scorecard for two compared CoNLL indicated percent of macths and type of mismatchs
    :param matched_conll: compared CoNLL object
    :return: scorecard
    """

    total_score = 0
    added_label = 0
    missed_label = 0
    mismatchs = 0

    for token in matched_conll:
        if len(token[1]) > 1:
            if token[1][0] == "O":
                added_label += 1
            elif token[1][1] == "O":
                missed_label += 1
            else:
                mismatchs += 1

            total_score += 1

        else:
            if token[1] != "O":
                total_score += 1

    score_card = {
        "accuracy": 1 - (added_label + missed_label + mismatchs) / total_score,
        "added_label": added_label / (added_label + missed_label + mismatchs),
        "missed_label": missed_label / (added_label + missed_label + mismatchs),
        "mismatch": mismatchs / (added_label + missed_label + mismatchs),
    }

    return score_card


def load_conll(path):
    """ Load CoNLL file as list of strings"""
    conll = []
    with open(path, "r") as f1:
        print()
        for line in f1:
            conll.append(line)

    return conll


def assert_matching_conll(conll_1, conll_2, match_score=0.75):
    """
    Check if CONLL files have the same structure or if modifications are necessary
    :param conll_1: First CoNLL
    :param conll_2: Second CoNLL
    :param match_score: overlap score above which re alignment operation should be performed or tokenization reviewed
    :return: True CoNLL perfectly aligned
    """
    matching = True

    for i, j in zip(conll_1, conll_2):
        if i.split()[0] != j.split()[0]:
            matching = False

    if not matching:
        setA = set([i[0] for i in conll_1])
        setB = set([i[0] for i in conll_2])
        overlap = setA & setB
        union = setA | setB
        if float(len(overlap)) / len(union) > match_score:
            # raise something
            print("CoNLL files don't match perfectly but seem close, check tokenization for discrepencies")
        else:
            # raise something
            print("CoNLL files don't match")

    return matching
