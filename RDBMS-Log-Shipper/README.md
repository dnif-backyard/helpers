## Overview

RDBMS stands for Relational Database Management System. RDBMS is the basis for SQL, and for all modern database systems like MS SQL Server, IBM DB2, Oracle, MySQL, and Microsoft Access.

The RDBMS connector fetches logs from the Database server through ODBC or JDBC and forwards to DNIF Core using UDP or TCP client.

## Prerequisite

Requires atleast Java JDK version-14 to connect database through JDBC. Also, Ensure JAVA_HOME environment variable is set.

## Setup

1. Clone the helpers repository from github.

    `git clone https://github.com/rajboke2/helpers.git -b rdbms_log_shipper`
2. Go inside the RDBMS-Log-Shipper directory.

    `cd helpers/RDBMS-Log-Shipper/`
3. Run the requirement.sh as shown below:

    `bash requirement.sh`

## Configuration

Create configuration file inside RDBMS-Log-Shipper/config/ directory or in any desired location.

Below is the sample configuration format using JDBC.

    connector_config:
        log_source: ""
    database_config:
        query: "select * from TABLE_NAME where {field_name} > {initial_value} limit FETCH_LIMIT"
        field_name: somefield
        initial_value: ""
        connection_mode: jdbc
        connection_string: ""
        classpath: ""
        connection_driver: ""
        user: ""
        password: ""
    forwarding_config:
        dst_ip: ""
        dst_port: ""
        transfer_type: udp

##### Note
For ODBC, You need to change the 'connection_mode' to 'odbc' and need to specify proper 'connection_string'.
user, password, classpath and connection_driver fields are not required for ODBC as it is configured in 'connection_string'. Rest all is same.

### The configuration is divided into 3-sections:

#### connector_config
Connector level configurations.

    log_source: Enter the log type.

#### database_config
Database query and connection related configurations.

    query: Enter SQL query here.
    eg: select * from TABLE_NAME where {field_name} > {initial_value} limit FETCH_LIMIT
    Change TABLE_NAME and FETCH_LIMIT in query. Specify 'field_name' and 'initial_value' in below config fields.
    
    field_name: Specify table column name. This will be used to maintain bookmarking of logs fetched till now.
    initial_value: Specify initial value for the above column specified to start fetching log from this value.
    connection_mode: Specify odbc or jdbc.
    connection_string: Enter proper ODBC/JDBC connection string to the database.
    classpath: Specify the JDBC driver path. Not required for ODBC.
    connection_driver: Specify the JDBC driver name. Not required for ODBC.
    user: Enter database username. Not required for ODBC.
    password: Enter correct password. Not required for ODBC.

#### forwarding_config:
Forwarding configurations.

    dst_ip: Enter DNIF Core IP here.
    dst_port: Enter port of listener.
    transfer_type: Specify udp or tcp.

## Execution

Run rdbms_connector.py file and pass configuration file as argument to it.
#### Example:

    python3 RDBMS-Log-Shipper/rdbms_connector.py RDBMS-Log-Shipper/config/someconfigfile.yml
    
Check logs in RDBMS-Log-Shipper/log/ directory.