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

## Spartan

## Parallel Computing - MPI4PY

## Team 
| Name       	| Student ID 	| Email                          	|
|------------	|------------	|--------------------------------	|
| Zeyang Xue  | 1396314   	| zexue@student.unimelb.edu.au 	|
| Zicheng Mu 	| 1261665    	| zmu1@student.unimelb.edu.au    	|

## Dataset
The datasets used in this assignment were obtained from Twitter (with official permission) and contain information that can be utilized for various research purposes.

The image below displays the JSON structure of a tweet, with some less important fields omitted for clarity.
![tweet-JSON-structure](https://github.com/jo-muuuuuu/Twitter-Analysis-on-HPC-Platform/assets/142861960/b2535802-1150-47d8-bfc8-e7d37de74846)

## Output
