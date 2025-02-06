import json
import os
import re
import pandas as pd
import sys
import argparse
import logging

#this does not need to be a argument, it does not change 
path_to_duplicate_csv = "/scratch/projects/sam/repos/SABD_Replication_SB/data_processing/SEA_Lab_query_corpus_ground_truth_Final.csv"

if __name__ == '__main__':
    #adding arguments
    parser = argparse.ArgumentParser(description='Process some integers.') #left it the same as the parser in create_test_set
    parser.add_argument('--project_name', required=True, help="name of the project, used for jsonl file name")
    parser.add_argument('--project_path', required=True, help="path to project containing json format issues")
    args = parser.parse_args()

    project_path = args.project_path
    project_name = args.project_name
    path_to_jsonl_file = os.path.join(project_path,(project_name + ".jsonl"))

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()

    logger.addHandler(logging.StreamHandler())
    os.makedirs('./log', exist_ok=True)
    fileHandler = logging.FileHandler('./log/json_to_jsonl_{}.log'.format(project_name))
    logger.addHandler(fileHandler)

    logger.info(args)

    #saving each bug report in a dictionary, it will be a dictionary of dictionaries, the key will be the bug_report and the value will be all necessary fields for the jsonl file
    jsonl_dictionary_list = []

    #loop through json files in project:
    #get all files in a folder
    #itterate through each path, until no more files in the folder
    #change path_to_json_file each time
    bug_reports = os.listdir(project_path)

    logger.info("Extracting important fields from json issues in project {}".format(project_name))

    for bug_report in bug_reports:
        path_to_report = os.path.join(project_path,bug_report)

        #for each file, open input data json file to read
        try:
            with open(path_to_report, 'r') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
                logger.error("Error: input issue report {} file not found".format(path_to_report))
        #need to process creation ts into right format before adding to dictionary
        split_created_at = re.split(r"[TZ]", data['created_at'])
        creation_ts = split_created_at[0] + " " + split_created_at[1] + " " + "+0000"  

        #dup_id!!
        #load csv of spread sheet into data processing folder
        #go to csv file
        #find dup_id for bug_id
        #populate dup_id field of jsonl_dictionary
        duplicate_csv = pd.read_csv(path_to_duplicate_csv)
        project_reports = duplicate_csv[duplicate_csv["Repository_Name"] == project_name]

        #this should check if the issue number is in 
        if project_reports["query"].isin([data['number']]).any():
            curr_corresponding_row = project_reports[project_reports["query"] == data['number']]
            csv_index = curr_corresponding_row.index[0]
            ground_truth_string = curr_corresponding_row.loc[csv_index][3]
            #adds only the numbers from the ground truth string to the ground truth list
            ground_truth_list = [number for number in (re.split(r"[\[\]\|]", ground_truth_string)) if number.isalnum()]
            curr_dup_id = ground_truth_list[0]
        else:
            #if the current dup_id has no ground truth, its ground truth is an empty list
            curr_dup_id = []

        
        
        #this is done because csv index is maintained even in filtered data frame, need exact index for look up

        jsonl_dictionary = {'bug_id': str(data['number']),'creation_ts':creation_ts,'short_desc':data['title'],'product':"",'component':"",'version':"",'bug_status':data['state'],'priority':"",'bug_severity':"", 'description':data['body'],'dup_id':curr_dup_id}
        jsonl_dictionary_list.append(jsonl_dictionary)
        logger.info("issue {} processed".format(data['number']))
        json_file.close()

    #for each dictionary within jsonl_dictionary create a new json object and add to jsonl file
    logger.info("writing to jsonl file at path {}".format(path_to_jsonl_file))
    try:
        with open(path_to_jsonl_file, 'w') as jsonl_file:
            for dict in jsonl_dictionary_list:
                jout = json.dumps(dict) + '\n'
                jsonl_file.write(jout)
    except FileNotFoundError:
        logger.error("Output file not created")

        jsonl_file.close()

   

    

    




    

