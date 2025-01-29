import json
import os
import re
import pandas as pd


project_path = "/scratch/projects/sam/repos/SABD_Replication_SB/dataset/andOTP"
path_to_jsonl_file = "../dataset/andOTP/andOTP_test.jsonl"
path_to_duplicate_csv = "/scratch/projects/sam/repos/SABD_Replication_SB/data_processing/SEA_Lab_Data_And_Duplicate_Information.csv"
project_name = "andOTP"


if __name__ == '__main__':
    #saving each bug report in a dictionary, it will be a dictionary of dictionaries, the key will be the bug_report and the value will be all necessary fields for the jsonl file
    jsonl_dictionary_list = []

    #loop through json files in project:
    #get all files in a folder
    #itterate through each path, until no more files in the folder
    #change path_to_json_file each time
    bug_reports = os.listdir(project_path)
    for bug_report in bug_reports:
        path_to_report = os.path.join(project_path,bug_report)

        #for each file, open input data json file to read
        try:
            with open(path_to_report, 'r') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
                print("error, file not found")
        #need to process creation ts into right format before adding to dictionary
        split_created_at = re.split(r"[TZ]", data['created_at'])
        creation_ts = split_created_at[0] + " " + split_created_at[1] + " " + "+0000"  

        #dup_id!!
        #load csv of spread sheet into data processing folder
        #go to csv file
        #find dup_id for bug_id
        #populate dup_id field of jsonl_dictionary
        duplicate_csv = pd.read_csv(path_to_duplicate_csv)
        curr_corresponding_row = duplicate_csv[((duplicate_csv['Repository_Name'] == project_name) and (duplicate_csv['Issue_Number'] == data['number']))]
        print(curr_corresponding_row)

        jsonl_dictionary = {'bug_id': str(data['number']),'creation_ts':creation_ts,'short_desc':data['title'],'product':"",'component':"",'version':"",'bug_status':data['state'],'priority':"",'bug_severity':"", 'description':data['body'],'dup_id':"list with one element, the bug id"}
        jsonl_dictionary_list.append(jsonl_dictionary)
        json_file.close()

    #for each dictionary within jsonl_dictionary create a new json object and add to jsonl file
    try:
        with open(path_to_jsonl_file, 'w') as jsonl_file:
            for dict in jsonl_dictionary_list:
                jout = json.dumps(dict) + '\n'
                jsonl_file.write(jout)
    except FileNotFoundError:
        print("error file not found")

        jsonl_file.close()

   

    

    




    

