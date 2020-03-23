# La pseudonymisation : c'est quoi ?

## À qui s'adresse ce guide?
Modif2!

Ce guide s'adresse aux organismes publics, et plus particulièrement aux personnes chargées de la mise en place de la pseudonymisation des données dans ces organismes. Accessoirement, il intéressera les prestataires à qui les organismes publics demandent d'aider à mettre en place la pseudonymisation des données dans le cadre d'un marché public.

## Quelles sont les différences entre anonymisation et pseudonymisation ?

La pseudonymisation est un traitement de données personnelles réalisé de manière à ce qu'on ne puisse plus attribuer les données relatives à une personne physique sans avoir recours à des informations supplémentaires. En pratique la pseudonymisation consiste à remplacer les données directement identifiantes (nom, prénom, etc.) d’un jeu de données par des données indirectement identifiantes (alias, numéro dans un classement, etc.).

La pseudonymisation permet ainsi de traiter les données d’individus sans pouvoir identifier ceux-ci de façon directe. En pratique, il est toutefois bien souvent possible de retrouver l’identité de ceux-ci grâce à des données tierces. C’est pourquoi des données pseudonymisées demeurent des données personnelles. L’opération de pseudonymisation est potentiellement réversible, contrairement à l’anonymisation.

## Pourquoi pseudonymiser ?


Le règlement général sur la protection des données (RGPD) n’impose pas aux administrations d’anonymiser les documents qu’elles détiennent. L’anonymisation n’est qu’une solution parmi d’autres pour pouvoir exploiter des données personnelles dans le respect des droits et libertés des personnes.

En revanche, lorsque les administrations souhaitent diffuser ces documents (ou des données qu’ils contiennent), par exemple en les publiant en ligne, leur anonymisation préalable est une obligation légale qui s’impose à elles par principe en application du Code des relations entre le public et l’administration, CRPA (article L. 312-1-2).  Ainsi  lorsque les documents administratifs comportent des données personnelles, ils ne peuvent être rendus publics qu'après avoir fait l'objet d'un traitement permettant de rendre impossible l'identification de ces personnes.

## Quelles données personnelles dois-je retirer de mon jeu de données ?

Cela dépend du contexte réglementaire; le même cadre ne s'applique pas à tous les document.  
Néanmoins, il conviendra la plupart du temps de pseudonymiser toute information se rapportant à une personne physique identifiée ou identifiable. Une «personne physique identifiable» est une personne physique qui peut être identifiée, directement ou indirectement, notamment par référence à un identifiant, tel qu'un nom, un numéro d'identification, des données de localisation, un identifiant en ligne, ou à un ou plusieurs éléments spécifiques propres à son identité physique, physiologique, génétique, psychique, économique, culturelle ou sociale

# Comment pseudonymiser ?

## Cas où les données à caractère personnel sont tabulaires

Lors de la situation classique ou les données à caractère personnel sont clairement identifiable dans une base de données, il est aisé de procéder directement à des traitements visant à pseudonymiser ou anonymiser. Ce cas de figure n'est pas l'objet de ce guide. Pour plus d'information à ce sujet on se référera aux ressources de la CNIL.


## Cas où les données à caractère personnel apparaissent dans du texte libre

Dans ce cas de figure, les données identifiantes peuvent être compliqué à repérer ; traiter ce genre de données de manière manuelle est un processus humain long et requiert de l'expertise. L'IA et les techniques de traitement du langage naturel peuvent apporter des solutions à ce problème.


## Puis-je utiliser l'Intelligence Artificielle pour pseudonymiser ?

 Utiliser l'IA requiert de valider un certain nombre de points :
 - Y a-t-il des données annotées ? Puis-je annoter rapidement des données
 - Le volume et la qualité des données : Ces données sont-elles faciles à récupérer, à préparer et à gérer ?
 - Ai-je une infrastructure de calcul suffisante : serveurs de stockage, RAM, accès à des GPU?

![alt text](Choice_vf.svg "Logo Title Text 1")


# Quelles sont les étapes d'un projet de pseudonymisation ?

## Les données

Les données sont constitués de l'ensemble des documents (texte libre) à classifier ou permettant la mise en place d'un classificateur.

***
> ### Exemple de mise en oeuvre : moteur de pseudonymisation pour le Conseil d'État
> Les données provenant du Conseil d'État sont des décisions de justice où les noms et adresses des personnes apparaissent en clair. L'objectif est de pseudonymiser ces noms et adresses pour permettre la [publication des décisions](https://beta.legifrance.gouv.fr/search/cetat?tab_selection=cetat&searchField=ALL&query=&page=2&init=true)
***

La reconnaissance d'entité nommée est un exercice de classification et donc de machine learning supervisé. L'entrainement d'un tel algorithme nécessite de disposer de données annotées selon les classes à prédire. La création d'un jeu de données annotées peut être très consommatrice en temps homme. 
Pour essayer [notre outil d'annotation basé sur Doccano](http://0.0.0.0/).

## Labélisation

Les algorithmes de NLP prennent en entrée un fichier au format colonne où chaque ligne comporte un mot et une annotation linguistique. Par exemple :

| Token   | Label  | 
| ----------| ----------| 
| Thomas | B-PER | 
| CLAVIER | I-PER | 
| aime | O | 
| beaucoup | O | 
| Paris | B-LOC  | 

Nous utilisons le format BIO pour labéliser nos données. Le préfix B- avant un label indique que le label est le début d'un groupe, le préfix I- indique que le label est à l'intérieur d'un groupe, et le label O indique que le token n'a pas de label particulier.  
Pour aider au formatage des données, notre outil comporte une section permettant de transformer des json annotés par Doccano en format CONLL.  

***

> ### Le format CoNLL : 
> Pour  Conference on Natural Language Learning, est un format général, dont il existe de nombreuses versions, couramment employé pour les tâches de NLP, décrivant des données textuels en colonne selon un nombre d'attribut (label NER, type d'élément grammaticale etc.)
***

Pour transformer des données déjà annotés par un autre système, un développement spécifique sera nécessaire la plupart du temps. Plusieurs exemples de fonctions et de librairies développées pour le Conseil d'État constitueront néanmoins un point de départ.

***
> ### Exemple de mise en oeuvre : moteur de pseudonymisation pour le Conseil d'État
> Le conseil d'État dispose de 250 000 décisions déjà labélisées provenant des différents échelons de la justice administrative. 25 000 de ces décisions avaient reçu une vérification manuelle et ont permis de constituer un sous-échantillon de 5000 décisions pour l'apprentissage de l'algorithme.
***

## Tokénisation

Si l'on considère un document, composé de blocs de caractères, la tokénisation est la tâche qui consiste à découper ce document en éléments atomiques, en gardant ou supprimant la ponctuation. Par exemple :  

| Phrase        | 
| :------------- |
| Mes amis, mes enfants, l'avènement de la pseudonymisation automatique est proche. | 

Pourrait se tokénisation des manières suivantes :

| Token1   | Token2   | Token3   | Token4   | Token5   | Token6   | Token7   | Token8   | Token9   | Token10   | Token11   | Token12   | Token13   | Token14   | Token15   | Token16   |
| :----------| :----------| :----------| :----------| :----------| :----------| :----------| :----------| :----------| :----------| :----------|  :----------| :----------| :----------| :----------| :----------| 
| Mes  | amis  |  , | mes  | enfants  | ,   |l   | ' | avènement  | de   | la   |pseudonymisation| automatique| est  | proche  | .|
 

| Token1   | Token2   | Token3   | Token4   | Token5   | Token6   | Token7   | Token8   | Token9   | Token10   | Token11   |
| :----------| :----------| :----------| :----------| :----------| :----------| :----------| :----------| :----------| :----------| :----------| 
| Mes| amis| mes| enfants| l'avènement | de | la| pseudonymisation| automatique | est| proche|


Les tokens sont souvent associés aux mots, mais il est important de comprendre qu'une autre unité peut être choisie, par exemple les caractères eux-mêmes, ou que le choix de conserver ou non la ponctuation ou non a son importance.  
De manière pratique, il est important de comprendre la tokénisation utilisée par les algorithmes, afin de ne pas faire d'erreur lors de la localisation des entités à pseudonymiser dans le texte.  
Notre outil utilise les tokenisateurs du package **NLTK** : **WordPunctTokenizer** pour tokeniser une phrase en éléments, et **PunktSentenceTokenizer** pour découper le document en phrases (ou plus communément *sentences*, en anglais).


## Apprentissage

La reconnaisance d'entité nommée dans Flair se décompose en deux étapes. D'abord, la phrase à labéliser est découpée en caractères et passée à un modèle de langage pré-entrainé.
Il est possible d'utiliser de nombreux modèle de langage supportés par Flair, et notamment les modèles Bert et Camembert, ou de combiner plusieurs modèle de langages.
Ce modèle de langage permet pour chaque mot d'obtenir une représentation vectorielle (ou *embedding*).  Cet embedding est ensuite passé à un classificateur BiLSTM-CRF qui attribue à chaque mot une des classes du jeu de données d'entrainement.

L'entrainement d'un tel classificateur nécéssite de choisir un certain nombre de valeurs appelées (hyper)paramètres. Des exemples de configuration avec des explications des différents paramètres et de leur impact sont disponibles dans la section correspondante du Git.  
Nous proposons un exemple de module permettant d'entrainer un reconnaisseur d'entités nommées via la librairie FLAIR à partir d'un corpus annoté.  
Enfin, pour aller plus loin, la librairie Flair propose un module très pratique permettant de trouver les paramètres optimaux pour l'apprentissage : https://github.com/flairNLP/flair/blob/master/resources/docs/TUTORIAL_8_MODEL_OPTIMIZATION.md .



## Validation


La validation des performances du réseau et la mise en production est un double processus reposant sur l'analyse de métriques et sur l'expérience humaine.

![alt text](process.svg "Logo Title Text 1")


Notre module de génération de document pseudonymisés permet de produire en sorti des fichiers labélisés, au format CoNLL. Ceci permet de :   

 - Utiliser des métriques pour comparer un document labélisé par l'algorithme à des fichiers de référence dont la labélisation est connue. On utilise généralement le [F1-score](https://fr.wikipedia.org/wiki/Pr%C3%A9cision_et_rappel) pour mesurer la performance du modèle.
 - Charger dans [notre outil d'annotation basé sur Doccano](http://0.0.0.0/) un fichier mettant en avant les différences entre deux labélisations de sources différentes, indiquant en rouge les labels en désaccord et en vert les labels en accord.


## Génération du document pseudonymisé

Le modèle entrainé permet d'attribuer à chaque token du document à pseudonymiser. Pour le bon fonctionnement de cette étape il est très important de fournir à l'algorithme un document tokénisé d'une manière similaire à celle utilisée pour entrainer l'algorithme.  
Cette étape nécessite de reconstruire le texte à partir des sorties de l'algorithme : notre outil propose un module permettant de tester l'algorithme de reconnaissance d'entités nommées fournit nativement par Flair, ou un modèle entrainé sur des données spécifiques, et de générer des documents pseudonymisés. Le résultat est aussi visible [sur notre site](http://127.0.0.1:8050/).


# Quels sont les prérequis d'un tel projets?

## Les librairies

De nombreuses librairies permettent d'entrainer et d'utiliser des algorithmes de reconnaissance d'entités nommées. Parmi celles-ci, [Flair](https://github.com/flairNLP/flair) et [Spacy](https://spacy.io/usage/spacy-101) présentent l'avantage de proposer des algorithmes à l'état de l'art tout en facilitant l'expérience utilisateur.

 - Flair: Un framework simple pour le NLP. Flair permet d'utiliser des modèles de NLP à l'état de l'art sur des textes de tout genre, en particulier des algorithmes de reconnaissance d'entité nommées et des embeddings pré-entrainés
 - SpaCy: Un framework Python à forte capacité d'industrialisation pour le NLP. Il s'agit d'une librairie pour le NLP en Python et Cython. Il est construit sur les toutes dernières recherches et a été conçu dès le début pour être utilisé en production. Il possède des modèles statistiques et des embeddings pré-entrainés.

Nous utilisons Flair pour le fonctionnement de cet outil.

## Annotation

[Notre outil d'annotation](http://0.0.0.0/) est basé sur Doccano.
Doccano est un outil d'annotation de texte open source. Il fournit des fonctionnalités d'annotation pour la classification de texte, la labélisation de mots et d'autres tâches classiques de NLP. Ainsi, il est possible de créer des données labélisées pour l'analyse des sentiments, **la reconnaissance d'entités nommées**, la synthèse de texte, etc.  
Il est possible de créer rapidement un dataset de documents labélisés en installant rapidement et simplement Doccano. Notre outil permet de transformer simplement les données annotées via Doccano en fichiers CoNLL.


## L'infrastructure

L'apprentissage de modèles de NLP récents, basés sur des réseaux de neurones nécessite des ressources dédiées, notamment des ressources de type GPU afin d'accélérer considérablement le temps de calcul. Même en disposant de GPU de dernières générations, il faut compter plusieurs jours voire plusieurs semaine pour un apprentissage complet du modèle.


# Voir la pseudonymisation en action

Vous pouvez essayer notre démonstrateur de pseudonymisation sur http://127.0.0.1:8050/ ou directement voir le code sur https://github.com/etalab-ia

# Ressources
https://www.cnil.fr/fr/guide-rgpd-du-developpeur
https://www.cnil.fr/fr/lanonymisation-des-donnees-un-traitement-cle-pour-lopen-data


```python

```
