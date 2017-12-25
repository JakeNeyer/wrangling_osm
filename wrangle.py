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
