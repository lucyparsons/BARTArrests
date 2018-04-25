'''
Parsing bart arrest data. Fields per arrest are:
['Primary Location', 'Sex', 'Race', 'Case_Number', 'Date_Arrest', 'D.O.B']

To get sex and race I find lines that start with "Sex:" & "Race:" then take the
last character as the sex/race. This works except when there is a line break in
the middle of the field, which is pretty rare.

For primary loc, case number, arrest date, the data was the next line after the
line that had the field name.

The text file has different arrests interleaved, however from a cursory reading
each field is ordered in the file. So I gather the each field one at a time
into an array, then combine these field arrays to get an array of arrests.

If a fields values are not totally ordered it is possible for this to create
arrests near each other with swapped field values. But the error should not
propogate throughout the arrests. And I think the values are *mostly* ordered.

One arrest is a dictionary keyed by the field names.

This Doesn't get D.O.B. because the dob value didn't appear in a regular way.
One way to get it would be to scan the document and create an array of each
date before ~18ish years ago.

I'm not even trying to get the violation info, but that is in the files

'''
from glob import glob
from collections import defaultdict
import json

next_line_fields = ['Primary Location', 'Case_Number', 'Date_Arrest']
same_line_fields = ['Sex:', 'Race:']


def find(string, name):
    '''Like `str.find` but raises an error if not found.'''
    res = string.find(name)
    if res == -1:
        raise ValueError('not found')
    return res


def next_line_name(x, name):
    '''
    Find the value in `x` for the `name` field, return remainder of `x` and
    field value
    '''
    x = x[find(x, name):]
    x = x[find(x, '\n') + 1:]
    loc = find(x, '\n')
    return x[:loc], x[loc:]


def get_field_values(data_, field):
    values = []
    data = data_
    while data:
        try:
            res, data = next_line_name(data, field)
        except ValueError:
            break
        values.append(res)
    return values


def parse_file(data):
    field_dict = defaultdict(list)
    lines = data.split('\n')
    for line in lines:
        for field in same_line_fields:
            if line.startswith(field):
                s = line[-1]
                field_dict[field].append(s)
    [field_dict[field].extend(get_field_values(data, field))
        for field in next_line_fields]

    arrest_array = construct_arrests(field_dict)
    return field_dict, arrest_array


def construct_arrests(field_dict):
    fields, values = field_dict.keys(), list(field_dict.values())
    arrest_tuples = zip(*values)
    return map(lambda a: dict(zip(fields, a)), arrest_tuples)


arrest_array = []
arrest_fields = defaultdict(list)
for name in sorted(glob("txts/*.txt"), key=lambda x: int(x[-8:-4])):
    with open(name) as fh:
        year_dict, year_array = parse_file(fh.read())
        [arrest_fields[k].extend(v) for k, v in year_dict.items()]
        arrest_array.extend(year_array)
print(json.dumps(
    {'arrest_array': arrest_array, 'arrest_fields': arrest_fields},
    indent=2))