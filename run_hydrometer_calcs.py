#import neccesary packages and modules
from sed_size_analysis_functions import hydrometer_calcs

directory = "C:/Users/josie/Downloads/sed_size_analysis_example"
data_file_name = "sedsizedata_sample_taylor.csv"


hc = hydrometer_calcs(path_to_data= directory + "/" + data_file_name, 
                    path_to_config= directory + "/config_files/params.csv", 
                    path_to_colnames= directory + "/config_files/colnames.csv", 
                    path_to_calcset= directory + "/config_files/calcset.csv")

results = hc.calc_percent_size()

print(results)

# Save output
results.to_csv(directory + "/output.csv", index=False)
