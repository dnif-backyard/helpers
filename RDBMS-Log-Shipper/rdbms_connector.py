#!/usr/bin/env python3
import orjson
import time
import unicodedata
import datetime
import ipaddr
import uuid
import yaml
import os
import traceback
import sys
import ast

from collections import OrderedDict
from event_publisher import EventPublish
from utils import yaml_handler, logg_helper

init_config_path = sys.argv[1]

try:
    if os.path.isfile(init_config_path):
        config = yaml_handler.load(init_config_path)
    else:
        raise Exception("Connector not configured")
except Exception as e:
    raise Exception(e)

connector_path = os.path.dirname(os.path.abspath(__file__))

connector_config = config.get('connector_config', {})
db_config = config.get("database_config", {})
forwarding_config = config.get("forwarding_config", {})

log_level = connector_config.get('log_level', 1)
log_max_bytes = connector_config.get('log_max_bytes', 10000000)  # 10 mb log file limit
log_max_bkup_count = connector_config.get('log_max_backup_count', 10)  # 10 backup log file limit

connector_name = init_config_path.split('/')[-1].split('.')[0]

# Log config file handling
default_log_file = f"{connector_path}/log/{connector_name}/{connector_name}.log"
log_file = connector_config.get('log_file_path', default_log_file)

# Create directory for logging if not exist
log_directory = os.path.dirname(os.path.abspath(log_file))
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Bookmark config file handling
default_bookmark_file = f"{connector_path}/bookmark/{connector_name}.yml"
bookmark_file = connector_config.get('bookmark_path', default_bookmark_file)

# Create directory for bookmarking if not exist
bookmark_directory = os.path.dirname(os.path.abspath(bookmark_file))
if not os.path.exists(bookmark_directory):
    os.makedirs(bookmark_directory)

bookmark = dict()

# Database query default value
marker_initial_value = db_config.get('initial_value', '')
query_vars = dict()
query_vars['field_name'] = db_config.get('field_name', '')

logger = logg_helper.get_logger(f"RDBMS_{connector_name}", int(log_level), file_name=log_file,
                                max_bytes=log_max_bytes, backup_count=log_max_bkup_count)
logger.info(f"Log level set to {log_level}")


# Load package for odbc/jdbc
mode = db_config.get('connection_mode', '').lower()

if not mode:
    logger.error("'connection_mode' not configured in 'database_config' section")
    logger.info("Configure valid connection_mode [odbc, jdbc]")
    sys.exit(0)
elif mode == 'odbc':
    # import package for ODBC
    import pyodbc
elif mode == 'jdbc':
    # import package for JDBC
    import jaydebeapi

    # Export JDBC driver path to CLASSPATH environment variable
    default_jars = [f"{connector_path}/rdbms_jar/postgresql-42.2.9.jar",
                    f"{connector_path}/rdbms_jar/ojdbc8.jar",
                    f"{connector_path}/rdbms_jar/mysql-connector-java-8.0.21.jar",
                    f"{connector_path}/rdbms_jar/mssql-jdbc-7.4.1.jre11.jar"
                    ]
    os.environ['CLASSPATH'] = db_config.get('classpath', ":".join(default_jars))
else:
    logger.error(f"Invalid connection_mode '{mode}' configured")
    logger.info("Valid connection_mode [odbc, jdbc]")
    sys.exit(0)


def fix_datatype(row):
    for key, value in row.items():
        try:
            if key in ['AnalyzerIPV4', 'SourceIPV4', 'TargetIPV4']:
                if value is not None:
                    row[key] = str(ipaddr.IPv4Address(abs(value)))
            elif key in ['AnalyzerIPV6', 'SourceIPV6', 'TargetIPV6']:
                if value is not None:
                    row[key] = str(ipaddr.IPv6Address(ipaddr.Bytes(value)))
            elif value is None:
                row[key] = 'NULL'
            elif type(value) is bytes:
                row[key] = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
            elif type(value) is datetime.datetime:
                row[key] = value.isoformat()
            elif type(value) is uuid.UUID:
                row[key] = value.hex
            elif 'java class' in str(type(value)):
                try:
                    row[key] = value.toString()
                except:
                    row[key] = value
        except Exception as e:
            logger.warning(f"value of '{key}' is not valid. Warning: {e}")
    return row


def get_connection():
    try:
        logger.debug("Connecting to the database server..")

        connection_string = db_config.get('connection_string', '')
        if not connection_string:
            logger.error("'connection_string' not defined in 'database_config' section")
            logger.info("Specify proper 'connection_string' in 'database_config' section")
            raise Exception("'connection_string' not defined in 'database_config' section")

        if mode == 'odbc':
            connection = pyodbc.connect(connection_string)
            logger.info("Connected to the database server by ODBC!")
            return connection
        elif mode == 'jdbc':
            connection_driver = db_config.get("connection_driver", '')
            username = db_config.get("user", '')
            password = db_config.get("password", '')

            if not connection_driver:
                logger.error("'connection_driver' not defined in 'database_config' section")
                logger.info("Specify proper 'connection_driver' in 'database_config' section")
                raise Exception("'connection_driver' not defined in 'database_config' section")
            elif not username or not password:
                logger.error("'user' or 'password' not defined in 'database_config' section")
                logger.info("Specify proper 'user' and 'password' in 'database_config' section")
                raise Exception("'user' or 'password' not defined in 'database_config' section")

            connection = jaydebeapi.connect(connection_driver, connection_string, [username, password])
            logger.info("Connected to the database server by JDBC!")
            return connection

    except Exception as e:
        logger.error(f"Error in database connectivity : {e}")


def fetch_log(connection):
    global bookmark, query_vars

    try:
        log_data = []

        logger.debug("Creating DB cursor")
        cursor = connection.cursor()

        marker_value = bookmark.get('marker_value', marker_initial_value)

        if not marker_value:
            logger.error("'initial_value' not defined in 'database_config' section")
            logger.info("Specify proper 'initial_value' in 'database_config'")
            raise Exception("'initial_value' not defined in 'database_config' section")
        elif not query_vars['field_name']:
            logger.error("'field_name' not defined in 'database_config' section")
            logger.info("Specify proper 'field_name' in 'database_config'")
            raise Exception("'field_name' not defined in 'database_config' section")

        query_vars['initial_value'] = marker_value
        query_str = db_config.get('query', '')
        query = query_str.format(**query_vars)
        logger.debug(f"SQL query : {query}")

        cursor.execute(query)
        logger.debug("SQL query executed!")

        rows = cursor.fetchall()
        logger.debug("SQL query Result Fetched!")

        if rows is not None:
            desc = [unicodedata.normalize('NFKD', d[0]).encode('ascii', 'ignore') for d in cursor.description]
            key = []
            for i in desc:
                key.append(i.decode())
            # create list of dictionaries from desc and rows
            count = 0
            for row in rows:
                count += 1
                result = fix_datatype(dict(zip(key, row)))

                if count == len(rows):
                    # Set the bookmark and write into config file
                    bookmark['marker_value'] = str(result[db_config['field_name']])
                    with open(bookmark_file, 'w') as yaml_file:
                        yaml.safe_dump(bookmark, yaml_file)
                log_data.append(str(result))

            logger.debug(f"Log sent till : {db_config['field_name']} = {bookmark.get('marker_value', '')}")
        return log_data

    except Exception as e:
        logger.error(f"Error in rdbms connector: {e}")
        logger.debug(traceback.format_exc())

    finally:
        try:
            cursor.close()
        except:
            logger.error("Unable to close cursor")


def execute():
    try:
        if config:
            logger.info("configuration received")
        else:
            logger.error("connector not configured")
            sys.exit(0)

        global bookmark

        backoff = connector_config.get('backoff_duration', 10)

        if os.path.exists(bookmark_file):
            try:
                with open(bookmark_file, 'r') as stream:
                    bookmark = yaml.safe_load(stream)
            except Exception as e:
                logger.error(f"Could not open bookmark file : {e}")
                sys.exit(0)

        connection = get_connection()

        if connection:
            evt_pub_config = {}
            evt_pub_config.update(connector_config)
            evt_pub_config.update(forwarding_config)

            evt_pub_obj = EventPublish(evt_pub_config)
            success = evt_pub_obj.check_config()
            if not success:
                logger.error("Event publisher check config failed!")
                raise Exception("Event publisher check config failed!")

            evt_pub_obj.spawn_threads()

            while True:
                logs = fetch_log(connection)
                if not logs:
                    logger.info(f"No logs to fetch. Sleeping for {backoff} seconds")
                    if isinstance(backoff, str):
                        time.sleep(int(backoff))
                    else:
                        time.sleep(backoff)
                else:
                    logger.debug("Logs received")
                    for raw_log in logs:
                        try:
                            log_event = OrderedDict()
                            log_event['log_source'] = connector_config.get('log_source', '')
                            log_event.update(ast.literal_eval(raw_log))
                        except Exception as e:
                            logger.error(f"Error updating 'log_source' : {e}")
                            logger.warning("Skipping log. Check 'raw_log' in DEBUG mode")
                            logger.debug(f"raw_log : {raw_log}")
                            continue
                        evt_pub_obj.sendtoevtbuffer(orjson.dumps(log_event))
                        logger.debug("Log sent to buffer")

    except Exception as e:
        logger.error(e)
        sys.exit(0)

    finally:
        try:
            connection.close()
        except:
            logger.error("Unable to close database connection")


if __name__ == "__main__":
    execute()
