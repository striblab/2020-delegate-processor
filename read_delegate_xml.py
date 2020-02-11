import csv
from datetime import datetime
from xml.dom import minidom

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

        # Make sure it's in the candidate list (not all states have every candidate)
        if candidate_lname not in candidate_list:
            candidate_list.append(candidate_lname)

        data_by_state[state_id][candidate_lname] = candidate.attributes['dTot'].value

# Now grab primary dates
data_by_date = {}
primary_dates = csv.DictReader(open('csv/primary_dates.csv', 'r'))

# First, make non-cumulative data by date
for row in primary_dates:
    if row['Date'] not in data_by_date.keys():
        data_by_date[row['Date']] = {candidate: 0 for candidate in candidate_list}

    state_data = data_by_state[row['StateAbb']]
    for cand, delegates in state_data.items():
        data_by_date[row['Date']][cand] += int(delegates)

# Now make an object to keep a running total
candidate_running_delegate_total = {candidate: 0 for candidate in candidate_list}

data_by_date_cumulative = []

# Make an initial starting point with 0s
start_date_obj = {'date': '02/01/2020'}
start_date_obj.update(candidate_running_delegate_total)
data_by_date_cumulative.append(start_date_obj)


today = datetime.today()
print("Now: {}".format(today.strftime('%m/%d/%Y')))
for date, candidates in data_by_date.items():
    # only take dates in the past, ignore future contests
    parsed_date = datetime.strptime(date, '%m/%d/%Y')
    if parsed_date <= today:
        print(parsed_date)
        date_obj = {
            'date': date
        }
        for c, value in candidates.items():
            # As you go through each date add new values to cumulative total
            candidate_running_delegate_total[c] += value
            date_obj[c] = candidate_running_delegate_total[c]
        data_by_date_cumulative.append(date_obj)

# Find candidates with more than zero cumulative delegates
final_candidate_list = []
last_row = data_by_date_cumulative[-1]
for cand, total in last_row.items():
    if cand != 'date':
        if total > 0:
            final_candidate_list.append(cand)

# Assemble final data, filtering out candidates with zero delegates
final_data = []
for date_row in data_by_date_cumulative:
    output_row = {'date': date_row['date']}
    output_row.update({c: date_row[c] for c in final_candidate_list})
    final_data.append(output_row)

out_csv = csv.DictWriter(
    open('csv/delegates_cumulative.csv', 'w'),
    fieldnames=final_data[0].keys()
)
out_csv.writeheader()
out_csv.writerows(final_data)
