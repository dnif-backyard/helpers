...................................................Hardware benchmarking.......................................................

Working with script............................................................................................................

Upload the Systembench..v2.0.tar.xz on /var/tmp folder on your respective machine.

Navigate to the /var/tmp folder using cd command
cd /var/tmp/

Untar the shared file using below command
tar -xf Systembench..v2.0.tar.xz

Navigate to Systembench folder
cd Systembench

Run the script using below command
bash Sysbench.sh

Output and logs will be stored in /DNIF/Benchsystem/

About Sysbench...................................................................................................................
Benchmarks help us in testing and quantification of our hardware infrastructure. Consistently performant hardware infrastructure forms the base of a high performance data structure. A cloud deployment or an on-prem high density virtualisation platform shares its compute and storage across multiple hosts. This typically causes hot and cold patches in performance.

This document discusses standard hardware testing and benchmarking tools that can be used to benchmark hardware before a deployment.

Testing Process..................................................................................................................

When to test, how to ensure consistent performance.

Test and benchmark your hardware before you install, to ensure the underlying hardware fulfils expecations. Initial results must satisfy or exceed the performance benchmarks indicated in scaling datanodes or your custom solution design document.

Repeat tests if you find performance related issues while in operations and compare the results with the initial benchmarking.

Benchmarking......................................................................................................................

This section will cover in detail the tools and the commands used to benchmark hardware.

Testing tool......................................................................................................................

Choosing the right tool that will remain consistent across tests is extremely important, for DNIF we have selected sysbench which has been available and trusted for years. Sysbench is also a part of the standard linux stack so it can be installed using the following command.

CPU Benchmarking...................................................................................................................

The test metric to be measured are

    Total run time in seconds
    Total number of events executed
    CPU events executed

Memory Benchmarking................................................................................................................

The test metric to be measured are

    Operations per second
    Throughput


File IO Benchmarking................................................................................................................

Benchmarking file IO is done in three parts - create a test file for a specific size, conduct your test on the file and finally delete the file to return the used disk space back to operations.
The test metric to be measured are

    Write speed during test prepare
    Read and write operations per second
    Read and write throughput
