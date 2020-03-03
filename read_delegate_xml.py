import csv
import sys
from datetime import datetime
from xml.dom import minidom

# When candidates drop out and should stop accumulating delegates. If the stop date is 3/3/2020, for example, delegates for the 3/3/2020 contest will be counted, but any delegates from a theoretical 3/4/2020 contest will not.
stop_counting_dates = {
    'Klobuchar': datetime.strptime('03/03/2020', '%m/%d/%Y'),
    'Buttigieg': datetime.strptime('03/03/2020', '%m/%d/%Y'),
}

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

# Now grab primary dates. Use OrderedDict if it's python v less than 3.7, as on the EC2 box
if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 7):
    from collections import OrderedDict
    data_by_date = OrderedDict()
else:
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
# print("Now: {}".format(today.strftime('%m/%d/%Y')))
for date, candidates in data_by_date.items():
    # only take dates in the past, ignore future contests
    parsed_date = datetime.strptime(date, '%m/%d/%Y')
    if parsed_date <= today:
        # print(parsed_date)
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
    for c in final_candidate_list:
        # Check if this candidate has dropped out and if this is after their stop counting date
        try:
            stop_date = stop_counting_dates[c]
            bool_stop = datetime.strptime(date_row['date'], '%m/%d/%Y') > stop_date
        except:
            bool_stop = False
        if not bool_stop:
            output_row[c] = date_row[c]

    # output_row.update({c: date_row[c] for c in final_candidate_list if date_row['date'] < })
    final_data.append(output_row)

out_csv = csv.DictWriter(
    open('csv/delegates_cumulative.csv', 'w'),
    fieldnames=final_data[0].keys()
)
out_csv.writeheader()
out_csv.writerows(final_data)
