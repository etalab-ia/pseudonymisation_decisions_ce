"""
Once the CoNLL files have been generated, split these files in train, validation and test. Trying to keep the
distribution of tags stratified (same proportion in each split).
"""

import glob
from collections import defaultdict
import numpy as np
import re


def count_tags(conll_paths, tags):
    """
    Count tags in list of CoNLL files
    :param conll_paths: Path to CoNLL files
    :param tags: list of tags of interest
    :return: file_tag_counts: dict: keys are file paths, value are tuples (tag, number of occurrence in file)
    :return: tag_file_counts: dict:  keys are tags, values are tuple (file path, number of occurrence in file)
    :return: totals_dict: dict: keys are tags, value are total number of tag occurrence in corpus
    TODO: Add tag discoverer function by default if all tags are used
    """
    file_tag_counts = defaultdict(list)
    tag_file_counts = defaultdict(list)
    for path in conll_paths:
        with open(path) as filo:
            content = filo.read()
            for tag in tags:
                findo = re.findall(tag, content)
                if findo:
                    file_tag_counts[path].append((tag[2:], len(findo)))
                    tag_file_counts[tag[2:]].append((path, len(findo)))

    totals_dict = defaultdict(int)
    for file_path, tags_count in file_tag_counts.items():
        for tag in tags_count:
            totals_dict[tag[0]] += tag[1]
    return file_tag_counts, tag_file_counts, totals_dict


def get_min_class_samples(tag_file_counts, min_class_count=("", -1)):
    """

    :param tag_file_counts: dict:  keys are tags, values are tuple (file path, number of occurrence in file)
    :param min_class_count: tuple (tag of interest, minimum number of occurence in corpus)
    :return: list of files containing min_class_count[1] occurrences of tag min_class_count[0]
    """
    if min_class_count[1] == -1:
        files = []
        for tag in tag_file_counts:
            files += list(set([element[0] for element in tag_file_counts[tag]]))

        return list(set(files))

    min_sample = []
    sum_min_tags = 0
    min_class_files = tag_file_counts[min_class_count[0]]
    min_class_files = min_class_files
    i = 0

    while sum_min_tags < min_class_count[1]:
        min_sample.append(min_class_files[i][0])
        sum_min_tags += min_class_files[i][1]
        i += 1
    # _, _, counts = count_tags(min_sample, tags)

    return min_sample


def split_sets(sample_paths, proportions):
    """ Return train test dev dataset"""

    print(f"Number of files to use {len(sample_paths)}")
    train_p, dev_p, test_p = proportions
    train = np.random.choice(sample_paths, size=int(len(sample_paths) * train_p), replace=False)
    print(f"Number of files in train {len(train)}")
    dev_test = list(set(sample_paths) - set(train))
    dev = np.random.choice(dev_test, size=int(len(sample_paths) * dev_p), replace=False)
    test = list(set(dev_test) - set(dev))
    print(f"Number of files in dev {len(dev)}")
    print(f"Number of files in test {len(test)}")
    return train, dev, test


def save_datasets(train, dev, test, train_dev_test_folder):
    """
    Save train, test, dev datasets to target location
    """

    for name, dataset in {"train": train, "dev": dev, "test": test}.items():

        with open(train_dev_test_folder + name, 'w') as outfile:
            for path in dataset:
                with open(path) as infile:
                    outfile.write(infile.read())
                    outfile.write("\n")


def create_training_dataset(conll_files_path, training_set_path, tags, min_class_count=("", -1),
                            proportions=(.80, .10, .10)):
    """
    Creates train test and validation datasets for training from list of conll files.

    :param tags: List of tags of interest
    :param conll_files_path: path to the conll files
    :param training_set_path: target path for train test dev sets
    :param min_class_count: tuple : set minimum number of instances to be used for given tag
    :param proportions: tuple : specifies proportions of files allocated to train test dev
    :return: None: Creates dataset to target folder
    """
    annotation_conll_paths = glob.glob(conll_files_path + "*.CoNLL", recursive=True)
    file_tag_counts, tag_file_counts, counts = count_tags(annotation_conll_paths, tags)
    sample_paths = get_min_class_samples(tag_file_counts, min_class_count)
    train, dev, test = split_sets(sample_paths, proportions)
    save_datasets(train, dev, test, training_set_path)
