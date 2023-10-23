import json

INTERSECTION = json.load(open('categories_intersection.json', 'r'))
UNION = json.load(open('categories_union.json', 'r'))

for cat, domains in INTERSECTION.items():

    print("Union of TLDs for ", cat, len(UNION[cat]))

    print("Intersecting values for", cat + ':', len(INTERSECTION[cat]), '(', len(INTERSECTION[cat])/len(UNION[cat])*100, '%)')