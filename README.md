# SharedSqlQueries for [QGIS](http://qgis.org)

This QGIS plugin allows to share SQL customised queries (with user editable parameters) written by a db manager.
Those queries can then be used in a friendly interface by QGIS end users.
SQL queries are stored in a shared directory.
The result of querie can be either a table or a layer with geometry column that can be loaded into QGIS.
SQL queries is - for now - to be used only with PostgreSql/Postgis.

# Install
Copy this directory in your plugin directory.
Edit config.json and type your own folder to store SQL queries.

In this query folder, create a new config.json file that contains the following :
```json
{
    "queries_folder": "path to your folder",
	"bdpostgis": { "host":"my host","port":"5432","dbname":"my db name" }
}
```
You can add **user** and **password** in bdpostgis parameters if required.

# SQL files
They have to be put in subdirectory of the main query folder.
SQL files have to be UTF8 encoded.
SQL query must at least return an integer column (gid column, required by Qgis)
Every parameters are written like this : '**## _parameter name_ : _parameter value_ ##' .

# Example :
```sql
/*
## layer name : Panneau-panonceau avec date ##
## gid : gid ##
## geom : geom ##
## layer storage : shp ##
## layer directory : c:/temp ##
*/
SELECT row_number() over() as gid,
	p.type AS panneau,
	pco.type AS panonceau,
	v.typevoie||' '||v.excipientvoie||' '||v.libellevoie AS adresse,
	adresse.adresse_proche(p.geom,30) AS adresse_proche,
	p.creation_date AS date_creation,
	p.modification_date AS date_modification,
	p.date_po AS date_pose_shv,
	p.geom AS geom
FROM shv.panneau p, shv.panonceau pco, adresse.voie v, shv.support s
WHERE p.idsupport = s.idsupport
	AND p.idpanneau = pco.idpanneau
	AND s.voie1 = v.idvoie
	AND p.type = ## Type de panneau : 'B6d' ##
	AND pco.type = ## Type de panonceau : 'M6h' ##
	AND p.creation_date >= ## Après le : '2015/01/01' ##
	AND p.creation_date < ## Avant le : '2015/01/01' ##
	ORDER BY adresse;
```

# Header parameters
Put header parameters in the comment block at the beginning of your request
* **layer name** : name of the output layer (default : My Query)
* **gid** : name of the required integer key column (default : gid).
    ** WARNING ** : if your gid has duplicate values, Qgis will crash. Ensure your gid has unique values !
    Use this gid if you don't know how to deal with duplicate gid :
   ```sql
   SELECT row_number() over() as gid, ...
   ```
* **geom** : name of the geometry column (default : geom). Can be 'None' if no geometry is returned by query.
* **layer storage** : type of storage.
    * source : sql query is stored in the output layer. Sql query is performed each time the map is refreshed. Not suitable for time consuming queries.
    * memory : result of query is stored in a Qgis memory layer
    * shp : result is stored in a shape file
    * geojson : result is stored in a geojson file
* **layer directory** : required if layer storage is shp or geojson : the directory where the file will be written

# SQL parameters
Any parameter can be stored in sql query. Each parameter will be editable by user before query will be executed.

# Forbidden characters
The '%' character is not allowed when layer storage is _source_ because Qgis refuse to load sql layer with this character.
Use math _mod()_ function instead, or use a different layer storage.

# QML associated files
You can create a qml file (layer style file for Qgis) whose name is the name of the query file.
If so, after loading sql layer, this style will be applied to the newly added layer.


