import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "aurora_il.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Rd." :"Road",
            "Ave": "Avenue",
            "Rd" : "Road",
            "Rd." : "Road",
            "Ln" : "Lane",
            "Dr" : "Drive",
            "Cir" : "Circle",
            "Blvd" : "Boulevard",
            }

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):
    street_type = name.rsplit(' ')[-1]
    m = street_type_re.search(name)
    street_name = name.rsplit(' ' , 1)[0]
    if street_type in mapping:
        name = street_name + ' ' + mapping[street_type]
    return name

def test():
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))

if __name__ == '__main__':
    test()