The folder ns-allinone-3.19 is the working folder we used to run all the simulations. It is a copy of the original github the authors created with some modifications to better suit our needs. 

**Files we changed or added to this folder include:**

* Within the [ns-3.19 folder](\ns-allinone-3.19\ns-3.19): 
> [autorun.sh](\ns-allinone-3.19\ns-3.19\autorun.sh) : This is a mostly stock version of the original autorun script included in the original repository. The only modifications made to it was to remove the sections that enabled testing with Conga. 

>[Timed_autorun.sh](\ns-allinone-3.19\ns-3.19\Timed_Autorun.sh): This is another modification from the original autorun script that stops all the simulations after 2 hours. This was made to facilitate the group 2 testing we did. 

>[autorun_final.sh](\ns-allinone-3.19\ns-3.19\autorun_final.sh): This was another script that was made with the idea to allow us to see when each simulation gets completed as the original does not support this. This was made early on in the process and it removes the ability to run all the simulations in parallel. It runs each simulation individually and lets the user know once each one has completed. This was only used for a few of our data points as it greatly increases the time to complete all the simulations. Only generates a graph in PDF form. 

* Within the [analysis folder](\ns-allinone-3.19\ns-3.19\analysis):

>[plot_fct.py](\ns-allinone-3.19\ns-3.19\analysis\plot_fct.py): This is mostly an unchanged version of the script found in the original repository. Only changes made to this was the removal of Conga and Drill from the graph. This was only used briefly when we started and it generates graphs in PDF form. 

>[plot.py](\ns-allinone-3.19\ns-3.19\analysis\plot.py): This is the same as the previous plot_fct.py but with changes to fix the x axis in order to make the graphs look similar to the graphs found in the original paper. The axis is fixed to 1.8k, 3.5k, 4.6k, 5.5k, 6.3k, 7.2k, 8.6k, 16k, 21k, and 2.0M bytes in order to match the original graphs. This was mainly used for all the additional data we gathered in the first group of tests. Only generates graphs in PDF form. 

>[pTable.py](\ns-allinone-3.19\ns-3.19\analysis\pTable.py): This is a modificatinon of the previous scripts but adds an additional table with numbers on each of the measured flow sizes. This was used in the first group of tests to gather more detailed data when trying to replicate the original results from the paper. Only generates a pdf containing a graph and a table with detailed numbers. 

>[NpTable.py](\ns-allinone-3.19\ns-3.19\analysis\NpTable.py): This is a further modification of the pTable.py script and it was made to facilitate easier data gathering while conducting the group 2 tests. The changes made to it allow it to export the generated table to CSV format while additionally generating an image that matches the PDF file for ease of use in reports. Running this script once generates a total of 12 different PDF, CSV, and PNG files of the various graphs and tables.