import csv
import sys
from datetime import datetime
from xml.dom import minidom
from collections import OrderedDict

candidates_with_delegates = ['Biden', 'Sanders', 'Buttigieg', 'Klobuchar', 'Warren', 'Bloomberg', 'Gabbard']

# First parse AP delegate data
data_by_state = {}
mydoc = minidom.parse('xml/delstate.xml')

dems = mydoc.getElementsByTagName('del')[0]

states = dems.getElementsByTagName('State')
candidate_list = []

for state in states:
    state_id = state.attributes['sId'].value
    candidates = state.childNodes
    data_by_state[state_id] = {}
    for candidate in candidates:
        candidate_lname = candidate.attributes['cName'].value
        if candidate_lname in candidates_with_delegates:

            # Make sure it's in the candidate list (not all states have every candidate)
            if candidate_lname not in candidate_list:
                candidate_list.append(candidate_lname)

            data_by_state[state_id][candidate_lname] = candidate.attributes['dTot'].value


state_out_list = []

primary_dates = csv.DictReader(open('csv/primary_dates.csv', 'r'))

# First, make non-cumulative data by date
for row in primary_dates:
    state_date_row = {'date': row['Date'], 'state': row['State'], 'delegates_available': row['DemDelegates']}

    state_data = data_by_state[row['StateAbb']]
    delegates_projected_total = 0
    for cand, delegates in state_data.items():
        state_date_row[cand] = int(delegates)
        delegates_projected_total += int(delegates)
    state_date_row['delegates_projected'] = delegates_projected_total
    state_out_list.append(state_date_row)

# print(state_out_list)
out_csv = csv.DictWriter(
    open('csv/delegates_by_state.csv', 'w'),
    fieldnames=state_out_list[0].keys()
)
out_csv.writeheader()
out_csv.writerows(state_out_list)
