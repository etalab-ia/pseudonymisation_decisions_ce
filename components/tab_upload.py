import base64
from hashlib import md5
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from flair.models import SequenceTagger

from dash_interface.data_ETL import load_text, create_upload_tab_html_output

TEXTE_EXEMPLE = """
        Lecture du mercredi 28 février 2018
REPUBLIQUE FRANCAISE

AU NOM DU PEUPLE FRANCAIS


Vu la procédure suivante :

Mme Aleron Landry, demeurant au 123 rue Fausse Ville-Fantastique-Sur-Saône, a demandé au juge des référés du tribunal 
administratif de Poitiers, sur le fondement de l'article L. 521-1 du code de justice administrative, de suspendre 
l'exécution de la décision du 21 juillet 2012 par laquelle le recteur de l'académie de Bordeaux a rejeté sa demande 
d'inscription en première année de licence de sciences et techniques des activités physiques et sportives (STAPS) à 
l'université de Bordeaux pour l'année 2002/2003 et d'enjoindre au recteur de l'inscrire temporairement au sein de 
cette formation dans un délai de quinze jours, sous une astreinte de 10 euros par jour de retard. 

Par une ordonnance n° 1703763 du 21 mars 2011, le juge des référés du tribunal administratif a suspendu 
l'exécution de cette décision et a enjoint au recteur de l'académie de Bordeaux de procéder à l'inscription de Mme 
Landry en première année de licence de STAPS dans l'attente qu'il soit statué au fond sur sa légalité. 

Par un pourvoi, enregistré le 3 janvier 2009 au secrétariat du contentieux du Conseil d'Etat, la ministre de 
l'enseignement supérieur, de la recherche et de l'innovation demande au Conseil d'Etat d'annuler cette ordonnance. """

tagger = SequenceTagger.load('/home/pavel/code/pseudo_conseil_etat/models/flair_embeds/1600_200_200/best-model.pt')

tab_upload_content = dbc.Tab(
    label='Données',
    tab_id="tab-upload",
    children=html.Div(className='control-tab', children=[
        html.Div("Veuillez choisir un fichier à analyser (type .doc, .docx, .txt. Max 200 Ko)",
                 className='app-controls-block'),
        html.Div(
            id='seq-view-fast-upload',
            children=dcc.Upload(
                id='upload-data',
                className='control-upload',
                max_size="200000",  # 200 kb
                children=html.Div([
                    "Faire glisser ou cliquer pour charger un fichier"
                ]),
            ),
        ),
        html.Div(["Ou ", html.B("lancez le texte exemple", id="exemple-text")],
                 className='app-controls-block'),

    ])
)


def pane_upload_content(contents, file_name, n_clicks, data):
    if contents is None and n_clicks is None:
        data = data or {"n_clicks": 0}
        return html.Div("Chargez un fichier dans l'onglet données pour le faire apparaitre pseudonymisé ici",
                        style={"width": "100%", "display": "flex", "align-items": "center",
                               "justify-content": "center"}), data
    if n_clicks is not None and n_clicks > data["n_clicks"]:
        decoded = TEXTE_EXEMPLE
        content_id = md5(decoded.encode("utf-8")).hexdigest()
        data = data or {content_id: []}
        data["n_clicks"] = n_clicks
        if content_id in data and data[content_id]:
            children = data[content_id]
            return children, data
    else:
        file_name, extension = file_name.split(".")
        temp_path = f"/tmp/output.{extension}"
        content_type, content_string = contents.split(',')

        content_id = md5(content_string.encode("utf-8")).hexdigest()

        data = data or {content_id: []}
        if content_id in data and data[content_id]:
            children = data[content_id]
            return children, data

        # If we do not have it stored, compute it
        decoded = base64.b64decode(content_string)

        f = open(temp_path, 'wb')
        f.write(decoded)
        f.close()
        decoded = load_text(temp_path)

    html_pseudoynmized, html_tagged = create_upload_tab_html_output(text=decoded, tagger=tagger)

    pseudo_content = dbc.Card(dbc.CardBody(html_pseudoynmized), className="mt-3",
                            style={"maxHeight": "750px", "overflow-y": "scroll"})

    tagged_content = dbc.Card(dbc.CardBody(html_tagged), className="mt-3",
                            style={"maxHeight": "750px", "overflow-y": "scroll"})

    children = dbc.Tabs(
        [
            dbc.Tab(tagged_content, label="Document annotée"),
            dbc.Tab(pseudo_content, label="Document pseudonymisé"),
        ]
    )

    # data.clear()
    data = {"n_clicks": data["n_clicks"], content_id: children}
    # data = {"n_clicks": n_clicks}
    return children, data
