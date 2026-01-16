# sed_size_analysis_tools
This repository contains a module for conducting sediment size analysis from csv files in whatever setup you have your data in. The way that it handles different data structures is by using a set of config files, which are described below. For the easiest, most straightforward use of this code, keep the data and config files in the same file structure as the example:

main_folder_for_sed_size_analyis
-->  data.csv
-->  config_files_folder
-------->  colnames.csv
-------->  calcset.csv
-------->  params.csv

Make sure to update the directory path and the data_file_name, while keeping the format of the directory the same. The current code will produce an output.csv file containing the data + processing steps + final outputs. When you want to run this, you will likely need to change the config files to get things to function with your code. Below is an explanation of the different config files and what options you have.

### colnames.csv
This file essentially is the instructions for the code to read your data. There are two columns: "Variable" and "col_name_in_data". The "Variable" column contains the variables that are used in the code **Do not change these values**. The "col_name_in_data" column are the names of the columns in your datasheet (data.csv file). You will likely need to change these to get the code to run properly. Below is a description of each variable:

T30_temp: Air temperature at 30 seconds. [C]
R_30: Uncorrected hydrometer reading at 30 seconds. [g/L]
R_b_30: Uncorrected blank hydrometer reading at 30 seconds. [g/L]

T60_temp: Air temperature at 60 seconds. [C]
R_60: Uncorrected hydrometer reading at 60 seconds. [g/L]
R_b_60: Uncorrected blank hydrometer reading at 60 seconds. [g/L]

T5400_temp: Air temperature at 5400 seconds (90 minutes). [C]
R_5400: Uncorrected hydrometer reading at 5400 seconds (90 minutes). [g/L]
R_b_5400: Uncorrected blank hydrometer reading at 5400 seconds (90 minutes). [g/L]


T86400_temp: Air temperature at 86400 seconds (24 hours). [C]
R_86400: Uncorrected hydrometer reading at 86400 seconds (24 hours). [g/L]
R_b_86400: Uncorrected blank hydrometer reading at 86400 seconds (24 hours). [g/L]

C: Dry mass of soil. [g]

The code is written to handle as many hydrometer readings as you want to add, as long as you give it a temp, hydrometer reading and a blank reading for that time and format the names the same, with time in seconds. However, you need a minimum of 2 readings for the code to run successfully.

Additionally, it is important to note that you can provide the same col_name_in_data for multiple variables. So for example if you only took one temperature reading for both the 30 and 60 second hydrometer readings, you can just provide the same column name in "col_name_in_data". See the T30_temp and T60_temp in the example colnames.csv

### calcset.csv

This file stores the calculation settings that the code use. There are two columns in this file, "Setting" and "Value". Right now, there is only one setting to choose: 

extrapolation: how to handle situations where the either 50um or 2 um falls outside of all of the X values for the times that were measured. There are two options:
                1- "extrapolate": uses the closest two datapoints to extrapolate the P value for either 2um or 50um
                2- "truncate": uses the closest measured value as the P value for either 2um or 50um


### params.csv

This file contains parameters that are static across all experiments that you process. This file should contain:

mu: the dynamic viscosity of the fluid [centiPoise (cP)]
rho_l: the density of the fluid [g/cm**3]
rho_s: the density of the sediment [g/cm**3]
g: acceleration due to gravity [cm/s**2]
L0: hydrometer calibration constant [cm]
k: hydrometer calibration slope [cm/ (gL**-1)]


To run a size fraction calculation from a hydrometer experiment, run the "run_hydrometer_calcs.py" script. 