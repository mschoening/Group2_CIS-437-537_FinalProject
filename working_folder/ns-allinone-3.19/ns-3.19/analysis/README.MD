This folder contains all of the scripts used to generate data from the simulations. All of the scripts here output their results to the figures folder.

**Files our group added/edited include:**

>[plot_fct.py](plot_fct.py): This is mostly an unchanged version of the script found in the original repository. Only changes made to this was the removal of Conga and Drill from the graph. This was only used briefly when we started and it generates graphs in PDF form. 

>[plot.py](plot.py): This is the same as the previous plot_fct.py but with changes to fix the x axis in order to make the graphs look similar to the graphs found in the original paper. The axis is fixed to 1.8k, 3.5k, 4.6k, 5.5k, 6.3k, 7.2k, 8.6k, 16k, 21k, and 2.0M bytes in order to match the original graphs. This was mainly used for all the additional data we gathered in the first group of tests. Only generates graphs in PDF form. 

>[pTable.py](pTable.py): This is a modificatinon of the previous scripts but adds an additional table with numbers on each of the measured flow sizes. This was used in the first group of tests to gather more detailed data when trying to replicate the original results from the paper. Only generates a pdf containing a graph and a table with detailed numbers. 

>[NpTable.py](NpTable.py): This is a further modification of the pTable.py script and it was made to facilitate easier data gathering while conducting the group 2 tests. The changes made to it allow it to export the generated table to CSV format while additionally generating an image that matches the PDF file for ease of use in reports. Running this script once generates a total of 12 different PDF, CSV, and PNG files of the various graphs and tables.