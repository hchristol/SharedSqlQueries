# simple translation module (Qt Translator... no thanks)

from PyQt4.QtCore import QSettings

# initialize locale
locale = QSettings().value('locale/userLocale')[0:2]

# french translation
translation_fr = {
    u"Shared SQL Queries": u"Requêtes partagées",
    u"Query File": u"Fichier de Requête",
    u"Open": u"Ouvrir",
    u"Run": u"Exécuter",
    u"Error": u"Erreur",
    u"Invalid parameter": u"Paramètre invalide",
    u"My Request": u"Ma Requête",
    u"layer name": u"Nom de la couche",
    u"Unable to add a layer corresponding to this query !": u"Impossible d'ajouter une couche correspondant à cette requête !"
}


translations = {"fr": translation_fr}


def tr(message):
    if locale in translations:
        if message in translations[locale]:
            return translations[locale][message]
    return message  # nothing found
