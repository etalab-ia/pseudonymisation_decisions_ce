import dash_bootstrap_components as dbc
import dash_html_components as html

tab_about_content = dbc.Tab(
    label='À propos',
    tab_id="tab-about",
    children=html.Div(className='page', children=[
        html.H4(className='what-is', children='Pourquoi un outil de pseudonymization?'),
        html.P("Le règlement général sur la protection des données (RGPD) n’impose pas aux "
               "administrations d’anonymiser les documents qu’elles détiennent. Ainsi "
               "lorsque les "
               "documents administratifs comportent des données personnelles, ils ne peuvent "
               "être rendus publics qu'après avoir fait l'objet d'un traitement permettant "
               "de rendre impossible l'identification de ces personnes."),
        html.Br(),
        html.P("Dans l'onglet données vous pouvez charger un fichier afin de le faire "
               "pseudonimizer par l'algorithme "),

    ])
)