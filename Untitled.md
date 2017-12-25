
# Wrangling OpenStreetMap Data

## 1. Map Area Used:

#### Aurora, IL 

https://www.openstreetmap.org/relation/124817#map=11/41.7308/-88.2422

I chose data from Aurora, Illinois because it is my hometown. I love being able to see data points that I have seen in real life as it really brings a much more realistic, intuitive feel to my project

## 2. Problems Encountered

The first problem I encountered was to be expected. There were several street abbreviations that needed to be standardized.

## 3. Cleaning The Data

In order to clean the data, I wanted to correct the abbreviated street names in the same process of turning the XML elements into JSON in an effort to be more efficient. To do so, I used the code below:



```python
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json


#Regular Expression for street types
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


#Already Existing Fields in OSM Data
CREATED = ["uid", "version", "changeset", "timestamp", "user"]

#Mapping Of Street Names
MAPPING = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd" : "Road",
            "Rd." : "Road",
            "Ln" : "Lane",
            "Dr" : "Drive",
            "Ct" : "Court",
            "Cir" : "Circle",
            "Blvd" : "Boulevard",
            "Blvd." : "Boulevard"
            }

def update_name(name, mapping):
    '''
    This function cleans the street abbreviations.
    :param name: 
    :param mapping: 
    :return updated name: 
    '''
    street_type = name.rsplit(' ')[-1]
    m = street_type_re.search(name)
    street_name = name.rsplit(' ', 1)[0]
    if street_type in mapping:
        name = street_name + ' ' + mapping[street_type]
    return name


def shape_element(element):
    '''
    This function takes OSM XML Data and turns it into JSON objects.
    :param element:
    :return node:
    '''
    node = {}

    #Just Looking for node and way tags (see https://wiki.openstreetmap.org/wiki/Elements) for questions
    if element.tag == "node" or element.tag == "way":
        node['type'] = element.tag
        node['id'] = element.attrib['id']
        if 'visible' in element.attrib:
            node['visible'] = element.attrib['visible']
        if 'lat' in element.attrib and 'lon' in element.attrib:
            node['pos'] = []
            node['pos'].append(float(element.attrib['lat']))
            node['pos'].append(float(element.attrib['lon']))
        node['created'] = {}
        for i in CREATED:
            node['created'][i] = element.attrib[i]

        #Taking Special Consideration for the address as they are tagged as
        address = {}
        for i in element.iter('tag'):
            if 'addr:' in i.attrib['k']:
                if 'street:' in i.attrib['k'].split(':', 1)[1]:
                    pass
                else:
                    #Cleaning Street Abreviations by calling update_name()
                    address[i.attrib['k'].split(':', 1)[1]] = update_name(i.attrib['v'], MAPPING)
            else:
                node[i.attrib['k']] = i.attrib['v']

        if address:
            node['address'] = address


        return node
    else:
        return None


def process_map(file_in, pretty=False):
    '''
    This function returns write data to a JSON file
    :param file_in: 
    :param pretty: 
    :return JSON Data: 
    '''
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2) + "\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


data = process_map('aurora_il.osm', True)

```

## 4. Overview of Data

### Size of Files:

aurora_il.osm : 169.9 MB
aurora_il.osm.json : 220.6 MB
### Number of Unique Users:
> db.aurora_il.distinct('created.user').length

Result:
796

### Number of Nodes:
> db.aurora_il.find({"type":"node"}).count()

Result:
801984
### Number of Ways:
> db.aurora_il.find({"type":"way"}).count()

Result:
74256
## Exploring More of the Data:

### Number of Restaurants:
> db.aurora_il.find({"amenity": "restaurant"}).count()

Result:
332 
### Top Ten Cuisines:
> db.aurora_il.aggregate({"$match":{"cuisine":{"$exists":1}}},{"$group":{"_id":"$cuisine","count":{"$sum":1}}},{"$sort":{"count": -1}}, {"$limit":10})

Result:
{ "_id" : "burger", "count" : 67 }
{ "_id" : "pizza", "count" : 36 }
{ "_id" : "mexican", "count" : 35 }
{ "_id" : "sandwich", "count" : 26 }
{ "_id" : "coffee_shop", "count" : 22 }
{ "_id" : "chinese", "count" : 19 }
{ "_id" : "american", "count" : 15 }
{ "_id" : "italian", "count" : 12 }
{ "_id" : "ice_cream", "count" : 11 }
{ "_id" : "chicken", "count" : 9 }
### Different Types of Cuisine:
> db.aurora_il.distinct("cuisine").length

Result:
48

## Data Statistics:

The top user 'Umbugbene' makes up 31.8% of all the entries in the data set. Here is the detailed breakdown of the users and their contributions: 


```python
import pprint
from pymongo import MongoClient

def get_db(db_name):
    '''
    Setting Up MongoDB Connections
    :param db_name:
    :return db:
    '''
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def make_pipeline():
    pipeline = [{"$match":{"created.user":{"$exists":1}}},
                {"$group":{"_id":"$created.user","count":{"$sum":1}}},
                {"$sort":{"count": -1}},
                {"$project": {"perc": { "$multiply": [ { "$divide": ["$count", 876295] }, 100 ] }}}]
    return pipeline

def aggregate(db, pipeline):
    return [doc for doc in db.aurora_il.aggregate(pipeline)]


if __name__ == '__main__':
    db = get_db('opendata')
    pipeline = make_pipeline()
    result = aggregate(db, pipeline)
    pprint.pprint(result)
```

    [{'_id': 'Umbugbene', 'perc': 31.836424948219495},
     {'_id': 'woodpeck_fixbot', 'perc': 7.323218779064128},
     {'_id': 'alexrudd (NHD)', 'perc': 5.651749696163963},
     {'_id': 'patester24', 'perc': 4.852019011862444},
     {'_id': 'cowdog', 'perc': 4.694651915165555},
     {'_id': 'Deo Favente', 'perc': 4.4626524172795685},
     {'_id': 'jimjoe45', 'perc': 3.400110693316748},
     {'_id': 'mpinnau', 'perc': 3.240461260192059},
     {'_id': 'Mundilfari', 'perc': 3.1287408920511925},
     {'_id': 'TacoBeans44', 'perc': 2.44267056185417},
     {'_id': 'Marga_Dela', 'perc': 2.2137522181457157},
     {'_id': 'mappy123', 'perc': 1.6171494759184977},
     {'_id': 'TIGERcnl', 'perc': 1.5822297285731404},
     {'_id': 'knottga3', 'perc': 1.2809613201033898},
     {'_id': 'g246020', 'perc': 1.1441352512567116},
     {'_id': 'Mulad', 'perc': 1.0236278878688114},
     {'_id': 'Tharsis', 'perc': 0.7605886145647299},
     {'_id': 'asdf1234', 'perc': 0.6718057275232656},
     {'_id': 'raykendo', 'perc': 0.6695233910954644},
     {'_id': 'Sundance', 'perc': 0.62068139154052},
     {'_id': 'Ru55Ht', 'perc': 0.528474999857354},
     {'_id': 'maxerickson', 'perc': 0.5232256260734114},
     {'_id': 'bot-mode', 'perc': 0.4930987852264363},
     {'_id': 'Radek_trz', 'perc': 0.4547555332393771},
     {'_id': '42429', 'perc': 0.42782396339132367},
     {'_id': 'N219JK', 'perc': 0.4140158280031268},
     {'_id': 'BeatlesZeppelinRush', 'perc': 0.35102334259581536},
     {'_id': 'dhansen22', 'perc': 0.34874100616801423},
     {'_id': 'MGH', 'perc': 0.3269446932825133},
     {'_id': 'Kev-H', 'perc': 0.31119657193068545},
     {'_id': 'Chris Lawrence', 'perc': 0.3109683382879053},
     {'_id': 'bdiscoe', 'perc': 0.3054907308611826},
     {'_id': 'bbmiller', 'perc': 0.30206722621948084},
     {'_id': 'shimano44', 'perc': 0.2698862825874848},
     {'_id': 'mrusnaczyk', 'perc': 0.26281103966130126},
     {'_id': 'iandees', 'perc': 0.2615557546260106},
     {'_id': 'AndrewSnow', 'perc': 0.2348524184207373},
     {'_id': 'Matthew Truch', 'perc': 0.22675012410204326},
     {'_id': 'kstone113', 'perc': 0.2144255073919171},
     {'_id': 'MrAkshat', 'perc': 0.20518204485932248},
     {'_id': 'Rub21', 'perc': 0.20278559161013127},
     {'_id': 'Skuuba', 'perc': 0.1855539515802327},
     {'_id': 'Steven Vance', 'perc': 0.18349984879521167},
     {'_id': 'ridixcr', 'perc': 0.17688107315458834},
     {'_id': 'JoshM11', 'perc': 0.17665283951180824},
     {'_id': 'Apoxol', 'perc': 0.17585402176207784},
     {'_id': 'BenUWebmaster', 'perc': 0.17459873672678722},
     {'_id': 'zrunner', 'perc': 0.1706046479781352},
     {'_id': 'samely', 'perc': 0.15440005934074713},
     {'_id': 'konan12', 'perc': 0.15382947523379684},
     {'_id': 'theborg', 'perc': 0.15268830701989627},
     {'_id': 'ashleyannmathew', 'perc': 0.1472106995931735},
     {'_id': 'Zol87', 'perc': 0.13625548473972807},
     {'_id': 'zephyr', 'perc': 0.136141367918338},
     {'_id': 'marthaleena', 'perc': 0.13214727916968602},
     {'_id': 'dannykath', 'perc': 0.1268979053857434},
     {'_id': 'bhavana naga', 'perc': 0.12336028392265162},
     {'_id': 'NE2', 'perc': 0.12199088206597093},
     {'_id': 'Blue Nacho', 'perc': 0.1189097278884394},
     {'_id': 'MikeN', 'perc': 0.11856737742426922},
     {'_id': 'PhQ', 'perc': 0.11560034006812775},
     {'_id': 'user_5359', 'perc': 0.11434505503283711},
     {'_id': 'MapAssist', 'perc': 0.10818274667777404},
     {'_id': 'HolgerJeromin', 'perc': 0.10247690560827119},
     {'_id': 'Phil D Basket', 'perc': 0.1019063215013209},
     {'_id': 'BobM', 'perc': 0.10133573739437061},
     {'_id': 'Infinipro', 'perc': 0.1011075037515905},
     {'_id': 'kollokollo', 'perc': 0.1011075037515905},
     {'_id': 'Gapsnap', 'perc': 0.10019456918047005},
     {'_id': 'muziriana', 'perc': 0.09791223275266892},
     {'_id': 'MatthewWhitesell87', 'perc': 0.09460284493235725},
     {'_id': 'mapper377', 'perc': 0.09437461128957714},
     {'_id': 'Tom Layo', 'perc': 0.09232050850455611},
     {'_id': 'RichRico', 'perc': 0.09038052254092514},
     {'_id': 'vsquared', 'perc': 0.09038052254092514},
     {'_id': 'garret', 'perc': 0.09026640571953508},
     {'_id': 'RoadGeek_MD99', 'perc': 0.08764171882756377},
     {'_id': 'alexrudd', 'perc': 0.08273469550779133},
     {'_id': 'Bhojaraj', 'perc': 0.08079470954416036},
     {'_id': 'teodorab_telenav', 'perc': 0.0806805927227703},
     {'_id': 'hno2', 'perc': 0.07919707404469956},
     {'_id': 'chris983', 'perc': 0.0790829572233095},
     {'_id': 'andrewpmk', 'perc': 0.07874060675913934},
     {'_id': 'Takuto', 'perc': 0.07839825629496916},
     {'_id': 'MikeNBulk', 'perc': 0.07554533576021774},
     {'_id': 'jonesydesign', 'perc': 0.07474651801048735},
     {'_id': 'alangard', 'perc': 0.07417593390353705},
     {'_id': 'am116', 'perc': 0.07269241522546631},
     {'_id': 'bradman4562', 'perc': 0.07075242926183535},
     {'_id': 'nickvet419', 'perc': 0.07052419561905524},
     {'_id': 'Luis36995', 'perc': 0.06881244329820436},
     {'_id': 'terminalmage', 'perc': 0.06710069097735352},
     {'_id': 'Koharu', 'perc': 0.06675834051318334},
     {'_id': 'dmcbride98', 'perc': 0.06481835454955237},
     {'_id': 'radek-drlicka', 'perc': 0.06413365362121204},
     {'_id': 'fitzsimons', 'perc': 0.06413365362121204},
     {'_id': 'irasesu', 'perc': 0.062307784478971125},
     {'_id': 'OverThere', 'perc': 0.060824265800900376},
     {'_id': 'AlaskaDave', 'perc': 0.059797214408389865},
     {'_id': 'GXCEB0TOSM', 'perc': 0.059683097586999814},
     {'_id': 'Pierre Riteau', 'perc': 0.05956898076560976},
     {'_id': 'karitotp', 'perc': 0.0586560461944893},
     {'_id': 'eric22', 'perc': 0.058541929373099245},
     {'_id': 'StellanL', 'perc': 0.055574892016957755},
     {'_id': 'oba510', 'perc': 0.05523254155278759},
     {'_id': "Jet's Wheaton", 'perc': 0.052265504196646106},
     {'_id': 'Trex2001', 'perc': 0.052265504196646106},
     {'_id': 'torapa', 'perc': 0.051923153732475934},
     {'_id': 'Map4PoGO', 'perc': 0.051238452804135595},
     {'_id': 'Lolzep', 'perc': 0.050781985518575365},
     {'_id': 'geostone', 'perc': 0.04690201359131343},
     {'_id': '25or6to4', 'perc': 0.046559663127143255},
     {'_id': 'ruthmaben', 'perc': 0.04576084537741286},
     {'_id': 'sabas88', 'perc': 0.044049093056562},
     {'_id': 'cdelacruz', 'perc': 0.04347850894961172},
     {'_id': 'etorrvar', 'perc': 0.04347850894961172},
     {'_id': 'Cam4rd98', 'perc': 0.04347850894961172},
     {'_id': 'homeslice60148', 'perc': 0.04302204166405149},
     {'_id': 'dorianre', 'perc': 0.04188087345015092},
     {'_id': 'DougPeterson', 'perc': 0.040169121129300066},
     {'_id': 'kz7', 'perc': 0.03994088748651995},
     {'_id': 'abel801', 'perc': 0.03959853702234978},
     {'_id': 'calfarome', 'perc': 0.03959853702234978},
     {'_id': 'tebiggs', 'perc': 0.03925618655817961},
     {'_id': 'nicberry', 'perc': 0.038685602451229324},
     {'_id': 'Amy Lebre', 'perc': 0.03857148562983927},
     {'_id': 'wb8nbs', 'perc': 0.038115018344279036},
     {'_id': 'FrViPofm', 'perc': 0.03788678470149893},
     {'_id': 'Brian@Brea', 'perc': 0.03777266788010887},
     {'_id': 'Japanthers', 'perc': 0.03685973330898841},
     {'_id': 'ediyes', 'perc': 0.03685973330898841},
     {'_id': 'houston_mapper1', 'perc': 0.0358326819164779},
     {'_id': 'Johnathan Bahena Diaz', 'perc': 0.03491974734535744},
     {'_id': 'cluening', 'perc': 0.03491974734535744},
     {'_id': 'NickWaj', 'perc': 0.03469151370257732},
     {'_id': 'ChiefBurky', 'perc': 0.034463280059797215},
     {'_id': 'FTA', 'perc': 0.03434916323840716},
     {'_id': 'iarspider', 'perc': 0.034006812774236984},
     {'_id': 'Chetan_Gowda', 'perc': 0.032865644560336416},
     {'_id': 'dunduk', 'perc': 0.0326374109175563},
     {'_id': 'GeneBase', 'perc': 0.03206682681060602},
     {'_id': 'WinstonLords', 'perc': 0.03195270998921596},
     {'_id': 'Spanholz', 'perc': 0.031838593167825904},
     {'_id': 'BelpheniaProject', 'perc': 0.03172447634643585},
     {'_id': 'Brutus', 'perc': 0.03161035952504579},
     {'_id': 'piligab', 'perc': 0.030126840846975048},
     {'_id': 'Ivan Komarov', 'perc': 0.029898607204194932},
     {'_id': 'boeleman81', 'perc': 0.029442139918634706},
     {'_id': 'barnaclebarnes_linz', 'perc': 0.02898567263307448},
     {'_id': 'ToeBee', 'perc': 0.027502153955003737},
     {'_id': 'railfan-eric', 'perc': 0.02738803713361368},
     {'_id': 'Bob Stone', 'perc': 0.0268174530266634},
     {'_id': 'sageinventor', 'perc': 0.02670333620527334},
     {'_id': 'Skybunny', 'perc': 0.025904518455542938},
     {'_id': 'SednaBoo', 'perc': 0.025333934348592654},
     {'_id': 'Michael Keierleber', 'perc': 0.024649233420252315},
     {'_id': 'Aurimas Fišeras', 'perc': 0.0244209997774722},
     {'_id': 'ecr8on', 'perc': 0.0244209997774722},
     {'_id': 'Iowa Kid', 'perc': 0.02396453249191197},
     {'_id': 'Ojdhi', 'perc': 0.023622182027741797},
     {'_id': 'hofoen', 'perc': 0.0228233642780114},
     {'_id': 'Zenence', 'perc': 0.022595130635231286},
     {'_id': 'swimdb', 'perc': 0.02236689699245117},
     {'_id': 'bruck4', 'perc': 0.021910429706890944},
     {'_id': 'wrowold', 'perc': 0.02156807924272077},
     {'_id': 'rolandg', 'perc': 0.02099749513577049},
     {'_id': 'LocalTrailgeek', 'perc': 0.020883378314380432},
     {'_id': 'neuhausr', 'perc': 0.020883378314380432},
     {'_id': 'paulmach', 'perc': 0.020426911028820202},
     {'_id': 'patrick noll', 'perc': 0.02019867738604009},
     {'_id': 'fx99', 'perc': 0.020084560564650033},
     {'_id': 'korky99_04', 'perc': 0.019856326921869918},
     {'_id': 'ranjithjoy', 'perc': 0.019856326921869918},
     {'_id': 'GITNE', 'perc': 0.019628093279089806},
     {'_id': 'nyuriks', 'perc': 0.019628093279089806},
     {'_id': 'LaunchedFir', 'perc': 0.019513976457699745},
     {'_id': 'Peter-DG', 'perc': 0.019057509172139518},
     {'_id': 'Chris Nobre', 'perc': 0.018372808243799176},
     {'_id': 'cncr04s', 'perc': 0.01825869142240912},
     {'_id': 'anjinsan222', 'perc': 0.017802224136848892},
     {'_id': 'Sunfishtommy', 'perc': 0.017688107315458838},
     {'_id': 'TeresaPeteti', 'perc': 0.01757399049406878},
     {'_id': 'DaveHansenTiger', 'perc': 0.01734575685128866},
     {'_id': 'mdk', 'perc': 0.01711752320850855},
     {'_id': 'lgoughenour', 'perc': 0.01711752320850855},
     {'_id': 'aerosuch', 'perc': 0.016889289565728438},
     {'_id': 'Geogast', 'perc': 0.016889289565728438},
     {'_id': 'Bman', 'perc': 0.016546939101558265},
     {'_id': 'DomMedina', 'perc': 0.016432822280168208},
     {'_id': 'yurasi', 'perc': 0.01597635499460798},
     {'_id': 'adamos', 'perc': 0.01517753724487758},
     {'_id': 'illario2', 'perc': 0.01483518678070741},
     {'_id': 'Chaoshaq', 'perc': 0.014264602673757124},
     {'_id': 'je091926', 'perc': 0.01403636903097701},
     {'_id': 'wvdp', 'perc': 0.01369401856680684},
     {'_id': 'poornibadrinath', 'perc': 0.013465784924026726},
     {'_id': 'Andy Rothman', 'perc': 0.013009317638466498},
     {'_id': 'RetiredInNH', 'perc': 0.013009317638466498},
     {'_id': 'cardswin2005', 'perc': 0.012552850352906271},
     {'_id': 'JessicaOppenheimer', 'perc': 0.011982266245955985},
     {'_id': 'wilmaed', 'perc': 0.011982266245955985},
     {'_id': '!i!', 'perc': 0.011982266245955985},
     {'_id': 'GlassBrass440', 'perc': 0.011868149424565927},
     {'_id': 'jumbanho', 'perc': 0.011754032603175871},
     {'_id': 'Aaron Lidman', 'perc': 0.011754032603175871},
     {'_id': 'nbutyllithium', 'perc': 0.011754032603175871},
     {'_id': 'ramyaragupathy', 'perc': 0.011525798960395758},
     {'_id': 'Dylan Semler', 'perc': 0.011297565317615643},
     {'_id': 'oldtopos', 'perc': 0.011183448496225585},
     {'_id': 'hobbesvsboyle', 'perc': 0.010955214853445472},
     {'_id': 'Chasseur_De_Cadavres', 'perc': 0.010841098032055414},
     {'_id': 'DiestelkampAaron', 'perc': 0.0106128643892753},
     {'_id': 'shravan91', 'perc': 0.0106128643892753},
     {'_id': 'rosskin92', 'perc': 0.010498747567885245},
     {'_id': 'dominique hoavonon', 'perc': 0.010384630746495187},
     {'_id': 'Dustdjin', 'perc': 0.010384630746495187},
     {'_id': 'andygol', 'perc': 0.01027051392510513},
     {'_id': 'RolandD357', 'perc': 0.010156397103715072},
     {'_id': 'rallor', 'perc': 0.010156397103715072},
     {'_id': 'nusense', 'perc': 0.010042280282325016},
     {'_id': 'jacobbraeutigam', 'perc': 0.010042280282325016},
     {'_id': 'pbroviak', 'perc': 0.009928163460934959},
     {'_id': 'onearmedgeek', 'perc': 0.009814046639544903},
     {'_id': 'gxceb0t', 'perc': 0.009699929818154845},
     {'_id': 'Parcanman', 'perc': 0.009357579353984674},
     {'_id': 'Lexxy Fox', 'perc': 0.00912934571120456},
     {'_id': 'gpsradler', 'perc': 0.009015228889814503},
     {'_id': 'Ed_Hedborn', 'perc': 0.008901112068424446},
     {'_id': 'becw', 'perc': 0.008901112068424446},
     {'_id': 'egore911', 'perc': 0.00867287842564433},
     {'_id': 'rza31', 'perc': 0.008558761604254275},
     {'_id': 'dmgroom_ct', 'perc': 0.008330527961474161},
     {'_id': 'Eliyak', 'perc': 0.008102294318694046},
     {'_id': 'jsieben7', 'perc': 0.007874060675913933},
     {'_id': 'CHAINJOJ', 'perc': 0.007759943854523876},
     {'_id': 'kugelfiesch', 'perc': 0.007759943854523876},
     {'_id': 'AmethystSkies92', 'perc': 0.007759943854523876},
     {'_id': 'gormur', 'perc': 0.007759943854523876},
     {'_id': 'manings', 'perc': 0.007645827033133819},
     {'_id': 'howdystranger', 'perc': 0.007645827033133819},
     {'_id': 'Phil Scherer', 'perc': 0.007645827033133819},
     {'_id': 'panoramedia', 'perc': 0.007645827033133819},
     {'_id': 'tmcw', 'perc': 0.007531710211743762},
     {'_id': 'Claret', 'perc': 0.007531710211743762},
     {'_id': 'elsevansickle', 'perc': 0.007531710211743762},
     {'_id': 'pratikyadav', 'perc': 0.0073034765689636485},
     {'_id': 'Paul Johnson', 'perc': 0.007189359747573592},
     {'_id': 'Maazin5', 'perc': 0.007189359747573592},
     {'_id': 'Gene Tam', 'perc': 0.00684700928340342},
     {'_id': 'jmassey92', 'perc': 0.00684700928340342},
     {'_id': 'jzabawski', 'perc': 0.00684700928340342},
     {'_id': 'Teesta', 'perc': 0.00684700928340342},
     {'_id': 'MarksKim013', 'perc': 0.006732892462013363},
     {'_id': 'surveyor54', 'perc': 0.006618775640623306},
     {'_id': 'ccharhut', 'perc': 0.006504658819233249},
     {'_id': 'Juergen Juffa', 'perc': 0.006504658819233249},
     {'_id': 'Edward', 'perc': 0.006504658819233249},
     {'_id': 'uboot', 'perc': 0.006504658819233249},
     {'_id': 'mpbretl', 'perc': 0.006504658819233249},
     {'_id': 'Lemur', 'perc': 0.006390541997843192},
     {'_id': 'Timothy Smith', 'perc': 0.006390541997843192},
     {'_id': 'pyram', 'perc': 0.006162308355063079},
     {'_id': 'didier2020', 'perc': 0.006048191533673021},
     {'_id': 'Saucon Support', 'perc': 0.006048191533673021},
     {'_id': 'claysmalley', 'perc': 0.005934074712282964},
     {'_id': 'ChrisZontine', 'perc': 0.005934074712282964},
     {'_id': 'linuxUser16', 'perc': 0.005819957890892907},
     {'_id': 'Tyhawkeye1', 'perc': 0.005819957890892907},
     {'_id': 'Jeff Johnson', 'perc': 0.00570584106950285},
     {'_id': 'AaronAsAChimp', 'perc': 0.00570584106950285},
     {'_id': 'PeterEastern', 'perc': 0.00570584106950285},
     {'_id': 'greencube', 'perc': 0.00570584106950285},
     {'_id': 'dfultz11', 'perc': 0.00570584106950285},
     {'_id': 'lmaxon', 'perc': 0.005477607426722736},
     {'_id': 'Iqhra', 'perc': 0.005477607426722736},
     {'_id': 'Imp_GL', 'perc': 0.005363490605332679},
     {'_id': 'courtnei19', 'perc': 0.005363490605332679},
     {'_id': 'reunify_aarti', 'perc': 0.005363490605332679},
     {'_id': 'mpmckenna8', 'perc': 0.0052493737839426225},
     {'_id': 'mannequinZOD', 'perc': 0.0052493737839426225},
     {'_id': 'KristenK', 'perc': 0.0052493737839426225},
     {'_id': 'KindredCoda', 'perc': 0.0052493737839426225},
     {'_id': 'MilaZ', 'perc': 0.005021140141162508},
     {'_id': 'Drum_Castle', 'perc': 0.005021140141162508},
     {'_id': 'mgoe', 'perc': 0.005021140141162508},
     {'_id': 'amillar', 'perc': 0.0049070233197724515},
     {'_id': 'srashid2', 'perc': 0.004792906498382394},
     {'_id': 'BCNorwich', 'perc': 0.004792906498382394},
     {'_id': 'steverumizen', 'perc': 0.004792906498382394},
     {'_id': 'katie_gillingham', 'perc': 0.004792906498382394},
     {'_id': 'bitslab', 'perc': 0.004792906498382394},
     {'_id': 'woodpeck_repair', 'perc': 0.004678789676992337},
     {'_id': 'Dami_Tn', 'perc': 0.004678789676992337},
     {'_id': 'mr earth', 'perc': 0.004678789676992337},
     {'_id': 'bjake377', 'perc': 0.00456467285560228},
     {'_id': 'EEwasiuk', 'perc': 0.00456467285560228},
     {'_id': 'srividya_c', 'perc': 0.00456467285560228},
     {'_id': 'venkanna37', 'perc': 0.00456467285560228},
     {'_id': 'Maria Fish', 'perc': 0.004450556034212223},
     {'_id': 'jshipley', 'perc': 0.004450556034212223},
     {'_id': 'jinnantonix', 'perc': 0.004450556034212223},
     {'_id': 'T_9er', 'perc': 0.004450556034212223},
     {'_id': 'ruph', 'perc': 0.004450556034212223},
     {'_id': 'hca', 'perc': 0.004450556034212223},
     {'_id': 'JRArocks', 'perc': 0.004336439212822165},
     {'_id': 'Xaq', 'perc': 0.004336439212822165},
     {'_id': 'WickedSavvy', 'perc': 0.004336439212822165},
     {'_id': 'R0bst3r', 'perc': 0.0042223223914321095},
     {'_id': 'Ropino', 'perc': 0.0042223223914321095},
     {'_id': 'Gwyn Ciesla', 'perc': 0.0042223223914321095},
     {'_id': 'LilyC', 'perc': 0.004108205570042052},
     {'_id': 'jgrnt', 'perc': 0.004108205570042052},
     {'_id': 'davidearl', 'perc': 0.004108205570042052},
     {'_id': 'California Bear', 'perc': 0.004108205570042052},
     {'_id': 'BrianKiwi', 'perc': 0.004108205570042052},
     {'_id': 'EdSS', 'perc': 0.004108205570042052},
     {'_id': 'vnnie', 'perc': 0.003994088748651995},
     {'_id': 'Luiyo', 'perc': 0.003994088748651995},
     {'_id': 'Thomas8122', 'perc': 0.003879971927261938},
     {'_id': 'maxolasersquad', 'perc': 0.003879971927261938},
     {'_id': 'Bryce C Nesbitt', 'perc': 0.003879971927261938},
     {'_id': 'nikhilprabhakar', 'perc': 0.003879971927261938},
     {'_id': 'MST Hiker', 'perc': 0.003879971927261938},
     {'_id': 'Glassman', 'perc': 0.003879971927261938},
     {'_id': 'Alan Trick', 'perc': 0.003765855105871881},
     {'_id': 'Yoshinion', 'perc': 0.003765855105871881},
     {'_id': 'Andy Allan', 'perc': 0.003765855105871881},
     {'_id': 'Mikeeeeee999999', 'perc': 0.0036517382844818242},
     {'_id': 'FvGordon', 'perc': 0.0036517382844818242},
     {'_id': 'rab', 'perc': 0.0036517382844818242},
     {'_id': 'Jim S', 'perc': 0.0036517382844818242},
     {'_id': 'TyKo', 'perc': 0.0036517382844818242},
     {'_id': 'Danimal_34', 'perc': 0.0035376214630917667},
     {'_id': 'Sampool15', 'perc': 0.0035376214630917667},
     {'_id': 'Cali42', 'perc': 0.0035376214630917667},
     {'_id': 'mapserver', 'perc': 0.0035376214630917667},
     {'_id': 'RobynLHeine', 'perc': 0.00342350464170171},
     {'_id': 'RC22CUB', 'perc': 0.00342350464170171},
     {'_id': 'bitslab-diaz', 'perc': 0.003309387820311653},
     {'_id': 'n9oum', 'perc': 0.003309387820311653},
     {'_id': 'li3n3', 'perc': 0.003309387820311653},
     {'_id': 'user_870861', 'perc': 0.003309387820311653},
     {'_id': 'Marych_', 'perc': 0.003309387820311653},
     {'_id': 'jk92', 'perc': 0.003309387820311653},
     {'_id': 'TheSaxMan', 'perc': 0.003195270998921596},
     {'_id': 'strout', 'perc': 0.003195270998921596},
     {'_id': 'Czech', 'perc': 0.003195270998921596},
     {'_id': 'xybot', 'perc': 0.0030811541775315394},
     {'_id': 'Pierre-Alain Dorange', 'perc': 0.0030811541775315394},
     {'_id': 'White_Rabbit', 'perc': 0.0030811541775315394},
     {'_id': 'CloCkWeRX', 'perc': 0.0030811541775315394},
     {'_id': 'jimzat', 'perc': 0.0030811541775315394},
     {'_id': 'GIS_Downers', 'perc': 0.002967037356141482},
     {'_id': 'Joven', 'perc': 0.002967037356141482},
     {'_id': 'MrMacs', 'perc': 0.002967037356141482},
     {'_id': 'Camila33', 'perc': 0.002852920534751425},
     {'_id': 'Geo_Liz', 'perc': 0.002852920534751425},
     {'_id': 'AngryForks', 'perc': 0.002852920534751425},
     {'_id': 'klining', 'perc': 0.002852920534751425},
     {'_id': 'dtatter', 'perc': 0.002852920534751425},
     {'_id': 'YohanMapmaker', 'perc': 0.002738803713361368},
     {'_id': 'jaimemd', 'perc': 0.002738803713361368},
     {'_id': 'Stephanie Landa', 'perc': 0.002738803713361368},
     {'_id': 'Wichita-dweller', 'perc': 0.0026246868919713113},
     {'_id': 'LpAngelRob', 'perc': 0.0026246868919713113},
     {'_id': 'Pnrrth', 'perc': 0.002510570070581254},
     {'_id': 'L3mming', 'perc': 0.002510570070581254},
     {'_id': 'Zerojpgs', 'perc': 0.002510570070581254},
     {'_id': 'salinds2', 'perc': 0.002510570070581254},
     {'_id': 'Cato_d_Ae', 'perc': 0.002510570070581254},
     {'_id': 'techlady', 'perc': 0.002396453249191197},
     {'_id': 'Nate_Wessel', 'perc': 0.002396453249191197},
     {'_id': 'Schimmel23', 'perc': 0.00228233642780114},
     {'_id': 'jharpster', 'perc': 0.00228233642780114},
     {'_id': 'Anthony Moffa', 'perc': 0.00228233642780114},
     {'_id': 'nimakdm', 'perc': 0.00228233642780114},
     {'_id': 'cdavila', 'perc': 0.00228233642780114},
     {'_id': 'captainjim', 'perc': 0.00228233642780114},
     {'_id': 'adrobcamp', 'perc': 0.00228233642780114},
     {'_id': 'Nikhil Tilwalli', 'perc': 0.00228233642780114},
     {'_id': 'dchiles', 'perc': 0.00228233642780114},
     {'_id': 'iWowik', 'perc': 0.0021682196064110827},
     {'_id': 'Logan Laughrey', 'perc': 0.0021682196064110827},
     {'_id': 'mugs15', 'perc': 0.0021682196064110827},
     {'_id': 'Little Brother', 'perc': 0.0021682196064110827},
     {'_id': 'OSMF Redaction Account', 'perc': 0.0021682196064110827},
     {'_id': 'nanders', 'perc': 0.002054102785021026},
     {'_id': 'stevea', 'perc': 0.002054102785021026},
     {'_id': 'Dmytro Ovdiienko', 'perc': 0.002054102785021026},
     {'_id': 'calamos', 'perc': 0.001939985963630969},
     {'_id': 'PokemonGOInvestigator', 'perc': 0.001939985963630969},
     {'_id': 'Moovit Team', 'perc': 0.001939985963630969},
     {'_id': 'arborist10', 'perc': 0.001939985963630969},
     {'_id': 'sco', 'perc': 0.0018258691422409121},
     {'_id': 'nakratz', 'perc': 0.0018258691422409121},
     {'_id': 'stucki1', 'perc': 0.0018258691422409121},
     {'_id': 'BFX', 'perc': 0.0018258691422409121},
     {'_id': 'JSWB', 'perc': 0.0018258691422409121},
     {'_id': 'craigloftus', 'perc': 0.0018258691422409121},
     {'_id': 'RaquelFish09', 'perc': 0.001711752320850855},
     {'_id': 'Ted Engel', 'perc': 0.001711752320850855},
     {'_id': 'ThorstenNeumann', 'perc': 0.001711752320850855},
     {'_id': 'ivansanchez', 'perc': 0.001711752320850855},
     {'_id': 'hitth3lights', 'perc': 0.001711752320850855},
     {'_id': 'Nowa1011', 'perc': 0.001597635499460798},
     {'_id': 'AJ_LA', 'perc': 0.001597635499460798},
     {'_id': 'Mr0grog', 'perc': 0.001597635499460798},
     {'_id': 'blahedo', 'perc': 0.001597635499460798},
     {'_id': 'nammala', 'perc': 0.001597635499460798},
     {'_id': 'kerosin', 'perc': 0.001597635499460798},
     {'_id': 'Gone', 'perc': 0.001597635499460798},
     {'_id': 'DennisL', 'perc': 0.001597635499460798},
     {'_id': 'camphouse', 'perc': 0.001597635499460798},
     {'_id': 'ssam', 'perc': 0.001483518678070741},
     {'_id': 'jazzact', 'perc': 0.001483518678070741},
     {'_id': 'mattmaxon', 'perc': 0.001483518678070741},
     {'_id': 'KR-KRKR-KR', 'perc': 0.001369401856680684},
     {'_id': 'MattStanford', 'perc': 0.001369401856680684},
     {'_id': 'rahulsaurav', 'perc': 0.001369401856680684},
     {'_id': 'zors1843', 'perc': 0.001369401856680684},
     {'_id': 'Mark Newnham', 'perc': 0.001369401856680684},
     {'_id': 'tyjo99', 'perc': 0.001369401856680684},
     {'_id': 'NicRoets', 'perc': 0.001369401856680684},
     {'_id': 'Milo', 'perc': 0.001369401856680684},
     {'_id': 'mapsinE3', 'perc': 0.001369401856680684},
     {'_id': 'DirtyJim', 'perc': 0.001255285035290627},
     {'_id': 'Matthew_Brock', 'perc': 0.001255285035290627},
     {'_id': 'Danny Nee', 'perc': 0.001255285035290627},
     {'_id': 'sdole', 'perc': 0.001255285035290627},
     {'_id': 'svance92', 'perc': 0.001255285035290627},
     {'_id': 'ben_says', 'perc': 0.001255285035290627},
     {'_id': 'SWF8', 'perc': 0.001255285035290627},
     {'_id': 'escada', 'perc': 0.001255285035290627},
     {'_id': 'Visum', 'perc': 0.001255285035290627},
     {'_id': 'SomeoneElse_Revert', 'perc': 0.00114116821390057},
     {'_id': 'TonyAugOG', 'perc': 0.00114116821390057},
     {'_id': 'lxbarth', 'perc': 0.00114116821390057},
     {'_id': 'okilimu', 'perc': 0.00114116821390057},
     {'_id': 'Keller Drees', 'perc': 0.00114116821390057},
     {'_id': 'MichaelCampbell', 'perc': 0.00114116821390057},
     {'_id': 'skipshearer', 'perc': 0.00114116821390057},
     {'_id': 'fredjunod', 'perc': 0.00114116821390057},
     {'_id': 'henningpohl', 'perc': 0.00114116821390057},
     {'_id': 'sargas', 'perc': 0.00114116821390057},
     {'_id': 'kelsey1181', 'perc': 0.00114116821390057},
     {'_id': 'Sky Slicer', 'perc': 0.001027051392510513},
     {'_id': 'Ted Zabawski', 'perc': 0.001027051392510513},
     {'_id': 'dchamper4', 'perc': 0.001027051392510513},
     {'_id': 'grimnok', 'perc': 0.001027051392510513},
     {'_id': 'IknowJoseph', 'perc': 0.001027051392510513},
     {'_id': 'JennaBoyd', 'perc': 0.001027051392510513},
     {'_id': 'NE3', 'perc': 0.001027051392510513},
     {'_id': 'Waubonsee Community College', 'perc': 0.001027051392510513},
     {'_id': 'teall', 'perc': 0.001027051392510513},
     {'_id': 'smur2452', 'perc': 0.001027051392510513},
     {'_id': 'EJMinniear', 'perc': 0.001027051392510513},
     {'_id': 'Peter14', 'perc': 0.001027051392510513},
     {'_id': 'RussNelson', 'perc': 0.001027051392510513},
     {'_id': 'TorhamZed', 'perc': 0.001027051392510513},
     {'_id': 'andrewsh', 'perc': 0.0009129345711204561},
     {'_id': 'ririmapper', 'perc': 0.0009129345711204561},
     {'_id': 'oanac2_telenav', 'perc': 0.0009129345711204561},
     {'_id': 'mike140', 'perc': 0.0009129345711204561},
     {'_id': 'GaelicHunter', 'perc': 0.0009129345711204561},
     {'_id': 'Zartbitter', 'perc': 0.0009129345711204561},
     {'_id': 'Dark Asteroid', 'perc': 0.0009129345711204561},
     {'_id': 'ceeerg', 'perc': 0.0009129345711204561},
     {'_id': 'vsilva525', 'perc': 0.0009129345711204561},
     {'_id': 'pathym', 'perc': 0.0009129345711204561},
     {'_id': 'ajgrigg91', 'perc': 0.000798817749730399},
     {'_id': 'inah_telenav', 'perc': 0.000798817749730399},
     {'_id': 'aallen90', 'perc': 0.000798817749730399},
     {'_id': 'sebastic', 'perc': 0.000798817749730399},
     {'_id': 'oini', 'perc': 0.000798817749730399},
     {'_id': 'Anthonyfish46', 'perc': 0.000798817749730399},
     {'_id': 'medavis7695', 'perc': 0.000798817749730399},
     {'_id': 'sllockard', 'perc': 0.000798817749730399},
     {'_id': 'sgauss', 'perc': 0.000798817749730399},
     {'_id': 'Ohr', 'perc': 0.000798817749730399},
     {'_id': 'bstenson', 'perc': 0.000798817749730399},
     {'_id': 'flamozzle', 'perc': 0.000798817749730399},
     {'_id': 'nfgusedautoparts', 'perc': 0.000798817749730399},
     {'_id': 'Jeff Ollie', 'perc': 0.000798817749730399},
     {'_id': 'Jolene Chow', 'perc': 0.000798817749730399},
     {'_id': 'Doug777', 'perc': 0.000798817749730399},
     {'_id': 'GCerretani', 'perc': 0.000798817749730399},
     {'_id': 'OMapper', 'perc': 0.000798817749730399},
     {'_id': 'ioanam_telenav', 'perc': 0.000684700928340342},
     {'_id': 'Rannier', 'perc': 0.000684700928340342},
     {'_id': "Mike O'Connor", 'perc': 0.000684700928340342},
     {'_id': 'danielle cain', 'perc': 0.000684700928340342},
     {'_id': 'Jguy', 'perc': 0.000684700928340342},
     {'_id': 'Monica Brandeis', 'perc': 0.000684700928340342},
     {'_id': 'norcross', 'perc': 0.000684700928340342},
     {'_id': 'Serway', 'perc': 0.000684700928340342},
     {'_id': 'Kelvin Limbrick', 'perc': 0.000684700928340342},
     {'_id': 'logic', 'perc': 0.000684700928340342},
     {'_id': 'VMeyer', 'perc': 0.000684700928340342},
     {'_id': 'h4ck3rm1k3', 'perc': 0.000684700928340342},
     {'_id': 'Cradle', 'perc': 0.000684700928340342},
     {'_id': 'lukesolo06', 'perc': 0.000684700928340342},
     {'_id': 'Ardric', 'perc': 0.000684700928340342},
     {'_id': 'Big Dal', 'perc': 0.000684700928340342},
     {'_id': 'eMerzh', 'perc': 0.000684700928340342},
     {'_id': 'fumo7887', 'perc': 0.000684700928340342},
     {'_id': 'DavidF', 'perc': 0.000684700928340342},
     {'_id': 'brogo', 'perc': 0.000570584106950285},
     {'_id': 'laurenmalia', 'perc': 0.000570584106950285},
     {'_id': 'StephenMangum', 'perc': 0.000570584106950285},
     {'_id': 'woodpeck', 'perc': 0.000570584106950285},
     {'_id': 'kjon', 'perc': 0.000570584106950285},
     {'_id': 'dherkes', 'perc': 0.000570584106950285},
     {'_id': 'invader_zim', 'perc': 0.000570584106950285},
     {'_id': 'KyleMachalinski', 'perc': 0.000570584106950285},
     {'_id': 'NayanataraM', 'perc': 0.000570584106950285},
     {'_id': 'mclaess', 'perc': 0.000570584106950285},
     {'_id': 'salix01', 'perc': 0.000570584106950285},
     {'_id': 'IceMan22', 'perc': 0.000570584106950285},
     {'_id': 'Rellec', 'perc': 0.000570584106950285},
     {'_id': 'agdegala', 'perc': 0.000570584106950285},
     {'_id': 'mahmoodr', 'perc': 0.000570584106950285},
     {'_id': 'rkachelriess', 'perc': 0.000570584106950285},
     {'_id': 'beej71', 'perc': 0.000570584106950285},
     {'_id': 'Md Alamgir', 'perc': 0.000570584106950285},
     {'_id': 'poppei82', 'perc': 0.000570584106950285},
     {'_id': 'user_7659', 'perc': 0.000570584106950285},
     {'_id': 'gundog', 'perc': 0.000570584106950285},
     {'_id': 'GerdP', 'perc': 0.000570584106950285},
     {'_id': 'lindsaybayley', 'perc': 0.000570584106950285},
     {'_id': 'Kbreit', 'perc': 0.000570584106950285},
     {'_id': 'williamrh', 'perc': 0.000570584106950285},
     {'_id': 'Jonathan ZHAO', 'perc': 0.000570584106950285},
     {'_id': 'Kia Of North Aurora', 'perc': 0.000570584106950285},
     {'_id': 'DWilson_Metronet', 'perc': 0.000570584106950285},
     {'_id': 'cacrawf', 'perc': 0.000570584106950285},
     {'_id': 'aroach', 'perc': 0.000570584106950285},
     {'_id': 'Ryjoma', 'perc': 0.000570584106950285},
     {'_id': 'Vegettoblue', 'perc': 0.000570584106950285},
     {'_id': 'Connor Aigner', 'perc': 0.000570584106950285},
     {'_id': 'nm7s9', 'perc': 0.000570584106950285},
     {'_id': 'scai', 'perc': 0.000570584106950285},
     {'_id': 'spencerrecneps', 'perc': 0.00045646728556022803},
     {'_id': 'maggot27', 'perc': 0.00045646728556022803},
     {'_id': 'Manu1400', 'perc': 0.00045646728556022803},
     {'_id': 'Maskulinum', 'perc': 0.00045646728556022803},
     {'_id': 'adjuva', 'perc': 0.00045646728556022803},
     {'_id': 'HANSOL9', 'perc': 0.00045646728556022803},
     {'_id': 'Orblivion', 'perc': 0.00045646728556022803},
     {'_id': 'johnsonbrett', 'perc': 0.00045646728556022803},
     {'_id': 'rhitz', 'perc': 0.00045646728556022803},
     {'_id': 'IdeaSara', 'perc': 0.00045646728556022803},
     {'_id': 'Blobo123', 'perc': 0.00045646728556022803},
     {'_id': 'geochrome', 'perc': 0.00045646728556022803},
     {'_id': 'skquinn', 'perc': 0.00045646728556022803},
     {'_id': 'davidbmalone', 'perc': 0.00045646728556022803},
     {'_id': 'MCJackson', 'perc': 0.00045646728556022803},
     {'_id': 'hefee', 'perc': 0.00045646728556022803},
     {'_id': 'buurmas', 'perc': 0.00045646728556022803},
     {'_id': 'skorasaurus', 'perc': 0.00045646728556022803},
     {'_id': 'Rob Gagala', 'perc': 0.00045646728556022803},
     {'_id': 'mcepican93', 'perc': 0.00045646728556022803},
     {'_id': 'Rat_catche', 'perc': 0.00045646728556022803},
     {'_id': 'dima', 'perc': 0.00045646728556022803},
     {'_id': 'spod', 'perc': 0.00045646728556022803},
     {'_id': 'LA2', 'perc': 0.00045646728556022803},
     {'_id': 'don-vip', 'perc': 0.00045646728556022803},
     {'_id': 'IanH', 'perc': 0.00045646728556022803},
     {'_id': 'tommy_pelmorex', 'perc': 0.00045646728556022803},
     {'_id': 'kalafut', 'perc': 0.00045646728556022803},
     {'_id': 'HunterFett', 'perc': 0.00045646728556022803},
     {'_id': 'jpbitzer', 'perc': 0.00045646728556022803},
     {'_id': 'fallingrock', 'perc': 0.000342350464170171},
     {'_id': 'cgu66', 'perc': 0.000342350464170171},
     {'_id': 'thetornado76', 'perc': 0.000342350464170171},
     {'_id': 'pereimer', 'perc': 0.000342350464170171},
     {'_id': 'Chris-55', 'perc': 0.000342350464170171},
     {'_id': 'Carl Simonson', 'perc': 0.000342350464170171},
     {'_id': 'Kurly', 'perc': 0.000342350464170171},
     {'_id': 'user_599436', 'perc': 0.000342350464170171},
     {'_id': 'achims311', 'perc': 0.000342350464170171},
     {'_id': 'wakingrufus', 'perc': 0.000342350464170171},
     {'_id': 'Jaryn Hart', 'perc': 0.000342350464170171},
     {'_id': 'katycat5e', 'perc': 0.000342350464170171},
     {'_id': 'dithompson', 'perc': 0.000342350464170171},
     {'_id': 'jwthornton', 'perc': 0.000342350464170171},
     {'_id': 'Emily Wong', 'perc': 0.000342350464170171},
     {'_id': 'Jean Bully', 'perc': 0.000342350464170171},
     {'_id': 'brillbo', 'perc': 0.000342350464170171},
     {'_id': 'zehpunktbarron', 'perc': 0.000342350464170171},
     {'_id': 'ceyockey', 'perc': 0.000342350464170171},
     {'_id': 'Stephen214', 'perc': 0.000342350464170171},
     {'_id': 'Kurt Pfaender', 'perc': 0.000342350464170171},
     {'_id': 'Clint Fransen', 'perc': 0.000342350464170171},
     {'_id': 'colag', 'perc': 0.000342350464170171},
     {'_id': 'ToffeHoff', 'perc': 0.000342350464170171},
     {'_id': 'Schlenker Enterprises Limited', 'perc': 0.000342350464170171},
     {'_id': 'danbjoseph', 'perc': 0.000342350464170171},
     {'_id': 'Ben97', 'perc': 0.000342350464170171},
     {'_id': 'Mike Nimer', 'perc': 0.000342350464170171},
     {'_id': 'TheCoat', 'perc': 0.00022823364278011402},
     {'_id': 'lancevinsel', 'perc': 0.00022823364278011402},
     {'_id': 'Heinz_V', 'perc': 0.00022823364278011402},
     {'_id': 'Dave Wegner', 'perc': 0.00022823364278011402},
     {'_id': 'Hobgoblin', 'perc': 0.00022823364278011402},
     {'_id': 'scross1234', 'perc': 0.00022823364278011402},
     {'_id': 'BugBuster', 'perc': 0.00022823364278011402},
     {'_id': 'beweta', 'perc': 0.00022823364278011402},
     {'_id': 'JimScap', 'perc': 0.00022823364278011402},
     {'_id': 'malajul', 'perc': 0.00022823364278011402},
     {'_id': 'Alexander Roalter', 'perc': 0.00022823364278011402},
     {'_id': 'locatus', 'perc': 0.00022823364278011402},
     {'_id': 'James Negley', 'perc': 0.00022823364278011402},
     {'_id': 'coelacanth', 'perc': 0.00022823364278011402},
     {'_id': 'goodsamaritan', 'perc': 0.00022823364278011402},
     {'_id': 'ewedistrict', 'perc': 0.00022823364278011402},
     {'_id': 'ChicagoPat', 'perc': 0.00022823364278011402},
     {'_id': 'TheHammer', 'perc': 0.00022823364278011402},
     {'_id': 'Ahlzen', 'perc': 0.00022823364278011402},
     {'_id': 'iav', 'perc': 0.00022823364278011402},
     {'_id': 'DaBears', 'perc': 0.00022823364278011402},
     {'_id': 'PlaneMad', 'perc': 0.00022823364278011402},
     {'_id': 'mabrew', 'perc': 0.00022823364278011402},
     {'_id': 'Clang', 'perc': 0.00022823364278011402},
     {'_id': 'Robbins', 'perc': 0.00022823364278011402},
     {'_id': 'upendrakarukonda', 'perc': 0.00022823364278011402},
     {'_id': 'JoshD', 'perc': 0.00022823364278011402},
     {'_id': 'Lart', 'perc': 0.00022823364278011402},
     {'_id': 'Gutsycat', 'perc': 0.00022823364278011402},
     {'_id': 'Math1985', 'perc': 0.00022823364278011402},
     {'_id': 'Eric Godwin', 'perc': 0.00022823364278011402},
     {'_id': 'theophrastos', 'perc': 0.00022823364278011402},
     {'_id': 'lesko987', 'perc': 0.00022823364278011402},
     {'_id': 'mueschel', 'perc': 0.00022823364278011402},
     {'_id': 'emacsen', 'perc': 0.00022823364278011402},
     {'_id': 'pvanwylen', 'perc': 0.00022823364278011402},
     {'_id': 'miklas', 'perc': 0.00022823364278011402},
     {'_id': 'bwarren', 'perc': 0.00022823364278011402},
     {'_id': 'BlainSupply', 'perc': 0.00022823364278011402},
     {'_id': 'Advantage Trailers', 'perc': 0.00022823364278011402},
     {'_id': 'Gozgo', 'perc': 0.00022823364278011402},
     {'_id': 'colindt', 'perc': 0.00022823364278011402},
     {'_id': 'kisaa', 'perc': 0.00022823364278011402},
     {'_id': 'Derick Rethans', 'perc': 0.00022823364278011402},
     {'_id': 'MasterJacoba', 'perc': 0.00022823364278011402},
     {'_id': 'Walter Schlögl', 'perc': 0.00022823364278011402},
     {'_id': 'TLacy', 'perc': 0.00022823364278011402},
     {'_id': 'Jim Polous', 'perc': 0.00022823364278011402},
     {'_id': 'Hundehalter', 'perc': 0.00022823364278011402},
     {'_id': 'PhotoDT', 'perc': 0.00022823364278011402},
     {'_id': 'soonerbh', 'perc': 0.00022823364278011402},
     {'_id': 'corb555', 'perc': 0.00011411682139005701},
     {'_id': 'Pepilepioux', 'perc': 0.00011411682139005701},
     {'_id': 'Bauer Dental', 'perc': 0.00011411682139005701},
     {'_id': 'benjamenster', 'perc': 0.00011411682139005701},
     {'_id': 'TomHynes', 'perc': 0.00011411682139005701},
     {'_id': 'Witoomard', 'perc': 0.00011411682139005701},
     {'_id': 'Arthtoach', 'perc': 0.00011411682139005701},
     {'_id': 'RicoZ', 'perc': 0.00011411682139005701},
     {'_id': 'styxrtp', 'perc': 0.00011411682139005701},
     {'_id': 'dpaschich', 'perc': 0.00011411682139005701},
     {'_id': 'stw1701', 'perc': 0.00011411682139005701},
     {'_id': 'hallj89', 'perc': 0.00011411682139005701},
     {'_id': 'fachi', 'perc': 0.00011411682139005701},
     {'_id': 'TonyMa', 'perc': 0.00011411682139005701},
     {'_id': 'growe222', 'perc': 0.00011411682139005701},
     {'_id': 'Daniel Mintz', 'perc': 0.00011411682139005701},
     {'_id': 'TheBrit', 'perc': 0.00011411682139005701},
     {'_id': 'NickOpenMap', 'perc': 0.00011411682139005701},
     {'_id': 'dfc849', 'perc': 0.00011411682139005701},
     {'_id': 'Jacob T', 'perc': 0.00011411682139005701},
     {'_id': 'MapperClapper', 'perc': 0.00011411682139005701},
     {'_id': 'realtyexecutive', 'perc': 0.00011411682139005701},
     {'_id': 'autorepail', 'perc': 0.00011411682139005701},
     {'_id': 'NickBolten', 'perc': 0.00011411682139005701},
     {'_id': 'velocitylaw', 'perc': 0.00011411682139005701},
     {'_id': 'psycastrology', 'perc': 0.00011411682139005701},
     {'_id': 'aandgrental', 'perc': 0.00011411682139005701},
     {'_id': 'Дмитрий Наумов', 'perc': 0.00011411682139005701},
     {'_id': 'Paul Gush', 'perc': 0.00011411682139005701},
     {'_id': 'queendawn', 'perc': 0.00011411682139005701},
     {'_id': 'Sparky5', 'perc': 0.00011411682139005701},
     {'_id': 'kb9fcc', 'perc': 0.00011411682139005701},
     {'_id': 'thelabs01', 'perc': 0.00011411682139005701},
     {'_id': 'cosmoshair', 'perc': 0.00011411682139005701},
     {'_id': 'tbh_10', 'perc': 0.00011411682139005701},
     {'_id': 'Francisco!!', 'perc': 0.00011411682139005701},
     {'_id': 'SandClub', 'perc': 0.00011411682139005701},
     {'_id': 'PierZen', 'perc': 0.00011411682139005701},
     {'_id': 'Thomas Pingel', 'perc': 0.00011411682139005701},
     {'_id': 'Bigdoza', 'perc': 0.00011411682139005701},
     {'_id': 'Warin61', 'perc': 0.00011411682139005701},
     {'_id': 'Thomabee', 'perc': 0.00011411682139005701},
     {'_id': 'Williamtorchia', 'perc': 0.00011411682139005701},
     {'_id': 'Andrius Stankevičius', 'perc': 0.00011411682139005701},
     {'_id': 'Syl', 'perc': 0.00011411682139005701},
     {'_id': 'pasztor', 'perc': 0.00011411682139005701},
     {'_id': 'Alienx', 'perc': 0.00011411682139005701},
     {'_id': 'Pokowaka', 'perc': 0.00011411682139005701},
     {'_id': 'Fa7C0N', 'perc': 0.00011411682139005701},
     {'_id': 'Gail P', 'perc': 0.00011411682139005701},
     {'_id': 'badpap', 'perc': 0.00011411682139005701},
     {'_id': 'dkwolf', 'perc': 0.00011411682139005701},
     {'_id': 'mfrns', 'perc': 0.00011411682139005701},
     {'_id': 'QLP2004', 'perc': 0.00011411682139005701},
     {'_id': 'mvexel', 'perc': 0.00011411682139005701},
     {'_id': 'AbbyMae', 'perc': 0.00011411682139005701},
     {'_id': 'Caribou52', 'perc': 0.00011411682139005701},
     {'_id': 'tryagain', 'perc': 0.00011411682139005701},
     {'_id': 'Mapnerdo', 'perc': 0.00011411682139005701},
     {'_id': 'bobbow', 'perc': 0.00011411682139005701},
     {'_id': 'jrdoro2', 'perc': 0.00011411682139005701},
     {'_id': 'Mark Alicz', 'perc': 0.00011411682139005701},
     {'_id': 'Hartmut Holzgraefe', 'perc': 0.00011411682139005701},
     {'_id': 'EmlynSquare', 'perc': 0.00011411682139005701},
     {'_id': 'Kelly Joniak', 'perc': 0.00011411682139005701},
     {'_id': 'Dion Dock', 'perc': 0.00011411682139005701},
     {'_id': 'elbatrop', 'perc': 0.00011411682139005701},
     {'_id': 'tkaap', 'perc': 0.00011411682139005701},
     {'_id': 'sjbucaro', 'perc': 0.00011411682139005701},
     {'_id': 'birksland', 'perc': 0.00011411682139005701},
     {'_id': 'Polyglot', 'perc': 0.00011411682139005701},
     {'_id': 'CleanUp', 'perc': 0.00011411682139005701},
     {'_id': 'iMarketSolutions', 'perc': 0.00011411682139005701},
     {'_id': 'wambacher', 'perc': 0.00011411682139005701},
     {'_id': 'geochanto', 'perc': 0.00011411682139005701},
     {'_id': 'clipdude', 'perc': 0.00011411682139005701},
     {'_id': 'androidguy', 'perc': 0.00011411682139005701},
     {'_id': 'storm72', 'perc': 0.00011411682139005701},
     {'_id': 'spindoctorappliance', 'perc': 0.00011411682139005701},
     {'_id': 'rkipnis', 'perc': 0.00011411682139005701},
     {'_id': 'thenitgoboom', 'perc': 0.00011411682139005701},
     {'_id': 'Gerneck', 'perc': 0.00011411682139005701},
     {'_id': 'kukai12', 'perc': 0.00011411682139005701},
     {'_id': 'batkins', 'perc': 0.00011411682139005701},
     {'_id': 'Kumar Saravanan', 'perc': 0.00011411682139005701},
     {'_id': 'Preferred', 'perc': 0.00011411682139005701},
     {'_id': 'mqudsi', 'perc': 0.00011411682139005701},
     {'_id': 'TheDutchMan13', 'perc': 0.00011411682139005701},
     {'_id': 'Benjamin Rorie', 'perc': 0.00011411682139005701},
     {'_id': 'werner2101', 'perc': 0.00011411682139005701},
     {'_id': 'McClaine', 'perc': 0.00011411682139005701},
     {'_id': '503Greg', 'perc': 0.00011411682139005701},
     {'_id': 'huntermap', 'perc': 0.00011411682139005701},
     {'_id': 'Cskonp', 'perc': 0.00011411682139005701},
     {'_id': 'myshakleeus', 'perc': 0.00011411682139005701},
     {'_id': 'dekalb77', 'perc': 0.00011411682139005701},
     {'_id': 'jeremyfelt', 'perc': 0.00011411682139005701},
     {'_id': 'wpedmonson', 'perc': 0.00011411682139005701},
     {'_id': 'Maarten Deen', 'perc': 0.00011411682139005701},
     {'_id': 'EdwardD20', 'perc': 0.00011411682139005701},
     {'_id': 'shivarx', 'perc': 0.00011411682139005701},
     {'_id': 'saikabhi', 'perc': 0.00011411682139005701},
     {'_id': 'tastygloria', 'perc': 0.00011411682139005701},
     {'_id': "Young's Appliances", 'perc': 0.00011411682139005701},
     {'_id': '4b696d', 'perc': 0.00011411682139005701},
     {'_id': 'klusark', 'perc': 0.00011411682139005701},
     {'_id': 'lisashebar', 'perc': 0.00011411682139005701},
     {'_id': 'Naomid612', 'perc': 0.00011411682139005701},
     {'_id': 'dciwil', 'perc': 0.00011411682139005701},
     {'_id': 'JohnG888', 'perc': 0.00011411682139005701},
     {'_id': 'ninjamask', 'perc': 0.00011411682139005701},
     {'_id': 'LightningBlaze', 'perc': 0.00011411682139005701},
     {'_id': 'fyrwlker', 'perc': 0.00011411682139005701},
     {'_id': 'Jothirnadh', 'perc': 0.00011411682139005701},
     {'_id': 'JohnWG', 'perc': 0.00011411682139005701},
     {'_id': 'durin42', 'perc': 0.00011411682139005701},
     {'_id': 'Sarr_Cat', 'perc': 0.00011411682139005701},
     {'_id': 'sejohnson', 'perc': 0.00011411682139005701},
     {'_id': 'drdinosdental', 'perc': 0.00011411682139005701},
     {'_id': 'Dero Bike Racks', 'perc': 0.00011411682139005701},
     {'_id': 'Olyon', 'perc': 0.00011411682139005701},
     {'_id': 'gisgurl', 'perc': 0.00011411682139005701},
     {'_id': 'pete404', 'perc': 0.00011411682139005701},
     {'_id': 'Nakaner-repair', 'perc': 0.00011411682139005701},
     {'_id': 'Solidmercury', 'perc': 0.00011411682139005701},
     {'_id': 'Jamie Tate', 'perc': 0.00011411682139005701},
     {'_id': 'Data411', 'perc': 0.00011411682139005701},
     {'_id': 'shopstylestudiodg', 'perc': 0.00011411682139005701},
     {'_id': 'RuslanDem', 'perc': 0.00011411682139005701},
     {'_id': 'florinbadita_telenav', 'perc': 0.00011411682139005701},
     {'_id': '<0174', 'perc': 0.00011411682139005701},
     {'_id': 'Berg Roofing', 'perc': 0.00011411682139005701},
     {'_id': 'slgan', 'perc': 0.00011411682139005701},
     {'_id': 'fschmidt', 'perc': 0.00011411682139005701},
     {'_id': 'euphoria240', 'perc': 0.00011411682139005701},
     {'_id': 'Dieter Schmeer', 'perc': 0.00011411682139005701},
     {'_id': 'josiebessie', 'perc': 0.00011411682139005701},
     {'_id': 'maximeguillaud', 'perc': 0.00011411682139005701},
     {'_id': 'James Films', 'perc': 0.00011411682139005701},
     {'_id': 'Gafergus', 'perc': 0.00011411682139005701},
     {'_id': 'alusiani', 'perc': 0.00011411682139005701},
     {'_id': 'JPB76', 'perc': 0.00011411682139005701},
     {'_id': 'j3d', 'perc': 0.00011411682139005701},
     {'_id': 'sanborn', 'perc': 0.00011411682139005701},
     {'_id': 'Pancake Lover', 'perc': 0.00011411682139005701},
     {'_id': 'Davlak', 'perc': 0.00011411682139005701}]


## 5. Other Ideas About the Data Set:

The data set could be improved by making bulk inputted data easier to filter out. Bots and automatic data dumps are very present in the data set as can be seen above. Elements from National Hydrography Dataset (NHD) were dumped in this case mainly by alexrudd(NHD) but only discovered after close investigation. Also, Topologically Integrated Geographic Encoding and Referencing data (tiger) data is spread throughout the data set. (See below for queries). While this data is important to some, it takes away the importance of user inputted data. I think focusing on user-inputted data, and highlighting its existence would help improve the data.
> db.aurora_il.find({"NHD:way_id":{"$exists":1}}).count()
815
> db.aurora_il.find({"tiger:reviewed":{"$exists":1}}).count()
14335
## 6. Conclusion:

After extensively looking through the OpenStreetMap data, I have fonud how much of it is inputted by automatic methods. I would like to see more light shed on the user-inputted part of the data set. Although this data set is extremely large, there are obviously still room for improvement when it comes to maintaing consistency of the data set.

## Sources

#### Project Examples

https://gist.github.com/carlward/54ec1c91b62a5f911c42

https://docs.google.com/document/d/1F0Vs14oNEs2idFJR3C_OPxwS6L0HPliOii-QpbmrMo4/pub

#### Udacity OpenStreetMap Case Study

https://www.youtube.com/watch?v=JyX6j00Q2Cg&feature=youtu.be

#### MongoDB Documentation

https://docs.mongodb.com/
