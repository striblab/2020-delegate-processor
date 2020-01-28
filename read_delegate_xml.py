from xml.dom import minidom

data_by_candidate = {}
# parse an xml file by name
mydoc = minidom.parse('xml/delstate.xml')

states = mydoc.getElementsByTagName('State')

for state in states:
    state_id = state.attributes['sId'].value
    print(state_id)
    candidates = state.childNodes
    for candidate in candidates:
        candidate_lname = candidate.attributes['cName'].value
        if candidate_lname not in data_by_candidate.keys():
            data_by_candidate[candidate_lname] = {}

        data_by_candidate[candidate_lname][state_id] = candidate.attributes['dTot'].value

print(data_by_candidate)

# one specific item attribute
# print('Item #2 attribute:')
# print(items[1].attributes['sId'].value)

# # all item attributes
# print('\nAll attributes:')
# for elem in items:
#     print(elem.attributes['name'].value)
#
# # one specific item's data
# print('\nItem #2 data:')
# print(items[1].firstChild.data)
# print(items[1].childNodes[0].data)
#
# # all items data
# print('\nAll item data:')
# for elem in items:
#     print(elem.firstChild.data)
