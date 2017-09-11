# Sql query read in an sql file where custom parameters can be overriden
# example of parameter :  ##My Value : type : default value##
# header info must be provided at the beginning of the file, in /* */

from codecs import open
import os.path
from translate import tr
import re # regular expression

# Tag for parameters
TAG = "##"
# inner Tag for parameters
SEP = " : "
# regex comment block search : match block comments
COMMENT_BLOCK_PATTERN = '(?<=\/\*)((?:|.|\n|\r)*)(?=\*\/)'
# regex comment line search : match lines comments
COMMENT_LINE_PATTERN = '--.*(\n|\r)'

# default values for header
# gid : name of column integer id
# geom : name of geometry column
# layer name : name of layer that will store resulting data
# layer storage : type of storage for this layer :
#       - source (sql query is directly the data source, memory
#       - memory : copy in memory of the sql query
DEFAULT_HEADER_VALUE = {
    'gid': {"value": 'gid'},
    'geom': {"value": 'geom'},
    'layer name': {"value": tr('My Request')},
    'layer storage': {"value": "source"}
}

class CustomSqlQuery:

    # read CustomSqlQuery from a given path to an sql file
    def __init__(self, path):
        stream = open(path, 'r', "utf8")
        self.path = path
        self.name = os.path.basename(path).replace(".sql", "")
        self.rawSql = stream.read()

        [self.header, self.sql] = extractHeader(self.rawSql)
        self.param = extractCustomParameters(self.sql)
        self.finalSql = None

    def updateFinalSql(self):
        self.finalSql = injectCustomParameters(self.param, self.sql)
        # print self.finalSql
        return self.finalSql

    # return a header value, or its default value if no header found
    def headerValue(self, paramName):
        if paramName in DEFAULT_HEADER_VALUE:
            # there is a default value
            return paramValue(self.header, paramName, DEFAULT_HEADER_VALUE[paramName]["value"])
        else:
            # there is no default value
            return paramValue(self.header, paramName)

    def styleFilePath(self):
        return os.path.dirname(self.path) + "/" + self.name + ".qml"


# extract first /* */ comment at the beginning of the file, and return sql without this header
def extractHeader(sql):

    search_comment = re.findall(COMMENT_BLOCK_PATTERN, sql)

    print search_comment

    if len(search_comment) == 0:
        # no header in the file
        return [None, sqlCommentIgnored(sql)]

    header_string = search_comment[0]

    # header just at the start of the file
    # if len(exploded) == 2:
    #     header_string = exploded[0]
    #     sql_after_header = sqlCommentIgnored(exploded[1])
    #
    # #...or header after empty lines :
    # if len(exploded) > 2:
    #     header_string = exploded[1]
    #     # add to sql
    #     sql_after_header=""
    #     for i in range(2, len(exploded), 2):
    #         sql_after_header += " " + sqlCommentIgnored(exploded[i])

    # print "sql_after_header = " + sql_after_header

    print "extractHeader : " + header_string
    header = extractCustomParameters(header_string)
    return [header, sqlCommentIgnored(sql)]




#return parameters read from an sql string
def extractCustomParameters(sql):
    param = {}
    # split sql to extract parameters
    exploded = sql.split(TAG)
    count = 0

    # print "extractCustomParameters"
    # print exploded

    for block in exploded:

        # param between two tag : only on odd words
        if (count % 2) == 1:
            [paramName, value] = readParamter(block)
            # store order to keep order when creating dialog
            value["order"] = count
            param[paramName] = value

        count += 1

    if count != 0 and (count % 2) != 1:
        exc = SyntaxError()
        exc.text = tr(u"Wrong Number of " + TAG)
        raise exc

    # print "extractCustomParameters fin, param = " + str(param)
    return param


# Read a string of parameter : ## myParameter : Value ##
def readParamter(stringParameter):

    number_of_words = 2

    # split in max number_of_attributes words (name type)
    word = stringParameter.split(SEP, number_of_words-1)

    if len(word) != number_of_words:
        exc = SyntaxError()
        exc.text = tr(u"Invalid parameter") + ":" + stringParameter
        raise exc

    paramName = word[0].strip()
    # default type for parameter
    typeOfParameter = 'string'

    # TODO : add a parameter type for richer type : #date, #float, #integer,...

    return [paramName, {"type": typeOfParameter, "default": word[1].strip()}]


# return an sql string where custom parameters has been set to their value, so
# the sql can be run.
def injectCustomParameters(param, sql):

    # split sql to extract parameters
    exploded = sql.split(TAG)
    count = 0
    finalSql=""

    for block in exploded:

        if (count % 2) == 1:
            # parameter sql block
            [paramName, value] = readParamter(block)

            # parameter for this block
            p = param[paramName]
            if "value" in p:
                finalSql += p["value"]
            else:
                # no value set : use default value
                finalSql += p["default"]

        else:
            # other sql block
            finalSql += block

        count += 1

    if count != 0 and (count % 2) != 1:
        exc = SyntaxError()
        exc.text = tr(u"Wrong Number of " + TAG)
        raise exc


    return finalSql


# return value from parameter list
def paramValue(paramList, paramName, defaultValue = None):
    if paramList is None:
        return defaultValue
    if paramName not in paramList:
        return defaultValue
    return value(paramList[paramName], defaultValue)


# return value from a single param dictionnary
def value(param, defaultValue = None):
    if param is None:
        return defaultValue
    if "value" in param:
        return param["value"]
    if "default" in param:
        return param["default"]
    return defaultValue

def sqlCommentIgnored(sql):
    without_block_comment = re.sub(COMMENT_BLOCK_PATTERN, "", sql)
    return re.sub(COMMENT_LINE_PATTERN, "", without_block_comment)
