import os
import json
from run.tokenization import nltk_word_punk_tokenize
from doccano_api import client_server


def instantiate_client(url='http://0.0.0.0/', user='admin', password='password'):
    """ The Doccano client """
    doccano_client = client_server.DoccanoClient(
        url,
        user,
        password
    )
    return doccano_client


def upload_file(client, project_id, file_path):
    """ Upload file to project """
    client.post_doc_upload(project_id, "conll", os.path.basename(file_path), os.path.dirname(file_path))


def clean_labels(client, project_id, tags):
    """ Clean tags after file upload ("O" tags and correct colors)"""
    response = client.get_label_list(project_id)
    for elem in response.json():
        if elem["text"] == "O":
            client.delete_label(project_id, elem["id"])

        elif "_vs_" in elem["text"]:
            client.patch_label_color(project_id, "#FF0000", elem["id"])

        elif elem["text"] in tags:
            client.patch_label_color(project_id, "#7CFC00", elem["id"])


def download_doccano_dataset_as_conll(client, project_id, tokenizer, validated):
    """
    Download Doccano dataset as a conll database
    :param validated: if True only use files with validated annotations
    :param client: doccano client
    :param project_id: doccano project id
    :param tokenizer: chosen tokenizer
    :return: list of list, each list describing a conll file
    """

    conll_database = []
    ret = client.get_doc_download(project_id)
    jsonable = ret.content.split(b"\n")
    labels = {elem["id"]: elem["text"] for elem in client.get_label_list(project_id).json()}
    for doc in jsonable:
        if doc:
            doc = json.loads(doc)
            if doc["annotation_approver"] or not validated:
                spans, text = nltk_word_punk_tokenize(doc["text"], tokenizer)
                annotations = {(i["start_offset"], i["end_offset"]): labels[i["label"]] for i in doc["annotations"]
                               if (i["start_offset"], i["end_offset"]) in spans}
                conll = []
                for span in spans:
                    if span in annotations:
                        conll.append("{} \t {}".format(text[span[0]:span[1]], annotations[span]))
                    else:
                        conll.append("{} \t {}".format(text[span[0]:span[1]], "O"))

                conll_database.append(conll)

    return conll_database
