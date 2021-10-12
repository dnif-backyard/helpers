## Overview

RDBMS stands for Relational Database Management System. RDBMS is the basis for SQL, and for all modern database systems like MS SQL Server, IBM DB2, Oracle, MySQL, and Microsoft Access.

The RDBMS connector fetches the logs from the Database server and forwards to DNIF Core using UDP or TCP client.

## Configuration

Go inside the RDBMS-Log-Shipper/ directory. Create configuration file inside config/ directory or any desired location.

Below is the sample configuration format using JDBC.

    connector_config:
     log_source: ""
    database_config:
     query: "select * from TABLE_NAME where {field_name} > {initial_value} limit FETCH_LIMIT"
     field_name: somefield
     initial_value: 0
     classpath: ""
     connection_driver: ""
     connection_string: ""
     connection_mode: jdbc
     user: “”
     password: “”
    forwarding_config:
     dst_ip: “”
     dst_port: “”
     transfer_type: udp

### The configuration is divided into 3-sections:

#### connector_config
Connector level configurations.

    log_source: Enter the log type.

#### database_config
Database query and connection related configurations.

    query: Enter SQL query here.
    eg: select * from TABLE_NAME where {field_name} > {initial_value} limit FETCH_LIMIT
    Change TABLE_NAME and FETCH_LIMIT in query. Specify field_name and initial_value in below config fields.
    
    field_name: Specify table column name.
    initial_value: Specify the initial value for the above column specified.
    classpath: Specify the JDBC driver path.
    connection_driver: Specify the JDBC driver name.
    connection_string: Enter proper connection string for JDBC connection.
    connection_mode: Specify JDBC here.
    user: Enter database username.
    password: Enter correct password.

#### forwarding_config:
Forwarding configurations.

    dst_ip: Enter DNIF Core IP here.
    dst_port: Enter port of listener.
    transfer_type: Specify udp or tcp.

## Execution

Run rdbms_connector.py file and pass configuration file as argument to it. 
#### Example:

    python3 RDBMS-Log-Shipper/rdbms_connector.py config/someconfigfile.yml
    
Check logs in RDBMS-Log-Shipper/log/