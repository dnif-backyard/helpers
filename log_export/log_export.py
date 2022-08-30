"""
    log_capture file to fetch logs from the DNIF Console
"""
import argparse
import datetime
import re
import subprocess
import sys
import time
import csv
import json
import os
import requests
import yaml
import urllib3
try:
    import pytz
except Exception as err:
    os.system("pip3 install pytz")
    import pytz

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

fmt = '%Y-%m-%dT%H:%M:%S'

def without_conf():
    """
        get the ip_address and token and write to config file
        :return:  ip_address and toker
        :rtype: dictionary
    """
    try:
        data = {}
        print("Config file not found.\n")
        ip_address = str(input(" Enter the Console IP: "))
        cluster_id = str(input(" Enter the Cluster ID: "))
        token = str(input(" Enter the Token: "))


        while True:
            if not ip_address:
                ip_address = str(input("\n Enter the Console IP: "))
            if not cluster_id:
                cluster_id = str(input("\n Enter the Cluster ID: "))
            if not token:
                token = str(input(" Enter the Token: "))
            if all(ip_address and token and cluster_id):
                break

        data['ip_address'] = ip_address
        data['token'] = token
        data['cluster_id'] = cluster_id

        with open('query_config.yaml', 'w') as f_obj:
            yaml.safe_dump(data, f_obj)
        return data
    except IOError as err:
        print("Error in without_conf => ", err)
        return data
    except Exception as err:
        print("Error in without_conf => ", err)
        return data


def convert(time, tz):
    try:
        Stime = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
        tz_obj = pytz.timezone(tz)
        datetime_obj = tz_obj.localize(Stime)
        time_string = datetime_obj.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S")
        return time_string
    except Exception as err:
        print("Error in convert => ", err)

def getduration(pduration):
    """
        get the diff from the pduration
        :return:  diff
        :rtype: date
    """
    pduration = pduration.replace("'", "").rstrip()
    if pduration[-1] == 'd':
        diff = datetime.timedelta(days=int(pduration[:-1]))
    elif pduration[-1] == 'm':
        diff = datetime.timedelta(minutes=int(pduration[:-1]))
    elif pduration[-1] == 'h':
        diff = datetime.timedelta(hours=int(pduration[:-1]))
    elif pduration[-1] == 'M':
        diff = datetime.timedelta(days=int(pduration[:-1]) * 30)
    elif pduration[-1] == 'w':
        diff = datetime.timedelta(weeks=int(pduration[:-1]))
    return diff

def get_clause(where_clause, query):
    try:
        time_zone = subprocess.check_output("cat /etc/timezone", shell=True)
        time_zone = time_zone.decode().strip()
        
        if len([ele for ele in ["$Duration", "$StartTime", "$EndTime"] if (ele in where_clause)]) == 0:
            if where_clause.strip() == "":
                where_clause = where_clause + " $Duration=5m"
            else:
                where_clause = where_clause + " AND $Duration=5m"

        for subpart in re.split(r'AND|NOT', where_clause):    
                if '$Duration' in subpart:
                    cdate = datetime.datetime.now()
                    diff = cdate - getduration(subpart.split('=')[-1])
                    startime = diff.timestamp() * 1000
                    endtime = cdate.timestamp() * 1000
                    start_time = diff.strftime(fmt)
                    end_time = cdate.strftime(fmt)
                    query_alt = f'$StartTime={start_time} AND $EndTime={end_time}'
                    query_list = query.split(" ")
                    for clause in query_list:
                        if "$Duration" in clause:
                            index = query_list.index(clause)
                            query = query.replace(clause, query_alt, index)
                            break
                    break
                elif "$StartTime" in subpart:
                    start_split = subpart.split('=')[-1]
                    startime = datetime.datetime.strptime(start_split.rstrip().replace("'", ""), fmt).timestamp() * 1000
                elif "$EndTime" in subpart:

                    end_split = subpart.split('=')[-1]
                    endtime = datetime.datetime.strptime(end_split.rstrip().replace("'", ""), fmt).timestamp() * 1000
                
        _limit = re.search(r"limit\s+(\d+)", query)
        limit = _limit.group(1)
        return query, startime, endtime, limit
    except Exception as err:
        print("Error in get_clause => ", err)

def get_new_query(query):
    """
        getting the query and converting it into start and end time
        :return:  query, start_time, limit
        :rtype: string, date, integer
    """
    new_query = ''
    startime = ''
    endtime = ''
    limit = 0
    try:
                
        verb_seq = re.findall(r"\s+(window|first|last|limit|group|where|as|IN)\s+", query)

        if "where" in verb_seq:
            where_clause = re.search(r"\s+where\s+(.*?)\s+(group|first|last|limit|as)", query)
            where_clause = where_clause.group(1)

            query, startime, endtime, limit = get_clause(where_clause, query)
            return query, startime, endtime, limit
        else:
            where_clause = ""
            query, startime, endtime, limit = get_clause(where_clause, query)
            return query, startime, endtime, limit
    except IndexError as err:
        print("Error in getting query => ", err)
        return new_query, startime, endtime, limit
    except Exception as err:
        print("Error in getting query => ", err)
        return new_query, startime, endtime, limit


def invoke_call(ip_address, query, token, cluster_id, offset=None, scope_id="default"):
    """
    An api call to the DNIF Console to invoke atask for provided query
    :param ip_address: Console to connect
    :type ip_address: str
    :param query: query to get data for
    :type query: str
    :param token: Auth token
    :type token: str
    :param offset: time
    :type offset: int
    :param scope_id: get date for given scope
    :type scope_id: str
    :return: task_id
    :rtype: str
    """
    task_id = None
    try:
        time_zone = subprocess.check_output("cat /etc/timezone", shell=True)
        time_zone = time_zone.decode().strip()
        task_id = ''
        url = f"https://{ip_address}/{cluster_id}/wrk/api/job/invoke"

        if offset:
            payload = {"query_timezone": time_zone,
                       "scope_id": scope_id,
                       "job_type": "dql",
                       "job_execution": "on-demand",
                       "query": query,
                       "wbkname": "untitled",
                       "wbkid": " ",
                       "offset": offset}
        else:
            payload = {"query_timezone": time_zone,
                       "scope_id": scope_id,
                       "job_type": "dql",
                       "job_execution": "on-demand",
                       "query": query,
                       "wbkname": "untitled",
                       "wbkid": " "}
                       

        headers = {'Token': token,
                   'Content-Type': 'application/json'
                   }
        response = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
        
        if response.status_code == 200:
            res = response.json()
            if res['status'] == 'success':
                task_id = res['data'][0]['id']
        return task_id
    except ConnectionError as conn_err:
        print("Error in Invoke => ", conn_err)
        return task_id
    except Exception as err:
        print("Error in Invoke => ", err)
        return task_id


def get_result(ip_address, task_id, token, cluster_id, limit=100, page_no=1):
    """
    Getting the data for give task_id
    :param ip_address: Console to connect
    :type ip_address: str
    :param task_id: task_id to get data for
    :type task_id: str
    :param token: Auth token
    :type token: str
    :param limit: amount of data to get
    :type limit: int
    :return: res
    :rtype: dict
    """
    try:
        url = f"https://{ip_address}/{cluster_id}/wrk/api/dispatcher/task" \
              f"/result/{task_id}?pagesize={limit}&pageno={page_no}"
        payload = {}
        headers = {'Token': token}
        response = requests.get(url, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            res = response.json()
            if res['status'].lower() == 'success':
                return res
            return {'status': 'failed'}
        return {'status': 'failed'}

    except ConnectionError as conn_err:
        print("Error in get_result => ", conn_err)
        return {'status': 'failed'}
    except Exception as err:
        print("Error in get_result => ", err)
        return {'status': 'failed'}


def get_task_status(ip_address, task_id, token, cluster_id):
    """
    Check status of the task submitted to Console
    :param ip_address: Console to connect
    :type ip_address: str
    :param task_id: check the status for
    :type task_id: str
    :param token: Auth token
    :type token: str
    :return: response
    :rtype: dict
    """
    data = {}
    try:
        url = f"https://{ip_address}/{cluster_id}/wrk/api/dispatcher/task/state/{task_id}"
        payload = {}
        headers = {'Token': token}
        response = requests.get(url, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data['status'].lower() == 'success':
                return data
        return data
    except ConnectionError as conn_err:
        print("Error in get_task_status => ", conn_err)
        return data
    except Exception as err:
        print("Error in get_task_status => ", err)
        return data


def with_scroll(data, query, scope_id, file_type):
    """
    the call brings the data between the time range and limit
    :param data: config data for api call
    :type data: dict
    :param query: user provided query
    :type query: str
    :param scope_id: user provided scope_id else default
    :type scope_id: str
    :param file_type: type of file to store data in
    :type file_type: str
    :return:
    :rtype:
    """
    try:
        timestamp = int(time.time())
        count = 0
        tmp = 0
        task_status_count = 0
        new_query, start_time, endtime, limit = get_new_query(query)
        get_time = endtime
        task_id = invoke_call(data['ip_address'], new_query,
                              data['token'], data['cluster_id'], None, scope_id)

        if task_id:
            while True:
                task_status = get_task_status(data['ip_address'], task_id, data['token'], data['cluster_id'])
                if task_status:
                    if task_status['task_state'] in ['STARTED', 'PENDING']:
                        continue
                    else:
                        if task_status['task_state'] != 'SUCCESS':
                            print("Task Execution Failed for task_id => ", task_id)
                            sys.exit()
                        else:
                            get_data = get_result(data['ip_address'], task_id, data['token'], data['cluster_id'], limit)
                            break
                else:
                    continue

            if get_data['status'].lower() == 'success':
                if file_type == 'csv':
                    with open(f'{timestamp}.csv', 'w', newline='') as f_obj:
                        w_f = csv.writer(f_obj)
                        w_f.writerow(get_data['result'][0].keys())
                        for row in get_data['result']:
                            if row['$CNAMTime'] > int(start_time):
                                w_f.writerow(list(row.values()))
                                count = count + 1
                else:
                    with open(f'{timestamp}.json', 'w') as output_file:
                        for dic in get_data['result']:
                            if dic['$CNAMTime'] > int(start_time):
                                output_file.write(f"{dic}\n")
                                count = count + 1

                print(f"\n\r Writing to file {BOLD}{GREEN}: {timestamp}.{file_type}{END}")
                print(f"\r Status: {YELLOW}IN PROGRESS \t{END} "
                f"Date: {BOLD}{YELLOW}{datetime.datetime.fromtimestamp(get_time/ 1000).strftime(fmt)}\t{END} "
                f"Records written: {BOLD}{YELLOW}{count}\t{END} ", end="")
                        
                
                if len(get_data['result']) != 0 and get_data['total_count'] == int(limit):
                    get_time = get_data['result'][-1]['$CNAMTime']
                    tmp = get_time
                else:
                    print(f"\r Status: {GREEN} COMPLETED \t{END} "
                    f"Date: {BOLD}{GREEN}{datetime.datetime.fromtimestamp(get_time/ 1000).strftime(fmt)}\t{END} "
                    f"Records written: {BOLD}{GREEN}{count}\t{END} ", end="")
                    sys.exit()

                while True:
                    if int(start_time/ 1000) >= int(get_time/ 1000):
                        print(f"\r Status: {GREEN} COMPLETED \t{END} "
                        f"Date: {BOLD}{GREEN}{datetime.datetime.fromtimestamp(get_time/ 1000).strftime(fmt)}\t{END} "
                        f"Records written: {BOLD}{GREEN}{count}\t{END}  \n", end="")
                        break
                    else:
                        task_id = invoke_call(data['ip_address'],
                                              new_query, data['token'], data['cluster_id'], get_time, scope_id)
                        if task_id:
                            while True:
                                task_status = get_task_status(data['ip_address'],
                                                              task_id, data['token'], data['cluster_id'])
                                if task_status:
                                    if task_status['task_state'] in ['STARTED', 'PENDING']:
                                        continue
                                    else:
                                        if task_status['task_state'] != 'SUCCESS':
                                            print("Task Execution Failed for task_id => ", task_id)
                                            print("Log Exported till datetime =>", datetime.datetime.fromtimestamp(get_time/ 1000).strftime(fmt))
                                            sys.exit()
                                        else:
                                            get_data = get_result(data['ip_address'],
                                                                task_id, data['token'], data['cluster_id'], limit)
                                            break
                                else:
                                    continue
                            if get_data['status'].lower() == 'success':

                                if file_type == 'json':
                                    with open(f'{timestamp}.json', 'a') as output_file:
                                        for dic in get_data['result']:
                                            if dic['$CNAMTime'] > int(start_time):
                                                output_file.write(f"{dic}\n")
                                                count = count + 1
                                else:
                                    with open(f'{timestamp}.csv', 'a', newline='') as f_obj:
                                        w_f = csv.writer(f_obj)
                                        for row in get_data['result']:
                                            if row['$CNAMTime'] > int(start_time):
                                                w_f.writerow(list(row.values()))
                                                count = count + 1

                                print(f"\r Status: {YELLOW}IN PROGRESS \t{END} "
                                    f"Date: {BOLD}{YELLOW}{datetime.datetime.fromtimestamp(get_time/ 1000).strftime(fmt)}\t{END} "
                                    f"Records written: {BOLD}{YELLOW}{count}\t{END} ", end="")

                                if get_data['task_status'] == "Task Executed Successfully":
                                    task_status_count = 0
                                    if len(get_data['result']) != 0 and get_data['total_count'] == int(limit) :
                                        get_time = get_data['result'][-1]['$CNAMTime']
                                        if tmp == get_time:
                                            print("Limit too low set limit to maximum EPS seen in Deployment")
                                            sys.exit()
                                        else:
                                            tmp = get_time
                                    else:
                                        print(f"\r Status: {GREEN} COMPLETED \t{END} "
                                        f"Date: {BOLD}{GREEN}{datetime.datetime.fromtimestamp(start_time/ 1000).strftime(fmt)}\t{END} "
                                        f"Records written: {BOLD}{GREEN}{count}\t{END} \n", end="")
                                        sys.exit()
                                else:
                                    if task_status_count > 15:
                                        print(f"{get_data.get('message', 'Something went wrong')} => {task_id}")
                                        print("Log Exported till datetime =>", datetime.datetime.fromtimestamp(get_time/ 1000).strftime(fmt))
                                        sys.exit()
                                    else:
                                        task_status_count = task_status_count + 1
                                        time.sleep(5) 
                            else:
                                time.sleep(10)
                        else:
                            time.sleep(10)
            else:
                time.sleep(10)
        else:
            print(f"Something went Wrong => {datetime.datetime.fromtimestamp(get_time/ 1000).strftime(fmt)}")
    except Exception as err:
        print("Error in with_scroll => ", err)


def without_scroll(data, query, scope_id, file_type):
    """
    the call brings the data between the time range irrespective of limit
    :param data: config data for api call
    :type data: dict
    :param query: user provided query
    :type query: str
    :param scope_id: user provided scope_id else default
    :type scope_id: str
    :param file_type: type of file to store data in
    :type file_type: str
    :return:
    :rtype:
    """
    try:
        timestamp = int(time.time())
        count = 0
        call_again = False
        page_no = 0
        new_query, start_time, end_time, limit = get_new_query(query)
        task_id = invoke_call(data['ip_address'], new_query,
                              data['token'], data['cluster_id'], None, scope_id)
        limit = 100
        limit_check = limit
        if task_id:
            while True:
                task_status = get_task_status(data['ip_address'], task_id, data['token'], data['cluster_id'])
                if task_status['task_state'] in ['STARTED', 'PENDING']:
                    continue
                else:
                    if task_status['task_state'] != 'SUCCESS':
                        print("Task Execution Failed for task_id => ", task_id)
                        sys.exit()
                    else:
                        get_data = get_result(data['ip_address'], task_id, data['token'], data['cluster_id'], limit)
                        break

            if get_data['status'].lower() == 'success':
                if file_type == 'csv':
                    with open(f'{timestamp}.csv', 'w', newline='') as f_obj:
                        w_f = csv.writer(f_obj)
                        w_f.writerow(get_data['result'][0].keys())
                        for row in get_data['result']:
                            if row['$CNAMTime'] > int(start_time):
                                w_f.writerow(list(row.values()))
                                count = count + 1
                else:
                    with open(f'{timestamp}.json', 'w') as output_file:
                        for dic in get_data['result']:
                            if dic['$CNAMTime'] > int(start_time):
                                output_file.write(f"{dic}\n")
                                count = count + 1

                print(f"\n\r Writing to file {BOLD}{GREEN}: {timestamp}.{file_type}{END}")
                print(f"\r Status: {YELLOW}IN PROGRESS \t{END} "
                      f"Records written: {BOLD}{YELLOW}{count}{END} ", end="")

                if get_data['total_count'] > limit_check:
                    call_again = True
                    limit_check = limit_check + limit
                    page_no = 2
                else:
                    print(f"\r Status: {GREEN} COMPLETED \t{END} "
                          f"Records written: {BOLD}{GREEN}{count}{END} \n", end="")
                    sys.exit()

                while call_again:
                    if task_id:
                        while True:
                            task_status = get_task_status(data['ip_address'],
                                                          task_id, data['token'], data['cluster_id'])
                            if task_status['task_state'] in ['STARTED', 'PENDING']:
                                continue
                            else:
                                if task_status['task_state'] != 'SUCCESS':
                                    print("Task Execution Failed for task_id => ", task_id)
                                    sys.exit()
                                else:
                                    get_data = get_result(data['ip_address'], task_id,
                                                          data['token'], data['cluster_id'], limit, page_no)
                                    break

                        if get_data['status'].lower() == 'success':
                            if file_type == 'json':
                                with open(f'{timestamp}.json', 'a') as output_file:
                                    for dic in get_data['result']:
                                        if dic['$CNAMTime'] > int(start_time):
                                            output_file.write(f"{dic}\n")
                                            count = count + 1
                            else:
                                with open(f'{timestamp}.csv', 'a', newline='') as f_obj:
                                    w_f = csv.writer(f_obj)
                                    for row in get_data['result']:
                                        if row['$CNAMTime'] > int(start_time):
                                            w_f.writerow(list(row.values()))
                                            count = count + 1

                            print(f"\r Status: {YELLOW}IN PROGRESS \t{END} "
                                  f"Records written: {BOLD}{YELLOW}{count}{END} ", end="")

                            if get_data['total_count'] > limit_check:
                                limit_check = limit_check + limit
                                call_again = True
                                page_no = page_no + 1
                            else:
                                print(f"\r Status: {GREEN} COMPLETED \t{END} "
                                      f"Records written: {BOLD}{GREEN}{count}{END} \n", end="")
                                sys.exit()
                        else:
                            print("Something went Wrong => Didn't got result")
                    else:
                        print("Something went Wrong => Didn't got the Id")
            else:
                print("Something went Wrong => Didn't got result")
        else:
            print("Something went Wrong => Didn't got the Id")

    except Exception as err:
        print("Error in without_scroll => ", err)


def execute():
    """
    main method for the file
    """
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-q", "--QUERY", help="DQL query")
        parser.add_argument("-no_scroll", "--NO_SCROLL",
                            action='store_true', help="NO Scroll option")
        parser.add_argument("-sid", "--SCOPE_ID", help="scope_id. "
                                                       "[default:default]", default='default')
        parser.add_argument("-ft", "--FILE_TYPE", help="output file format. "
                                                       "(json/csv) [default:json] ", default='json')

        args = parser.parse_args()
        if not args.QUERY:
            print(f'{BOLD} option not provided run python3 log_capture.py --help {END}')
            sys.exit()

        if os.path.exists('query_config.yaml'):
            with open('query_config.yaml', 'r') as f_obj:
                data = yaml.safe_load(f_obj)
        else:
            data = without_conf()

        if args.NO_SCROLL:
            without_scroll(data, args.QUERY, args.SCOPE_ID, args.FILE_TYPE)
        else:
            with_scroll(data, args.QUERY, args.SCOPE_ID, args.FILE_TYPE)

    except Exception as err:
        print("Error in Execute => ", err)


if __name__ == '__main__':
    execute()
