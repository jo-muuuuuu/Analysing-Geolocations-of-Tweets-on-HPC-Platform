# COMP90024 Assignment 1 - Social Media Analytics

## Introduction
The objective of this project is to deploy and execute an application in parallel to the University
of Melbourne HPC facility, SPARTAN, for the analysis of metrics associated with tweets and
their geolocations. The project will begin by establishing a baseline through the execution of
the application on 1 node and 1 core and subsequently utilize MPI to parallelize the application
and execute it on multiple cores. This report will provide an overview of ambiguous locations
found by the application and detail the implementation of the parallelization logic in codes
using the MPI for Python (mpi4py) package. Furthermore, the report will briefly discuss how
the application can be invoked and analyze the results obtained from different configuration
setups.

## Team 
| Name       	| Student ID 	| Email                          	|
|------------	|------------	|--------------------------------	|
| Zeyang Xue  | 1396314   	| zexue@student.unimelb.edu.au 	|
| Zicheng Mu 	| 1261665    	| zmu1@student.unimelb.edu.au    	|

## HPC System - [Spartan](https://dashboard.hpc.unimelb.edu.au/)

*High Performance Computing (HPC)* provides capacity to run a large number of computing tasks simultaneously and to run large-scale parallel tasks, therefore such systems are widely used for various research purposes.

In this reseach, we used *Spartan*, which is the HPC system owned by The University of Melbourne. It operates on the *Linux* operating system, which scales efficiently and effectively. And it run with a command-line interface with application use in batch mode due to latency and performance reasons. 

On the *Spartan* HPC system, the *Slurm Workload Manager* will track the resources available on a system and determine when jobs can run on compute nodes. And the script below is a sample of the Slurm job submission script.

![sample-script](https://github.com/jo-muuuuuu/Twitter-Analysis-on-HPC-Platform/assets/142861960/9e67e3fd-beaa-466b-bb54-407bfd396b25)


## Parallel Computing & [MPI4PY](https://mpi4py.readthedocs.io/en/stable/)
*Parallel computing* involves the steps of breaking large computations into smaller ones, and perform those smaller computations simultaneously. And the *Message Passing Interface (MPI)* is a standardized and portable message-passing system designed for parallel computers that are carrying out the same computation problem to communicate.

In this assignment, we utilized *Python* and the library *MPI4PY*, which provides Python bindings for the MPI standard, to carry out the analysis. Pseudo-code below illustrates our parallelization algorithm.
![pseudo-code](https://github.com/jo-muuuuuu/Twitter-Analysis-on-HPC-Platform/assets/142861960/f721bbe7-bbbc-4475-a510-aca33c6b896e)


## Dataset
The datasets used in this assignment were obtained from Twitter (with official permission) and contain information that can be utilized for various research purposes.

The image below displays the JSON structure of a tweet, with some less important fields omitted for clarity.
![tweet-JSON-structure](https://github.com/jo-muuuuuu/Twitter-Analysis-on-HPC-Platform/assets/142861960/b2535802-1150-47d8-bfc8-e7d37de74846)

## Output
Image below is the output of the 1-Node-1-Core scenario, and it was adjusted from the original layout for better display.
![sample-output](https://github.com/jo-muuuuuu/Twitter-Analysis-on-HPC-Platform/assets/142861960/62c7e0dc-658e-4f92-a911-9d94e531affd)

## Lessons Learned
We are proud of our algorithm of identifying ambiguous locations (which is not the key area of the analysis though), however, we did made some mistakes.

  * Excessive Wall Time: We set a tad longer wall time to guarantee the program will not be killed during run-time. But we did not adjust it properly, resulting the job submitted stayed in the queue longer than it actually needed.

  * No Module Purge Before Module Loading

  * Unsatisfied Performance: The usage of *ijson* made the program pretty unefficient. And our approach could also be optimized, although the specification stated the performance was not the key of this assignment.
