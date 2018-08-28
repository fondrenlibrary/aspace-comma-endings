#!/usr/bin/env python

import re
from tqdm import tqdm
import pandas as pd
import datetime
import asnake.logging as logging
today_date = datetime.datetime.today().strftime('%Y-%m-%d')
logging.setup_logging(filename='comma_end_logfile_funct_' + str(today_date) + '.log')
logger = logging.get_logger('comma_end_changes_log')
from asnake.client import ASnakeClient

client = ASnakeClient(baseurl='xxx',
                      username='xxx',
                      password='xxx')
client.authorize()


def pattern_matcher(x):
    """Match a resource title that ends with a comma."""
    pattern_match = re.compile(r'^.*\,$')
    result = pattern_match.match(x)
    return result


def extract_resources(y):
    """Look for ArchivesSpace resources that match pattern_matcher, then save them in a list and generate a CSV report."""
    if y == 'resources':
        obj_type = 'resource_records'
        all_records = client.get('repositories/2/resources', params={'all_ids': True}).json()
        base_uri = 'repositories/2/resources/'
        identifier = 'id_0'
    elif y == 'archival objects':
        obj_type = 'archival_objects'
        all_records = client.get('repositories/2/archival_objects', params={'all_ids': True}).json()
        base_uri = 'repositories/2/archival_objects/'
        identifier = 'ref_id'
    rec_index = []
    rec_titles = []
    rec_coll_nums = []
    print('Extracting...')
    for record in tqdm(all_records):
        uri = base_uri + str(record)
        try:
            record_detail = client.get(uri).json()
            record_title = record_detail['title']
            if pattern_matcher(record_title):
                rec_coll_num = record_detail[identifier]
                rec_index.append(record)
                rec_titles.append(record_title)
                rec_coll_nums.append(rec_coll_num)
        except:
            pass
    rec_df = pd.DataFrame()
    rec_df['Identifier'] = rec_coll_nums
    rec_df['Resource_no'] = rec_index
    rec_df['Collection_Title'] = rec_titles
    indexed_rec_df = rec_df.set_index(['Identifier'])
    today_date = datetime.datetime.today().strftime('%Y-%m-%d')
    file_name = 'comma_ending_' + obj_type + '_' + str(today_date) + '.csv'
    indexed_rec_df.to_csv(file_name)
    print('Extracted ' + str(len(rec_index)) + ' ' + y + ' with titles ending in commas.')
    return indexed_rec_df


def title_changer(z, q):
    """Change any matching resource titles found with extract_resources, with upload details saved to log file."""
    if z == 'resources':
        base_uri = 'repositories/2/resources/'
    elif z == 'archival objects':
        base_uri = 'repositories/2/archival_objects/'
    all_records = q['Resource_no'].tolist()
    found_records = []
    changed_records = []
    print('Processing ' + z + ' for title fixing...')
    for record in tqdm(all_records):
        uri = base_uri + str(record)
        try:
            record_detail = client.get(uri).json()
            record_title = record_detail['title']
            if pattern_matcher(record_title):
                found_records.append(record)
                logger.info('Title ending with comma found', record=uri)
                record_detail['title'] = re.sub(r'\,$', '', record_detail['title'])
                response = client.post(uri, json=record_detail)
                if response.status_code == 200:
                    logger.info('Title change pushed', response=response)
                    changed_records.append(record)
                else:
                    logger.info('Title changed failed', response=response)
            else:
                pass
        except:
            pass
    outcome = 'Processed ' + str(len(found_records)) + ' ' + z + ' and corrected ' + str(len(changed_records)) + ' titles.'
    return outcome


df_resources = extract_resources('resources')
title_changer('resources', df_resources)

df_arch_objs = extract_resources('archival objects')
title_changer('archival objects', df_arch_objs)
