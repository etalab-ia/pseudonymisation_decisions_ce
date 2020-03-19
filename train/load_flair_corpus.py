from flair.data import Corpus
from flair.datasets import ColumnCorpus


def create_flair_corpus(data_folder, column_format, percentage=1, only_downsample_train=True):

    """
    Instantiates a Corpus from CoNLL column-formatted task data such as CoNLL03 or CoNLL2000.

    :param data_folder: base folder with the task dat
    :param column_format: a map specifying the column format
    :param percentage: Percentage of corpus to be used for training
    :param only_downsample_train: Only apply downsample to training set (recommended)
    :return: a Corpus with annotated train, dev and test data
    """

    corpus: Corpus = ColumnCorpus(data_folder, column_format,
                                  train_file='train',
                                  test_file='test',
                                  dev_file='dev',
                                  in_memory=False)

    if percentage < 1:
        corpus.downsample(percentage=percentage, only_downsample_train=only_downsample_train)

    return corpus



