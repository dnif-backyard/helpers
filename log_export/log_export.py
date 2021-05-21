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
        token = str(input(" Enter the Token: "))

        while True:
            if not ip_address:
                ip_address = str(input("\n Enter the Console IP: "))
            if not token:
                token = str(input(" Enter the Token: "))
            if all(ip_address and token):
                break

        data['ip_address'] = ip_address
        data['token'] = token

        with open('query_config.yaml', 'w') as f_obj:
            yaml.safe_dump(data, f_obj)
        return data
    except IOError as err:
        print("Error in without_conf => ", err)
        return data
    except Exception as err:
        print("Error in without_conf => ", err)
        return data


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


def get_new_query(query):
    """
        getting the query and converting it into start and end time
        :return:  query, start_time, limit
        :rtype: string, date, integer
    """
    try:
        fmt = '%Y-%m-%dT%H:%M:%S'
        new_query =''
        startime = ''
        query_list = query.split()
        for i in query_list:
            if '$Duration' in i:
                chng_date = datetime.datetime.now() - getduration(i.split('=')[-1])
                startime = chng_date.timestamp() * 1000
                endtime = datetime.datetime.now().timestamp() * 1000
                start_time = datetime.datetime.fromtimestamp(startime / 1000).strftime(fmt)
                end_time = datetime.datetime.fromtimestamp(endtime / 1000).strftime(fmt)
                query_alt = f'$StartTime={start_time} AND $EndTime={end_time}'
                index = query_list.index(i)
                new_query = query.replace(i, query_alt, index)
        _limit = re.search(r"limit\s+(\d+)", query)
        limit = _limit.group(1)

        return new_query, startime, limit
    except IndexError as err:
        print("Error in getting query => ", err)
        return new_query, startime, limit
    except Exception as err:
        print("Error in getting query => ", err)
        return new_query, startime, limit


def invoke_call(ip_address, query, token, offset=None, scope_id="default"):
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
    try:
        time_zone = subprocess.check_output("cat /etc/timezone", shell=True)
        time_zone = time_zone.decode().strip()
        task_id = ''
        url = f"https://{ip_address}/wrk/api/job/invoke"

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


def get_result(ip_address, task_id, token, limit=100):
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
        url = f"https://{ip_address}:8090/wrk/api/dispatcher/task" \
              f"/result/{task_id}?pagesize={limit}&pageno=1"
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


def get_task_status(ip_address, task_id, token):
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
    try:
        data = {}
        url = f"https://{ip_address}/wrk/api/dispatcher/task/state/{task_id}"
        payload = {}
        headers = {'Token': token}
        response = requests.get(url, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data['status'].lower() == 'success':
                return data
            else:
                print('Task Execution Failed Try Again')
                sys.exit()
        return data
    except ConnectionError as conn_err:
        print("Error in get_task_status => ", conn_err)
        return data
    except Exception as err:
        print("Error in get_task_status => ", err)
        return data


def execute():
    """
    main method for the file
    """
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-q", "--QUERY", help="DQL query")
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

        timestamp = int(time.time())
        count = 0
        new_query, start_time, limit = get_new_query(args.QUERY)

        task_id = invoke_call(data['ip_address'], new_query,
                              data['token'], None, args.SCOPE_ID)
        if task_id:
            while True:
                task_status = get_task_status(data['ip_address'], task_id, data['token'])
                if task_status['task_state'] in ['STARTED', 'PENDING']:
                    continue
                else:
                    if task_status['task_state'] != 'SUCCESS':
                        print("Tasking Execution Failed Please Try Again")
                        sys.exit()
                    else:
                        get_data = get_result(data['ip_address'], task_id, data['token'], limit)
                        break

            if get_data['status'].lower() == 'success':
                if args.FILE_TYPE == 'csv':
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

                print(f"\n\r Writing to file {BOLD}{GREEN}: {timestamp}.{args.FILE_TYPE}{END}")
                print(f"\r Status: {YELLOW}IN PROGRESS \t{END} "
                      f"Records written: {BOLD}{YELLOW}{count}{END} ", end="")

                if len(get_data['result']) != 0:
                    get_time = get_data['result'][-1]['$CNAMTime']
                else:
                    print(f"\r Status: {GREEN} COMPLETED \t{END} "
                          f"Records written: {BOLD}{GREEN}{count}{END} \n", end="")
                    sys.exit()

                while True:
                    if int(start_time) >= get_time:
                        print(f"\r Status: {GREEN} COMPLETED \t{END} "
                              f"Records written: {BOLD}{GREEN}{count}{END} \n", end="")
                        break
                    else:
                        task_id = invoke_call(data['ip_address'],
                                              new_query, data['token'], get_time, args.SCOPE_ID)
                        if task_id:
                            while True:
                                task_status = get_task_status(data['ip_address'],
                                                              task_id, data['token'])
                                if task_status['task_state'] in ['STARTED', 'PENDING']:
                                    continue
                                else:
                                    if task_status['task_state'] != 'SUCCESS':
                                        print("Tasking Execution Failed Please Try Again")
                                        sys.exit()
                                    else:
                                        get_data = get_result(data['ip_address'], task_id, data['token'], limit)
                                        break

                            if get_data['status'].lower() == 'success':

                                if args.FILE_TYPE == 'json':
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

                                if len(get_data['result']) != 0:
                                    get_time = get_data['result'][-1]['$CNAMTime']
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

    except IndexError as err:
        print("Error in getting query => ", err)
    except Exception as err:
        print("Error in Execute => ", err)


if __name__ == '__main__':
    execute()
