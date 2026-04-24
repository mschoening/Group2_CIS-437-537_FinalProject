<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>CIS 437/537</th>
</tr>
<tr class="odd">
<th>Final Project Report</th>
</tr>
<tr class="header">
<th></th>
</tr>
<tr class="odd">
<th><p>Matthew Schoening, Zach Warsaw</p>
<p>4-24-2026</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# Introduction

This report presents our attempt to replicate the findings of \"Network Load Balancing with In-network Reordering Support for RDMA\" by Cha Hwan Song, Xin Zhe Khooi, Raj Joshi, Inho Choi, Jialin Li, and Mun Choon Chan, published at ACM SIGCOMM 2023.

Remote Direct Memory Access (RDMA) is a high-performance networking technology that enables direct memory transfers between machines without involving the CPU, significantly reducing latency in data center environments. However, RDMA poses a fundamental challenge to traditional load balancing algorithms such as Equal-Cost Multi-Path (ECMP), because RDMA performs packet pacing per connection, producing a near-continuous packet stream with very small inter-packet gaps. Traditional flowlet-based load balancing algorithms rely on these gaps to detect the boundaries of independent flows and reroute traffic accordingly. When those gaps are absent---as with RDMA---these algorithms cannot effectively redistribute load, leading to congestion and performance degradation.

The paper\'s primary contribution is ConWeave, a novel in-network load balancing algorithm designed specifically to handle RDMA workloads. ConWeave improves upon legacy approaches by monitoring per-flow round-trip time (RTT) spikes and proactively rerouting flows when congestion is detected---something ECMP is fundamentally unable to do. The authors\' evaluation demonstrates that ConWeave reduces Flow Completion Time (FCT) slowdown by 21.4% to 57.8% relative to ECMP across a variety of RDMA traffic loads and flow sizes.

# Replication Target: FCT Slowdown Results for Lossless and IRN RDMA Simulations at Varying Network Loads

![preview](Results/Used_In_readme/Original_Paper/All_Combined.png)

The authors found the following results from their simulations:  
**Lossless RDMA** - ConWeave achieves at least 23.3% avg and 45.8% p99 FCT improvement over baselines at 50% load

**IRN RDMA** - ConWeave achieves at least 42.3% avg and 66.8% p99 FCT improvement at 80% load

We chose to replicate these results as they show that conweave demonstrates a measurable improvement over other algorithms in reducing FCT slowdown. They provide a good baseline measurement that we could realistically try to replicate during our experiments. Additionally, while there were other figures in the original paper that we could have tried replicating, none of them had any solid documentation on how the authors came up with those figures so the above figures ended up being the most straightforward to replicate. The original paper also split their testing into hardware and software sections but our group chose to only attempt to replicate part of the software testing as we did not have access to the hardware the original authors used.

# Original Paper Methodology

The original paper measured all their results in a metric they call Flow Completion Time Slow-Down or FCT Slow-down. Breaking this down, Flow Completion Time (FCT) is the amount of time it takes to complete a flow and is measured using queue completion events that are tracked within the virtualized testing environment. Elaborating further, FCT Slow-Down is explained as the time it takes to complete a flow through various network loads (ex.: 50%, 80%, ect.), normalized by the time it would take to complete the same flow when the network has no other traffic. For their testing, the original authors conducted tests to measure the average and the 99-percentile (p99) or the worst 1% of the flow completion times.

The authors ran their simulations inside a virtualized leaf-spine network topology consisting of 8 leaf switches, 8 spine switches, and 16 hosts per leaf switch, giving a total of 128 end hosts. All links ran at 100 Gbps with a 1 microsecond propagation delay. Traffic was generated using a Web Search distribution and injected at two different network load levels: 50% and 80%. Each simulation run lasted 0.1 seconds of simulated time.

They tested under two different RDMA transport configurations: Lossless RDMA, which uses Priority Flow Control (PFC) to prevent packet drops, and IRN RDMA, which handles packet reordering in-network without relying on PFC. Across both configurations, they compared four load balancing algorithms: ECMP, Conga, LetFlow, and their proposed ConWeave algorithm.

Results were broken out by flow size --- short flows (less than 1 Bandwidth-Delay Product, or BDP) and long flows (greater than or equal to 1 BDP) --- and reported as both average and p99 FCT slow-down. Running all combinations (2 load levels × 2 RDMA modes × 4 algorithms × 2 flow sizes) produced a comprehensive picture of how each algorithm performs under realistic data center conditions.

# Our Methodology

For the most part, our methodology was very similar to the original papers in terms of the experimentation process. We tested using the same dataset and traffic generation programs and followed the directions gave as best as we could.  
  
In terms of data tested, we did end up differing in the amount of tests we ran. While the original paper only tested at 50% and 80% network loads, we decided to test on additional loads ranging from 10% to 100% to see how ConWeave behaved across the spectrum. We also decided to test with additional traffic generation times outside of the 0.1 seconds of traffic generation used in the original paper. The goal here was similar to the additional network loads as we wanted to see if the algorithm would perform similarly under these different conditions. Another part where we differed is throughout all of our tests, we excluded the tests on Conga and Drill as those were too computationally intense for us to run in our virtual environment on our hardware.  
  
We ended up running two distinct groups of tests. The first group was where we tried to replicate the paper as closely as possible. We followed the steps provided in the original github repository and tested all the network load and traffic generation combinations mentioned above, including the original tests. Like the original paper we tried to let all the simulations complete before gathering data. This meant letting the simulations run overnight if needed. For this group, the extensive data analysis was only done on the tests the original paper did due to time constraints before the presentation. The tests conducted using the additional parameters only have graphs made for them for this reason.  
  
The second group we tested was done in an effort to get more consistency than the first group. In this new group we decided to limit the simulations to 2 hours of run time in total. Everything else was conducted in the same way as the first group of tests. We did this in response to some of the simulations crashing before they would complete, with the idea being that having the simulation cut off at 2 hours would make all the tests equal in the amount of time that they were run. While this means that all of our results for this test group are incomplete, they are consistently incomplete and do not have data from complete simulations mixed with incomplete simulations like the previous group did. We were hoping that this would result in more predictable results as each simulation would have the same amount of time to run before collecting the data.

In both groups we used a simple percent error analysis on the data gathered in order to determine the percent improvement ConWeave has in reducing FCT Slowdowns over the other algorithms tested. These are the same calculations done by the original authors and it's a good statistical analysis for the data we are trying to show.

**Directions to running the simulations**

1.  In the terminal CD into the working directory:
``` shell
 cd ns-allinone-3.19
 cd ns-3.19
 ```
2.  Edit any of the autorun scripts stored in `/working_folder/ns-allinone-3.19/ns-3.19` to set the network traffic and the traffic generation time. you can do this by changing the "NETLOAD" and "RUNTIME" variables. For example, changing the file so NETLOAD='30' would set the simulation to run at a 30 percent network load. 

3.  Run the autorun script using this command:  
``` shell
./autorun.sh
```
Note: the autorun.sh script can be replaced with any of the autorun scripts located in `/working_folder/ns-allinone-3.19/ns-3.19` this includes: autorun.sh, Timed_Autorun.sh, and autorun_final.sh

4.  The script should start the simulation and run tests on ConWeave, FECMP, and Letflow. The simulations themselves can take anywhere from a few hours to over night to complete in our experience and can sometimes crash. 

5.  When you want to collect the data, run any one of the various analysis scripts like so: 
``` shell
python3 ./analysis/plot_fct.py
```
The scripts are located in `./working_folder/ns-allinone-3.19/ns-3.19/analysis`. All of these are just various modifications of the plot_fct.py script found in the original github repository. The data generated from running these is stored in the figures folder found where the scripts are stored.  They output PDF graphs and some of the scripts output additional images and CSVs to make it easier to gather the relevant data. The exact modifications to all of them are explained at the bottom of this readme under the contributions section and in another file in the /analysis folder. 

6. Once all the data is gathered, you can clean up all the data from the simulaton using this command:
``` shell
./cleanup.sh
```
Note: this does not clean up all the output graphs and images generated by some of the analysis scripts as this script was unchanged from the original repository. Manual removal of these extra CSVs and images will be required if you wish to completely remove every piece of data generated.  

7. After cleaning up the results, you can restart the process from step 2 to test other combinations of network loads and traffic generation times. 

# Test Group 1 Results:


**Replication of paper results**

Comparison to the figures shown in the original paper. Originals shown on the left, our results shown on the right.


**Average FCT Slowdown, 50% Average Load Using Lossless RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/Avg_50Pct_Lossless.png" width="400">
  <img src="Results/Used_In_readme/Group1_Data/Avg_50_Lossless.png" width="400">
</div>


**P99 FCT Slowdown, 50% Average Load Using Lossless RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/P99_50Pct_Lossless.png" width="400">
  <img src="Results/Used_In_readme/Group1_Data/P99_50_Lossless.png" width="400">
</div>


**Average FCT Slowdown, 80% Average Load Using Lossless RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/Avg_80Pct_Lossless.png" width="400">
  <img src="Results/Used_In_readme/Group1_Data/Avg_80_Lossless.png" width="400">
</div>


**P99 FCT Slowdown, 80% Average Load Using Lossless RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/P99_80Pct_Lossless.png" width="400">
  <img src="Results/Used_In_readme/Group1_Data/P99_80_Lossless.png" width="400">
</div>


**Average FCT Slowdown, 50% Average Load Using IRN RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/Avg_50Pct_IRN.png" width="400">
  <img src="Results/Used_In_readme/Group1_Data/Avg_50_IRN.png" width="400">
</div>


**P99 FCT Slowdown, 50% Average Load Using IRN RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/P99_50Pct_IRN.png" width="400">
  <img src="Results/Used_In_readme/Group1_Data/P99_50_IRN.png" width="400">
</div>


**Average FCT Slowdown, 80% Average Load Using IRN RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/Avg_80Pct_IRN.png" width="400">
  <img src="Results/Used_In_readme/Group1_Data/Avg_80_IRN.png" width="400">
</div>


**P99 FCT Slowdown, 80% Average Load Using IRN RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/P99_80Pct_IRN.png" width="400">
  <img src="Results/Used_In_readme/Group1_Data/P99_80_IRN.png" width="400">
</div>

# Analysis

**50% Network Load, Lossless RDMA**
<div style="display:flex; justify-content:center;">
  <img src="Results/Used_In_readme/Group1_Analysis/50_Lossless.png" width="1000">
</div>

For 50% network load using lossless RDMA, our group saw a Minimum 21% improvement in Avg FCT Slowdowns and 85% for P99 FCT Slowdowns. This is compared to the original paper minimums of 23.3% and 45.8% respectively.

**80% Network Load, Lossless RDMA**
<div style="display:flex; justify-content:center;">
  <img src="Results/Used_In_readme/Group1_Analysis/80_Lossless.png" width="1000">
</div>

For 80% network load using lossless RDMA, our group saw a Minimum 83% improvement in Avg FCT Slowdowns and 159% for P99 FCT Slowdowns. This is compared to the original paper minimums of 17.6% and 35.8% respectively.

**50% Network Load, IRN RDMA**
<div style="display:flex; justify-content:center;">
  <img src="Results/Used_In_readme/Group1_Analysis/50_IRN.png" width="1000">
</div>

For 50% network load using IRN RDMA, our group saw a Minimum 8% improvement in Avg FCT Slowdowns and 45% for P99 FCT Slowdowns. This is compared to the original paper minimums of 12.7% and 46.2% respectively.

**80% Network Load, IRN RDMA**
<div style="display:flex; justify-content:center;">
  <img src="Results/Used_In_readme/Group1_Analysis/80_IRN.png" width="1000">
</div>

For 80% network load using IRN RDMA, our group saw a Minimum 46% improvement in Avg FCT Slowdowns and 134% for P99 FCT Slowdowns. This is compared to the original paper minimums of 42.3% and 66.8% respectively.

**Additional results from outside the original tests:**

The following are an assortment of results tested at different network loads under 0.02, 0.1, and 0.5 seconds of traffic generation time. While these aren\'t all the results we tested, they show that ConWeave is generally better than the other algorithms tested. Additional results can be found here (include path to results here)

![preview](Results/Used_In_readme/Misc/Additional_Group1.png)

# Test Group 2 Results

Comparison to the figures shown in the original paper. Originals shown on the left, our results shown on the right.


### **Average FCT Slowdown, 50% Average Load Using Lossless RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/Avg_50Pct_Lossless.png" width="400">
  <img src="Results/Used_In_readme/50/AVG_TOPO_leaf_spine_128_100G_OS2_LOAD_50_FC_Lossless.png" width="400">
</div>




**P99 FCT Slowdown, 50% Average Load Using Lossless RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/P99_50Pct_Lossless.png" width="400">
  <img src="Results/Used_In_readme/50/P99_TOPO_leaf_spine_128_100G_OS2_LOAD_50_FC_Lossless.png" width="400">
</div>


**Average FCT Slowdown, 80% Average Load Using Lossless RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/Avg_80Pct_Lossless.png" width="400">
  <img src="Results/Used_In_readme/80/AVG_TOPO_leaf_spine_128_100G_OS2_LOAD_80_FC_Lossless.png" width="400">
</div>


**P99 FCT Slowdown, 80% Average Load Using Lossless RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/P99_80Pct_Lossless.png" width="400">
  <img src="Results/Used_In_readme/80/P99_TOPO_leaf_spine_128_100G_OS2_LOAD_80_FC_Lossless.png" width="400">
</div>


**Average FCT Slowdown, 50% Average Load Using IRN RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/Avg_50Pct_IRN.png" width="400">
  <img src="Results/Used_In_readme/50/AVG_TOPO_leaf_spine_128_100G_OS2_LOAD_50_FC_IRN.png" width="400">
</div>


**P99 FCT Slowdown, 50% Average Load Using IRN RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/P99_50Pct_IRN.png" width="400">
  <img src="Results/Used_In_readme/50/P99_TOPO_leaf_spine_128_100G_OS2_LOAD_50_FC_IRN.png" width="400">
</div>


**Average FCT Slowdown, 80% Average Load Using IRN RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/Avg_80Pct_IRN.png" width="400">
  <img src="Results/Used_In_readme/80/AVG_TOPO_leaf_spine_128_100G_OS2_LOAD_80_FC_IRN.png" width="400">
</div>


**P99 FCT Slowdown, 80% Average Load Using IRN RDMA**
<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Original_Paper/P99_80Pct_IRN.png" width="400">
  <img src="Results/Used_In_readme/80/P99_TOPO_leaf_spine_128_100G_OS2_LOAD_80_FC_IRN.png" width="400">
</div>


# Analysis  
***Here is the percent error analysis we conducted on the second group of test data. More results for additional data outside of the original paper tests can be found in the Results folder and in the TestGroup2_Pct_Error spreadsheet we used to calculate them located here:*** Results\Pct_Error_Spreadsheets\TestGroup2_Pct_Error.xlsx

**50% Network Load, Lossless RDMA**

<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Group2_Analysis/Avg_50_Lossless.png" width="400">
  <img src="Results/Used_In_readme/Group2_Analysis/P99_50_Lossless.png" width="400">
</div>

For the second group of tests at 50% network load using lossless RDMA, our group saw a Minimum 21% improvement in Avg FCT Slowdowns and 84% for P99 FCT Slowdowns. This is compared to the original paper minimums of 23.3% and 45.8% respectively.

**80% Network Load, Lossless RDMA**

<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Group2_Analysis/Avg_80_Lossless.png" width="400">
  <img src="Results/Used_In_readme/Group2_Analysis/P99_80_Lossless.png" width="400">
</div>

For the second group of tests at 80% network load using lossless RDMA, our group saw a Minimum 116% improvement in Avg FCT Slowdowns and 248% for P99 FCT Slowdowns. This is compared to the original paper minimums of 17.6% and 35.8% respectively.

**50% Network Load, IRN RDMA**

<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Group2_Analysis/Avg_50_IRN.png" width="400">
  <img src="Results/Used_In_readme/Group2_Analysis/P99_50_IRN.png" width="400">
</div>

For the second group of tests at 50% network load using IRN RDMA, our group saw a Minimum 7% improvement in Avg FCT Slowdowns and 43% for P99 FCT Slowdowns. This is compared to the original paper minimums of 12.7% and 46.2% respectively.

**80% Network Load, IRN RDMA**

<div style="display:flex; justify-content:center; gap:20px;">
  <img src="Results/Used_In_readme/Group2_Analysis/Avg_80_IRN.png" width="400">
  <img src="Results/Used_In_readme/Group2_Analysis/P99_80_IRN.png" width="400">
</div>

For the second group of tests at 80% network load using IRN RDMA, our group saw a Minimum 50% improvement in Avg FCT Slowdowns and 136% for P99 FCT Slowdowns. This is compared to the original paper minimums of 42.3% and 66.8% respectively.

# Comparison to Test group 1

![preview](Results/Used_In_readme/Tables/Comparison_Group1_Group2.png)

When compared to the first group of tests in the table seen above, the percent error analysis does not seem to differ too much from our original results. All the results highlighted in green cells are the ones that were similar to the original paper. Those results are similar across the board between Group 1 and Group 2. In contrast to this, the results where our data differed from the original paper had more variation between the two groups. Here, the highest minimum difference between the two groups was seen in the P99 80% network load test where the minimum of Group 2 was 89 percentage points higher than it was in Group 1 when testing Lossless RDMA.

# Traffic Generation Time Comparisons

The results are similar when comparing different traffic generation times too. With all the results that mirrored the original paper being roughly similar to one another. The same situation is seen here where the only data that varied a lot was seen in the results that never matched the original paper.

![preview](Results/Used_In_readme/Tables/Gen_Time_Compairson.png)

# Additional results from outside the original tests

Like the first group of tests, we also conducted additional simulations on network loads from 10% all the way to 100% with traffic generation times of 0.1 and 0.5 seconds. This is just a couple of the results but they show the same similar pattern to the original tests where ConWeave generally performs better than the other algorithms tested. More results can be found in the Results folder.

![preview](Results/Used_In_readme/Misc/Additional_Group2.png)

# Conclusion

Our results from the two different test groups show that ConWeave did provide a general improvement in FCT Slowdown reductions over FECMP and Letflow. For the 1:1 tests to the original papers, the overall average performance increase was 105.6% for Group 1 and 119% for Group 2. Group 1 also saw a minimum of 8% and a maximum of 270% increase in FCT Slowdown reductions while Group 2 saw a minimum of 7% and a maximum of 347%.

When tested at 0.5 seconds of traffic generation, our tests showed an overall average improvement of 102%, with a minimum 7% and a maximum 234% improvement over the other algorithms tested.

Unfortunately, through all the tests we conducted we were unable to completely match the results seen in the paper. In the original testing we did, we only matched half of the eight different tests shown in the paper. These results were mirrored by the 2nd group of tests and when testing different traffic generation times as well. In all of these, the sections that did not match were identical but varied in how much they were different from the original paper. Where the results mirrored the original paper, the data was only a handful of percentage points off from the original figures in all the different tests.

Our original hypothesis behind why our data did not match the authors was that incomplete data from the simulations was causing some of our tests to be way off. We thought that our inability to completely run some of the simulations without crashing was the culprit and decided to put a time limit on how long each simulation ran for the 2nd group of tests. This change ultimately did not seem to change anything as the tests that did not match were not any closer to the original tests. Additionally the tests that matched were the same in the 2nd group, disproving our hypothesis as none of the simulations were allowed to complete before collecting the data.

With incomplete data ruled out, that leaves a few other possible factors that we could not come up with a way to test for. We noted earlier that we decided to exclude Conga and Drill from testing as we did not have the computational power available to test them effectively. Since the minimums in the paper are from all tested algorithms, it is possible that the minimums that didn\'t match were from those two algorithms we chose to exclude. Another possibility could be differences in the simulation environment. The original paper stated that each simulation should only take a few hours to complete. On our setups, when we were running the simulations, we faced constant crashes or simulations that were taking over 8 hours to complete. We think this stark difference in completion time could be attributed to some kind of difference between what the original authors had and what we were testing on. That could be anything from differences in the actual hardware it is running on to differences in how the virtual environment was set up to run the simulations.

# Lessons Learned

Several practical lessons emerged from this replication effort that may be useful to others attempting to reproduce this paper:

> • Docker environment is essential: The authors\' Docker image is the only practical way to build the ns-3 simulator with the custom ConWeave patches. Attempting to build natively on Ubuntu 22.04 or later will encounter dependency conflicts with the older ns-3 version used.
>
> • Start with short simulation times: The TIME parameter in autorun.sh has a significant impact on runtime. Starting with 0.02s--0.05s allows you to verify the pipeline is working before committing to full-length runs.
>
> • FCT output files can be large: Full runs at 80% load produce several GB of FCT output data. Ensure sufficient disk space before running.
>
> • The plot_fct.py script requires specific Python dependencies (numpy, matplotlib) that are not pre-installed in the Docker image and must be added manually.
>
> • IRN RDMA runs generally complete faster than Lossless RDMA runs because IRN avoids PFC pause frames that can create complex simulation states.
>
> • The paper\'s Figures 12 and 13 represent the 80% and 50% load cases respectively --- this ordering is not immediately obvious from the repository structure and can cause confusion when comparing outputs.

# Contributions
List of files we modified or added to the original work in order to reproduce the results. 

* Within the [ns-3.19 folder](working_folder\ns-allinone-3.19\ns-3.19): 
> [autorun.sh](working_folder\ns-allinone-3.19\ns-3.19\autorun.sh) : This is a mostly stock version of the original autorun script included in the original repository. The only modifications made to it was to remove the sections that enabled testing with Conga. 

>[Timed_autorun.sh](working_folder\ns-allinone-3.19\ns-3.19\Timed_Autorun.sh): This is another modification from the original autorun script that stops all the simulations after 2 hours. This was made to facilitate the group 2 testing we did. 

>[autorun_final.sh](working_folder\ns-allinone-3.19\ns-3.19\autorun_final.sh): This was another script that was made with the idea to allow us to see when each simulation gets completed as the original does not support this. This was made early on in the process and it removes the ability to run all the simulations in parallel. It runs each simulation individually and lets the user know once each one has completed. This was only used for a few of our data points as it greatly increases the time to complete all the simulations. Only generates a graph in PDF form. 

* Within the [analysis folder](working_folder\ns-allinone-3.19\ns-3.19\analysis):

>[plot_fct.py](working_folder\ns-allinone-3.19\ns-3.19\analysis\plot_fct.py): This is mostly an unchanged version of the script found in the original repository. Only changes made to this was the removal of Conga and Drill from the graph. This was only used briefly when we started and it generates graphs in PDF form. 

>[plot.py](working_folder\ns-allinone-3.19\ns-3.19\analysis\plot.py): This is the same as the previous plot_fct.py but with changes to fix the x axis in order to make the graphs look similar to the graphs found in the original paper. The axis is fixed to 1.8k, 3.5k, 4.6k, 5.5k, 6.3k, 7.2k, 8.6k, 16k, 21k, and 2.0M bytes in order to match the original graphs. This was mainly used for all the additional data we gathered in the first group of tests. Only generates graphs in PDF form. 

>[pTable.py](working_folder\ns-allinone-3.19\ns-3.19\analysis\pTable.py): This is a modificatinon of the previous scripts but adds an additional table with numbers on each of the measured flow sizes. This was used in the first group of tests to gather more detailed data when trying to replicate the original results from the paper. Only generates a pdf containing a graph and a table with detailed numbers. 

>[NpTable.py](working_folder\ns-allinone-3.19\ns-3.19\analysis\NpTable.py): This is a further modification of the pTable.py script and it was made to facilitate easier data gathering while conducting the group 2 tests. The changes made to it allow it to export the generated table to CSV format while additionally generating an image that matches the PDF file for ease of use in reports. Running this script once generates a total of 12 different PDF, CSV, and PNG files of the various graphs and tables.  

* Within the [Results folder](Results) - Notable files/folders include:

>[80pct_50pct_Load_WithTables_First_Data_Run folder](Results\80pct_50pct_Load_WithTables_First_Data_Run): This includes all of the generated PDFs for the first group of tests on the original figures found in the paper. They include tests at 50 percent and 80 percent traffic load at 0.1 seconds of traffic generation. 

>[Group1_Additional_Data Folder](Results\Group1_Additional_Data): This is the additional data gathered for the first group of tests. It has tests from 10 percent to 100 percent network load and is divided into traffic generation times of 0.1 seconds and 0.5 seconds. Only PDF graphs are included here as we did not have time to do the extra analysis on all of these. 

>[Group2_All_Data](Results\Group2_All_Data): This is all the data for the testing done for group 2. It contains every test from 10 percent to 100 percent network load and is split up into groups by the two traffic generation times we tested. It contains over 200 files of varying types such as PDFs, CSVs, and PNGs.  

>[Used_In_readme](Results\Used_In_readme): This just contains images of the results we used in this readme sorted for easy reference. 

>[TestGroup1_Pct_Error spreadsheet](Results\Pct_Error_Spreadsheets\TestGroup1_Pct_Error.xlsx) : The spreadsheet used to calculate the percent error analysis on the original figures our group was trying to replicate. This is testing from the first group so it only includes the data from the 50 percent and 80 percent tests at 0.1 seconds of traffic generation. 

>[TestGroup2_Pct_Error spreadsheet](Results\Pct_Error_Spreadsheets\TestGroup2_Pct_Error.xlsx): The spreadsheet used to conduct the percent error analysis for group 2 of testing. It includes caluclations for the original figures as well as the additional figures generated from 10 percent to 100 percent network loads and split up by traffic generation times of 0.1 seconds and 0.5 seconds. 

>[old_data folder](Results\old_data): Folder containing any old data that was generated before the first test group. None of this data is used in any of the analysis sections. 