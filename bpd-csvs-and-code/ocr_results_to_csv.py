import argparse
import csv
import re

from google.cloud import storage
from google.cloud import vision_v1p2beta1 as vision
from google.protobuf import json_format


"""
Example:
    python ocr_results_to_csv.py --gcs-source-prefix ocr/2017
"""

BUCKET_NAME = 'bpd-arrests'

DATE_OF_ARREST_REGEX = '(\d{2}|\d \d)/\d{2}/\d{2} \d{2}:\d{2}'
DATE_OF_BIRTH_REGEX = '\d{2}(/|1)?\d{2}(/|1)?\d{4}'

CODES = ['VC', 'PC', 'HS', 'BP']

TERMS = ['WARRANT', 'MISDEMEANOR', 'FELONY']


# Debug Helpers
def get_list_of_blobs(prefix):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name=BUCKET_NAME)
    return list(bucket.list_blobs(prefix=prefix))


def get_responses_from_blob(blob):
    json_string = blob.download_as_string()
    response = json_format.Parse(
        json_string, vision.types.AnnotateFileResponse())
    return response.responses


def text_from_ocr_results(prefix):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name=BUCKET_NAME)

    for blob in bucket.list_blobs(prefix=prefix):
        json_string = blob.download_as_string()
        response = json_format.Parse(
            json_string, vision.types.AnnotateFileResponse())

        for page in response.responses:
            yield page.full_text_annotation.text


def process_text_blob(text_blob):
    rows = []

    blocks = text_blob.split('Case Number')
    if blocks[0] == '':
        blocks = blocks[1:]
    if blocks[-1] == '':
        blocks = blocks[:-1]

    for block in blocks:
        row = {}

        split_block = block.split('\n')
        if split_block[0] == '':
            split_block = split_block[1:]
        if split_block[-1] == '':
            split_block = split_block[:-1]

        row['case_number'] = split_block[0]

        try:
            split_block.index('Date Arrest')
            split_block.index('Primary Location')
            row['location'] = split_block[split_block.index('Primary Location')+1]
        except ValueError:
            # for now, we'll just skip it
            continue

        if re.search('[a-zA-Z]', row['location']) is None:
            # wasn't placed directly after the 'Primary Location' label, gotta try and find it.
            # TODO: this is ugly
            loc = [x for x in split_block if 'CA' in x]

            if len(loc) > 1:
                print('got multiple locations: {}'.format(loc))

            if len(loc):
                row['location'] = loc[0]

        doa = [x for x in split_block if re.search(DATE_OF_ARREST_REGEX, x)]
        if len(doa):
            row['date_of_arrest'] = re.search(DATE_OF_ARREST_REGEX, doa[0]).group()

        # Transform '0 5/20/17 20:56' -> '05/20/17 20:56'
        if row.get('date_of_arrest') is not None:
            if row['date_of_arrest'].startswith('0 ') or row['date_of_arrest'].startswith('1 '):
                split_date = row['date_of_arrest'].split(' ')
                row['date_of_arrest'] = ' '.join([''.join(split_date[0:2]), split_date[-1]])

        dob = [x for x in split_block if re.search(DATE_OF_BIRTH_REGEX, x)]
        if len(dob):
            row['dob'] = re.search(DATE_OF_BIRTH_REGEX, dob[0]).group()
            try:
                row['dob'] = clean_dob(row['dob'])
            except IndexError:
                pass

        sex = [x for x in split_block if re.search('Sex: [a-zA-Z]', x)]
        if len(sex):
            row['sex'] = re.search('Sex: [a-zA-Z]', sex[0]).group()[-1].upper()

        race = [x for x in split_block if re.search('Race: [a-zA-Z01]', x)]
        if len(race):
            row['race'] = re.search('Race: [a-zA-Z01]', race[0]).group()[-1].upper()
            if row['race'] == '0':
                row['race'] = 'O'
            if row['race'] == '1':
                row['race'] = 'I'

        crimes = [x for x in split_block if any([code for code in CODES if code in x])]
        if len(crimes):
            row['crimes'] = ' | '.join(crimes)


        rows.append(row)
    return rows


# Used to assist with a common OCR error
# '12/12/1990' -> '12/12/1990'
# '12112/1990' -> '12/12/1990'
# '12/1211990' -> '12/12/1990'
# '1211211990' -> '12/12/1990'
# '1212/1990'  -> '12/12/1990'
# '12/121990'  -> '12/12/1990'
def clean_dob(dob):
    split = list(dob)
    if len(split) == 10:
        split[2] = '/'
        split[5] = '/'
        return ''.join(split)
    elif len(split) in [8, 9]:
        day, month, year = '', '', ''
        for x in split:
            try:
                int(x)
                if len(day) != 2:
                    day += x
                elif len(month) != 2:
                    month += x
                elif len(year) != 4:
                    year += x
            except ValueError:
                pass
        return '/'.join([day, month, year])

    return dob


def list_of_rows_to_csv(rows, output):
    with open(output+".csv", 'w') as output_file:
        ROW_KEYS = ['case_number', 'date_of_arrest', 'sex', 'race', 'dob', 'location', 'crimes']
        dict_writer = csv.DictWriter(output_file, ROW_KEYS)
        dict_writer.writeheader()
        dict_writer.writerows(rows)


def ocr_dump_to_rows(prefix):
    all_rows = []
    for text_blob in text_from_ocr_results(prefix):
        all_rows.append(process_text_blob(text_blob))
    return all_rows


def main(prefix):
    all_rows = ocr_dump_to_rows(prefix)

    list_of_rows_to_csv(sum(all_rows, []), prefix.replace('/', '-'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gcs-source-prefix', required=True)
    args = parser.parse_args()
    main(args.gcs_source_prefix)
