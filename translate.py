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
    u"layer name": u"Nom de la couche en sortie",
    u"Unable to add a layer corresponding to this query !":
        u"Impossible d'ajouter une couche correspondant à cette requête !",
    u"Query File is not UTF8 encoded ! Please convert it to UTF8 !":
        u"Le fichier de requête n'est pas en UTF8 ! Merci de le convertir en UTF8 !",
    u"% is not allowed in SQL QGIS layer : please use mod function instead":
        u"% n'est pas autorisé dans une couche SQL QGIS : utilisez la fonction mod à la place"
}


translations = {"fr": translation_fr}


def tr(message):
    if locale in translations:
        if message in translations[locale]:
            return translations[locale][message]
    return message  # nothing found
