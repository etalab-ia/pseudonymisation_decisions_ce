"""
Main function to train a NLP model using flair library
"""

from flair.embeddings import TokenEmbeddings, WordEmbeddings, StackedEmbeddings, CharacterEmbeddings, FlairEmbeddings, \
    BertEmbeddings, CamembertEmbeddings
from typing import List
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from flair.visual.training_curves import Plotter
import utils.utils


def train(corpus, embeddings, model_save_path):
    """
    Control the training of a flair model
    TODO: Implement parameters control, finish embedding parametrisation
    :param corpus: Corpus object for training
    :param embeddings: list of embeddings to be used for training
    :param model_save_path: path to save log files
    :return:
    """

    embedding_types: List[TokenEmbeddings] = [

        # WordEmbeddings('fr-crawl'),

        # comment in this line to use character embeddings
        # CharacterEmbeddings(),

        # comment in these lines to use flair embeddings
        FlairEmbeddings('fr-forward'),
        FlairEmbeddings('fr-backward'),

        # bert embeddings
        # BertEmbeddings('bert-base-french')
        CamembertEmbeddings(),

        # CCASS Flair Embeddings FWD
        # FlairEmbeddings('/data/embeddings_CCASS/pavel/flair_language_model/jurinet/best-lm.pt'),

        # CCASS Flair Embeddings BWD
        # FlairEmbeddings('/data/embeddings_CCASS/pavel/flair_language_model/jurinet/best-lm-backward.pt')
    ]

    embeddings: StackedEmbeddings = StackedEmbeddings(embeddings=embedding_types)

    train_object = create_trainable_object(corpus, embeddings)

    trainer: ModelTrainer = ModelTrainer(train_object, corpus)
    trainer.num_workers = utils.utils.available_cpu_count()
    # 7. start training config à mettre en place
    trainer.train(model_save_path,
                  learning_rate=0.1,
                  mini_batch_size=128,
                  max_epochs=150,
                  anneal_factor=0.5,
                  patience=5,
                  checkpoint=True,
                  embeddings_storage_mode="cpu")

    create_train_plot(model_save_path)


def create_trainable_object(corpus, embeddings, task="ner"):
    """ Create train object specific to task. Only NER implemented"""

    tag_dictionary = corpus.make_tag_dictionary(tag_type=task)

    if task == "ner":
        tagger: SequenceTagger = SequenceTagger(hidden_size=256,
                                                embeddings=embeddings,
                                                tag_dictionary=tag_dictionary,
                                                tag_type=task,
                                                use_crf=True)

        return tagger


def create_train_plot(model_save_path):
    """ Plot train logs """

    plotter = Plotter()
    plotter.plot_weights(model_save_path + 'weights.txt')

if __name__ == '__main__':

    create_train_plot("/Users/thomasclavier/Documents/Projects/Etalab/models/baseline_ner3/")