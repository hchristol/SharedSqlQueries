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
	AND p.type = ## select distinct '''' || type || ''''  from shv.panneau; Type de panneau : 'B6d' ##
	AND pco.type = ## select distinct '''' || type || ''''  from shv.panonceau; Type de panonceau : 'M6h' ##
	AND p.creation_date >= to_date('## date Après le : 01/01/2015 ##','DD/MM/YYYY')
	AND p.creation_date < to_date('## date Avant le : 01/01/2016 ##','DD/MM/YYYY')
	ORDER BY adresse;
```

# Header parameters
Put header parameters in the comment block at the beginning of your request
* **result as** : you can both display the result of a query as a layer or as a list widget that you can export as xls file. The default value for this parameter is *layer*. If you only want to view a list widget (array) of your result, replace this value by *list*. If you want both a layer and a list widget, type *layer,list*
* **layer name** : name of the output layer (default : My Query)
* **gid** : name of the required integer key column (default : gid).
    **WARNING** : if your gid has duplicate values, Qgis will crash. Ensure your gid has unique values !
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
Same parameter can be duplicated. User will be asked only once for it. Just copy identical text parameter in your sql code.
Type of parameters :

* **text** : this is the default parameters : a simple string text

* **date** : if your parameter starts with this keyword, your parameter will appear in a date widget.

* **select** : if your parameter starts with this keyword, your parameter will be diplayed in a combo box. Items of the
    combo are the result of the select query you type. Example :
```sql
... AND class = ## select distinct '''' || class || ''''  from my_table; Class : 'Default value' ##
```
    Your query must end with a **;** to split it from the rest of your parameter description.

* **selected_item** : if your parameter starts with this keyword, that means the user must choose an entity on the map. Then the attribute used in sql will be the attribute of the entity. This attribute is given in the optional type attribute :
```sql
... AND name = ## selected_item name; Name : ##
```
    Your query must end with a **;** to split it from the rest of your parameter description.
    *Important* : If specific attribute "geom" is given, then the geom of the entity will be used in request (the ST_GeomFromEWKT will be used automaticaly to transform geometry from Qgis geometry to sql)
	
```sql
... AND geom = ## selected_item geom; Geometry of selected feature : ##
```
	
* **edited_geom** : display a tool to edit a geometry on map. You have to specify the type of geometry you want (point, line, polygon, use "&" to allow several types) :
```sql
	SELECT row_number() over() as gid, ST_Buffer(## edited_geom point&line&polygon; Edit a point or a line or a polygon on map : ##, 100) as geom;
```


# Forbidden characters
The '%' character is not allowed when layer storage is _source_ because Qgis refuse to load sql layer with this character.
Use math _mod()_ function instead, or use a different layer storage.

# Qgis dump
If Qgis crashes, it's probably because your query does not have the required fields. Ensure that your request return at least a gid column.

# Query with no geom column
At the moment, it works only with **layer storage** : source

# Other query
UPDATE, INSERT AND DELETE query can be performed. No layer name is required.

# QML associated files
You can create a qml file (layer style file for Qgis) whose name is the name of the query file.
If so, after loading sql layer, this style will be applied to the newly added layer.


