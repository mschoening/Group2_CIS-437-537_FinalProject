#!/usr/bin/python3

import subprocess
import os
import sys
import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import math
from cycler import cycler

# LB/CC mode matching
cc_modes = {
    1: "dcqcn",
    3: "hp",
    7: "timely",
    8: "dctcp",
}
lb_modes = {
    0: "fecmp",
    2: "drill",
    3: "conga",
    6: "letflow",
    9: "conweave",
}
topo2bdp = {
    "leaf_spine_128_100G_OS2": 104000,
    "fat_k4_100G_OS2": 153000,
}

C = [
    'xkcd:grass green',
    'xkcd:blue',
    'xkcd:purple',
    'xkcd:orange',
    'xkcd:teal',
    'xkcd:brick red',
    'xkcd:black',
    'xkcd:brown',
    'xkcd:grey',
]

LS = ['solid', 'dashed', 'dotted', 'dashdot']
M = ['o', 's', 'x', 'v', 'D']
H = ['//', 'o', '***', 'x', 'xxx']


def setup():
    def lcm(a, b):
        return abs(a * b) // math.gcd(a, b)

    def a(c1, c2):
        l = lcm(len(c1), len(c2))
        c1 = c1 * (l // len(c1))
        c2 = c2 * (l // len(c2))
        return c1 + c2

    def add(*cyclers):
        s = None
        for c in cyclers:
            if s is None:
                s = c
            else:
                s = a(s, c)
        return s

    plt.rc('axes', prop_cycle=(add(cycler(color=C),
                                   cycler(linestyle=LS),
                                   cycler(marker=M))))
    plt.rc('lines', markersize=5)
    plt.rc('legend', handlelength=3, handleheight=1.5, labelspacing=0.25)
    plt.rcParams["font.family"] = "sans"
    plt.rcParams["font.size"] = 10
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42


def getFilePath():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print("File directory: {}".format(dir_path))
    return dir_path


def get_pctl(a, p):
    i = int(len(a) * p)
    return a[i]


def size2str(steps):
    result = []
    for step in steps:
        if step < 10000:
            result.append("{:.1f}K".format(step / 1000))
        elif step < 1000000:
            result.append("{:.0f}K".format(step / 1000))
        else:
            result.append("{:.1f}M".format(step / 1000000))
    return result

# fix x axis to make all the graphs similar to the original paper.
def apply_custom_flow_size_ticks(ax, bucket_sizes, xvals):
    
    desired_sizes = [1800, 3500, 4600, 5500, 6300, 7200, 8600, 16000, 31000, 2_000_000]

    tick_positions = []
    tick_labels = []

    for target in desired_sizes:
        idx = min(range(len(bucket_sizes)),
                  key=lambda i: abs(bucket_sizes[i] - target))
        tick_positions.append(xvals[idx])
        tick_labels.append(size2str([target])[0])

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=10.5, rotation=40)


def get_steps_from_raw(filename, time_start, time_end, step=5):
    cmd_slowdown = (
        "cat %s" % (filename) +
        " | awk '{ if ($6>" + "%d" % time_start +
        " && $6+$7<" + "%d" % (time_end) +
        ") { slow=$7/$8; print slow<1?1:slow, $5} }' | sort -n -k 2"
    )
    output_slowdown = subprocess.check_output(cmd_slowdown, shell=True)
    aa = output_slowdown.decode("utf-8").split('\n')[:-2]
    nn = len(aa)

    res = [[i / 100.] for i in range(0, 100, step)]
    for i in range(0, 100, step):
        l = int(i * nn / 100)
        r = int((i + step) * nn / 100)
        fct_size = aa[l:r]
        fct_size = [[float(x.split(" ")[0]), int(x.split(" ")[1])] for x in fct_size]
        fct = sorted(map(lambda x: x[0], fct_size))

        res[int(i / step)].append(fct_size[-1][1])
        res[int(i / step)].append(sum(fct) / len(fct))
        res[int(i / step)].append(get_pctl(fct, 0.5))
        res[int(i / step)].append(get_pctl(fct, 0.95))
        res[int(i / step)].append(get_pctl(fct, 0.99))
        res[int(i / step)].append(get_pctl(fct, 0.999))

    result = {"avg": [], "p99": [], "size": []}
    for item in res:
        result["avg"].append(item[2])
        result["p99"].append(item[5])
        result["size"].append(item[1])

    return result


def add_table_subplot(ax_table, desired_sizes, results_by_lb, lbmode_order, lb_colors, metric_key):
    # Build table data
    table_data = []
    header = ["Flow Size"] + lbmode_order
    table_data.append(header)

    for size in desired_sizes:
        row = [size2str([size])[0]]
        for lb in lbmode_order:
            bucket_sizes = results_by_lb[lb]["size"]
            vals = results_by_lb[lb][metric_key]

            idx = min(range(len(bucket_sizes)),
                      key=lambda i: abs(bucket_sizes[i] - size))

            row.append(f"{vals[idx]:.3f}")
        table_data.append(row)

    ax_table.axis('off')
    table = ax_table.table(
        cellText=table_data,
        loc='center',
        cellLoc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.3)

    # Color the LB mode columns
    for col_idx, lb in enumerate(lbmode_order, start=1):
        color = lb_colors[lb]
        for row_idx in range(1, len(table_data)):  # skip header row
            cell = table[row_idx, col_idx]
            cell.get_text().set_color(color)


def main():
    parser = argparse.ArgumentParser(description='Plotting FCT of results')
    parser.add_argument('-sT', dest='time_limit_begin', action='store', type=int, default=2005000000)
    parser.add_argument('-fT', dest='time_limit_end', action='store', type=int, default=10000000000)

    args = parser.parse_args()
    time_start = args.time_limit_begin
    time_end = args.time_limit_end
    STEP = 5

    file_dir = getFilePath()
    fig_dir = file_dir + "/figures"
    output_dir = file_dir + "/../mix/output"
    history_filename = file_dir + "/../mix/.history"

    map_key_to_id = dict()

    with open(history_filename, "r") as f:
        for line in f.readlines():
            for topo in topo2bdp.keys():
                if topo in line:
                    parsed_line = line.replace("\n", "").split(',')
                    config_id = parsed_line[1]
                    cc_mode = cc_modes[int(parsed_line[2])]
                    lb_mode = lb_modes[int(parsed_line[3])]
                    encoded_fc = (int(parsed_line[9]), int(parsed_line[10]))
                    if encoded_fc == (0, 1):
                        flow_control = "IRN"
                    elif encoded_fc == (1, 0):
                        flow_control = "Lossless"
                    else:
                        continue
                    topo = parsed_line[13]
                    netload = parsed_line[16]
                    key = (topo, netload, flow_control)
                    if key not in map_key_to_id:
                        map_key_to_id[key] = [[config_id, lb_mode]]
                    else:
                        map_key_to_id[key].append([config_id, lb_mode])

    desired_sizes = [1800, 3500, 4600, 5500, 6300, 7200, 8600, 16000, 31000, 2_000_000]
    lbmode_order = ["fecmp", "letflow", "conweave"]

    for k, v in map_key_to_id.items():

        ################## AVG plotting ##################
        fig, (ax_plot, ax_table) = plt.subplots(
            2, 1, figsize=(4, 6),
            gridspec_kw={'height_ratios': [3, 2]}
        )
        fig.subplots_adjust(hspace=0.80, bottom=0.18)
        pos = ax_plot.get_position()
        ax_plot.set_position([pos.x0, pos.y0 - 0.1, pos.width, pos.height])
        fig.tight_layout()

        ax_plot.set_xlabel("Flow Size (Bytes)", fontsize=11.5)
        ax_plot.set_ylabel("Avg FCT Slowdown", fontsize=11.5)

        ax_plot.spines['top'].set_visible(False)
        ax_plot.spines['right'].set_visible(False)
        ax_plot.yaxis.set_ticks_position('left')
        ax_plot.xaxis.set_ticks_position('bottom')

        xvals = [i for i in range(STEP, 100 + STEP, STEP)]

        # Collect results for each LB mode
        results_by_lb = {}

        for tgt_lbmode in lbmode_order:
            for vv in v:
                config_id = vv[0]
                lb_mode = vv[1]

                if lb_mode == tgt_lbmode:
                    fct_slowdown = output_dir + "/{id}/{id}_out_fct.txt".format(id=config_id)
                    results_by_lb[lb_mode] = get_steps_from_raw(
                        fct_slowdown, int(time_start), int(time_end), STEP
                    )

        # Plot lines
        for lb in lbmode_order:
            if lb not in results_by_lb:
                continue
            ax_plot.plot(
                xvals,
                results_by_lb[lb]["avg"],
                markersize=1.0,
                linewidth=3.0,
                label=lb
            )

        ax_plot.legend(bbox_to_anchor=(0.0, 1.2), loc="upper left",
                       borderaxespad=0, frameon=False, fontsize=12,
                       facecolor='white', ncol=2, labelspacing=0.4,
                       columnspacing=0.8)

        # Custom X-axis ticks based on one LB mode's size buckets
        any_lb = next(iter(results_by_lb))
        apply_custom_flow_size_ticks(ax_plot, results_by_lb[any_lb]["size"], xvals)

        ax_plot.grid(which='minor', alpha=0.2)
        ax_plot.grid(which='major', alpha=0.5)

        # Capture colors for each LB mode from plotted lines
        lb_colors = {}
        for idx, lb in enumerate(lbmode_order):
            if lb not in results_by_lb:
                continue
            line = ax_plot.lines[idx]
            lb_colors[lb] = line.get_color()

        # Add table subplot for AVG
        add_table_subplot(ax_table, desired_sizes, results_by_lb, lbmode_order, lb_colors, metric_key="avg")

        fig_filename = fig_dir + "/{}.pdf".format("AVG_TOPO_{}_LOAD_{}_FC_{}".format(k[0], k[1], k[2]))
        print(fig_filename)
        plt.savefig(fig_filename, transparent=False, bbox_inches='tight')
        plt.close()

        ################## P99 plotting ##################
        fig, (ax_plot, ax_table) = plt.subplots(
            2, 1, figsize=(4, 6),
            gridspec_kw={'height_ratios': [3, 2]}
        )
        fig.subplots_adjust(hspace=0.80, bottom=0.18)
        pos = ax_plot.get_position()
        ax_plot.set_position([pos.x0, pos.y0 - 0.1, pos.width, pos.height])
        fig.tight_layout()

        ax_plot.set_xlabel("Flow Size (Bytes)", fontsize=11.5)
        ax_plot.set_ylabel("p99 FCT Slowdown", fontsize=11.5)

        ax_plot.spines['top'].set_visible(False)
        ax_plot.spines['right'].set_visible(False)
        ax_plot.yaxis.set_ticks_position('left')
        ax_plot.xaxis.set_ticks_position('bottom')

        xvals = [i for i in range(STEP, 100 + STEP, STEP)]

        # Reuse results_by_lb but recompute to be safe (or reuse from above if identical)
        results_by_lb = {}
        for tgt_lbmode in lbmode_order:
            for vv in v:
                config_id = vv[0]
                lb_mode = vv[1]

                if lb_mode == tgt_lbmode:
                    fct_slowdown = output_dir + "/{id}/{id}_out_fct.txt".format(id=config_id)
                    results_by_lb[lb_mode] = get_steps_from_raw(
                        fct_slowdown, int(time_start), int(time_end), STEP
                    )

        # Plot lines
        for lb in lbmode_order:
            if lb not in results_by_lb:
                continue
            ax_plot.plot(
                xvals,
                results_by_lb[lb]["p99"],
                markersize=1.0,
                linewidth=3.0,
                label=lb
            )

        ax_plot.legend(bbox_to_anchor=(0.0, 1.2), loc="upper left",
                       borderaxespad=0, frameon=False, fontsize=12,
                       facecolor='white', ncol=2, labelspacing=0.4,
                       columnspacing=0.8)

        any_lb = next(iter(results_by_lb))
        apply_custom_flow_size_ticks(ax_plot, results_by_lb[any_lb]["size"], xvals)

        ax_plot.grid(which='minor', alpha=0.2)
        ax_plot.grid(which='major', alpha=0.5)

        # Capture colors for each LB mode from plotted lines
        lb_colors = {}
        for idx, lb in enumerate(lbmode_order):
            if lb not in results_by_lb:
                continue
            line = ax_plot.lines[idx]
            lb_colors[lb] = line.get_color()

        # Add table subplot for p99
        add_table_subplot(ax_table, desired_sizes, results_by_lb, lbmode_order, lb_colors, metric_key="p99")

        fig_filename = fig_dir + "/{}.pdf".format("P99_TOPO_{}_LOAD_{}_FC_{}".format(k[0], k[1], k[2]))
        print(fig_filename)
        plt.savefig(fig_filename, transparent=False, bbox_inches='tight')
        plt.close()


if __name__ == "__main__":
    setup()
    main()
