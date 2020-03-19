# Module d'apprentissage

## Librairies utilisées

Ce module s'appuit sur la librairie [Flair](https://github.com/flairNLP/flair) pour l'apprentissage de l'algorithme de reconnaissance d'entités nommées.  

## Split du dataset

Le split du dataset consiste à créer, à partir d'une liste de fichiers CoNLL trois échantillons : entrainement, test et validation. 

## Corpus

Crée un objet Corpus Flair à partir des fichiers CoNLL indiqués en paramètres. Le Corpus représente le dataset utilisé pour entrainer l'algorithme. Il se compose d'une liste de Senteces divisé en trois groupes : l'échantillon d'entrainement, de test et de validation. 

## Train 

La fonction d'apprentissage du modèle à proprement parler. 
TODO : Parler des paramètres.