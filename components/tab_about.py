import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc

QUOI = dcc.Markdown("""
La pseudonymisation est un traitement de données personnelles réalisé de manière à ce qu'on ne puisse plus attribuer les
données relatives à une personne physique sans avoir recours à des informations supplémentaires. 
En pratique, **la pseudonymisation consiste à remplacer les données directement identifiantes d’un jeu 
de données par des données indirectement identifiantes**. 
""")

POURQUOI = dcc.Markdown("""
La loi [n°2016-1321](https://www.legifrance.gouv.fr/affichLoiPubliee.do?idDocument=JORFDOLE000031589829&type=general&legislature=14)
pour une République numérique fait de l’ouverture des données publiques la règle par défaut. Cela dit,
l'occultation préalable des éléments à caractère personnel est [une obligation légale](https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000033205514&cidTexte=LEGITEXT000031366350&dateTexte=20161009)
qui s’impose aux administrations.
Afin de faciliter l'ouverture au grand public, une solution automatisée de pseudonymisation, comme celle-ci, est donc
souhaitable pour faire face à la grande quantité des documents à traiter dans un temps raisonnable. 
""")

COMMENT = dcc.Markdown("""
La pseudonymisation peut être vu comme un problème de traitement de langage naturel, plus particulièrement,
comme une tache de [reconnaissance d'entités nommées](https://fr.wikipedia.org/wiki/Reconnaissance_d%27entit%C3%A9s_nomm%C3%A9es)
(REN). La REN est souvent résolue à l'aide des méthodes d'apprentissage supervisé séquentiel. Cette démo utilise une approche de ce type,
c'est-à-dire, nous avons entraîné un modèle en utilisant des décisions de justice annotées indirectement. Le modèle est
ensuite normalement capable de repérer des entités (noms, prènoms, adresses) dans des nouveaux documents. 

 
""")


UTILISER = dcc.Markdown("""
* Vous pouvez uploader un document et ensuite regarder les entités repérées dans le texte ainsi que le texte pseudonymisé
sur l'onglet **Pseudonymise!**.
* La quantité des documents annotés à la main a une relation avec la qualité de l'annotation automatique. Trouvez un
exemple de cette relation dans l'onglet **Combien d'annotations ?**
* Derrière cette démo tourne une [API ouverte de pseudonymisation](http://somelink.ici). Dans **Stats** nous affichons les statistiques d'utilisation.
""")

PLUSINFO = dcc.Markdown("""
Vous pouvez trouver beaucoup plus d'informations sur [notre guide pseudo](http://www.guides.etalab.gouv.fr).
""")

tab_about_content = dbc.Tab(
    label='À propos',
    tab_id="tab-about",
    children=html.Div(className='page', children=[
        html.H4(className='what-is', children='La pseudonymisation en quelque mots'),
        html.P(QUOI),
        html.H4(className='what-is', children='Pourquoi un outil de pseudonymisation ?'),
        html.P(POURQUOI),
        html.H4(className='what-is', children='Comment ça marche ?'),
        html.P(COMMENT),
        html.H4(className='what-is', children='Utiliser ce demo'),
        html.P(UTILISER),
        html.H4(className='what-is', children="Plus d'infos"),
        html.P(PLUSINFO),
    ])
)