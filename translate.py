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
    u"No config.json file found ! A default one is created but you have to edit it (in your plugin directory)":
        u"Aucun fichier de configuration trouvé ! Un fichier par défaut est créé mais vous devez le renseigner (dans votre dossier de plugin)",
    u"Invalid parameter": u"Paramètre invalide",
    u"My Request": u"Ma Requête",
    u"layer name": u"Nom de la couche en sortie",
    u"layer directory": u"dossier pour la couche",
    u"Unable to add a layer corresponding to this query !":
        u"Impossible d'ajouter une couche correspondant à cette requête !",
    u"Query File is not UTF8 encoded ! Please convert it to UTF8 !":
        u"Le fichier de requête n'est pas en UTF8 ! Merci de le convertir en UTF8 !",
    u"% is not allowed in SQL QGIS layer : please use mod function instead":
        u"% n'est pas autorisé dans une couche SQL QGIS : utilisez la fonction mod à la place",
    u"No geometry type found for memory layer ! Unable to load unknown geometry type !":
        u"Aucun type de géometrie pour la couche en mémoire ! Impossible d'ouvrir les géométrie de type inconnu !",
    u"No layer directory parameter found in query !":
        u"Pas de paramètre de dossier trouvé dans la requête !",
    u"Select just one feature on map !":
        u"Selectionnez une et une seule entité sur la carte !",
    u"Select a vector layer !":
        u"Sélectionnez une couche vectorielle !",
    u"This feature does not have such an attribute : ":
        u"Cette entité ne possède pas cet attribut : ",
    u"Attribute of selected feature":
        u"Attribut de l'entité sélectionné",
    u"Geometry of selected feature":
        u"Géométrie de l'entité sélectionnée",
    u"Click a point on map":
        u"Cliquez dans la carte pour saisir un point",
    u"Request performed":
        u"Requête exécutée",
    u"Result": u"Resultats",
    u"Output file :": u"Fichier résultat :"
}


translations = {"fr": translation_fr}


def tr(message):
    if locale in translations:
        if message in translations[locale]:
            return translations[locale][message]
    return message  # nothing found
