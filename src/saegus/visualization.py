import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import simuPOP as sim

class PopulationStatisticsPlot(object):
    """
    Plot for a specific arrangement of data resutling from the operator
    StoreStatistics
    """
    def __init__(self, pop, marker_sizes):
        self.pop = pop
        self.marker_sizes = marker_sizes


def plot_means_and_variances(selection_pop, selection_meta, drift_pop, drift_meta, figure_filename):
    """
    Plot for a specific arrangement of data resutling from the operator StoreStatistics
    """

    selection_statistics = pd.DataFrame(selection_pop.dvars().statistics)
    drift_statistics = pd.DataFrame(drift_pop.dvars().statistics)
    colors = {}
    markers = {}
    colors['drift'] = 'r'
    colors['meta-drift'] = 'm'
    colors['aggregate-drift'] = 'c'
    colors['selected'] = 'g'
    colors['meta-selected'] = 'b'
    colors['aggregate-selected'] = 'turquoise'

    markers['mean'] = 'o'
    markers['variance'] = 'D'

    gens = [i for i in range(0, selection_pop.dvars().gen+1, 2)]
    gen_labels = list(map(str, gens))
    selection_statistics = pd.DataFrame(selection_pop.dvars().statistics)
    drift_statistics = pd.DataFrame(drift_pop.dvars().statistics)
    sim.stat(selection_meta, meanOfInfo=['g', 'p'], vars=['meanOfInfo', 'meanOfInfo_sp'])
    sim.stat(selection_meta, varOfInfo=['g', 'p'], vars=['varOfInfo', 'varOfInfo_sp'])

    sim.stat(drift_meta, meanOfInfo=['g', 'p'], vars=['meanOfInfo', 'meanOfInfo_sp'])
    sim.stat(drift_meta, varOfInfo=['g', 'p'], vars=['varOfInfo', 'varOfInfo_sp'])

    selection_meta_mean = [selection_meta.dvars(i).meanOfInfo['p'] for i in range(selection_meta.numSubPop())]
    drift_meta_mean = [drift_meta.dvars(i).meanOfInfo['p'] for i in range(drift_meta.numSubPop())]

    selection_aggregate_mean = list(selection_statistics['aggregate'][11:22])
    selection_aggregate_variance = list(selection_statistics['aggregate'][33:44])
    vars_selection = list(selection_statistics['selected'][33:44])
    drift_aggregate_mean = list(drift_statistics['aggregate'][11:22])
    drift_aggregate_variance = list(drift_statistics['aggregate'][33:44])
    vars_drift = list(drift_statistics['selected'][33:44])

    #aggregate_sel = list(selection_statistics['aggregate'])
    #aggregrate_drift = list(drift_statistics['aggregate'])
    selected = list(selection_statistics[11:22]['selected'])
    drift = list(drift_statistics[11:22]['selected'])

    #selection_meta_means = [selection_meta.dvars(i).meanOfInfo['p'] for i in range(selection_meta.numSubPop())]
    #selection_meta_vars = [selection_meta.dvars(i).varOfInfo['p'] for i in range(selection_meta.numSubPop())]
    #drift_meta_means = [drift_meta.dvars(i).meanOfInfo['p'] for i in range(selection_meta.numSubPop())]
    #drift_meta_vars = [drift_meta.dvars(i).varOfInfo['p'] for i in range(selection_meta.numSubPop())]


    plt.style.use('ggplot')
    f, ax = plt.subplots(1, 2, figsize=(24, 16))

    stat_data = {}

    means_of_g = np.zeros((11, 5))
    vars_of_g = np.zeros((11, 5))
    means_of_p = np.zeros((11, 7))
    vars_of_p = np.zeros((11, 7))

    #means_of_g[:, 0] = gens
    #means_of_g[:, 1] = aggregate[:6]
    #means_of_g[:, 2] = nonsel[:6]
    #means_of_g[:, 3] = sel[:6]

    #stat_data['mean_g'] = means_of_g

    means_of_p[:, 0] = gens
    means_of_p[:, 1] = selected
    means_of_p[:, 2] = drift
    means_of_p[:, 3] = selection_meta_mean
    means_of_p[:, 4] = drift_meta_mean
    means_of_p[:, 5] = selection_aggregate_mean
    means_of_p[:, 6] = drift_aggregate_mean

    stat_data['mean_p'] = means_of_p
    mean_selected = ax[0].plot(means_of_p[:, 0], means_of_p[:, 1],
                                          markers['mean']+colors['selected'], markersize=8,
                                          alpha=0.6, label='Selection')
    mean_drift = ax[0].plot(means_of_p[:, 0], means_of_p[:, 2],
                                markers['mean']+colors['drift'], markersize=8,
                                alpha=0.6, label='Drift')
    mean_meta_selected = ax[0].plot(means_of_p[:, 0], means_of_p[:, 3],
                               markers['mean']+colors['meta-selected'], markersize=8,
                               alpha=0.6, label='Selection Meta-Population')
    mean_meta_drift = ax[0].plot(means_of_p[:, 0], means_of_p[:, 4], markers['mean']+colors['meta-drift'],
                          markersize=8, alpha=0.6, label='Drift Meta-Population')
    """
    mean_aggregate_selected = ax[0].plot(means_of_p[:, 0], means_of_p[:, 5],
                               markers['mean']+colors['aggregate-selected'], markersize=8,
                                         alpha=0.6, label='Selection Aggregate Population')
    mean_aggregate_drift = ax[0].plot(means_of_p[:, 0], means_of_p[:, 6], markers['mean']+colors['aggregate-drift'],
                          markersize=8, alpha=0.6, label='Drift Aggregate Population')
    """

    ax[0].set_xlim(-2.0, 22.0)
    mean_max = np.max(means_of_p) + 10
    ax[0].set_ylim(0, mean_max)

    #vars_of_g[:, 0] = gens
    #vars_of_g[:, 1] = aggregate[12:18]
    #vars_of_g[:, 2] = nonsel[12:18]
    #vars_of_g[:, 3] = sel[12:18]

    #stat_data['var_g'] = vars_of_g
    selection_meta_var = [selection_meta.dvars(i).varOfInfo['p'] for i in range(selection_meta.numSubPop())]
    drift_meta_var = [drift_meta.dvars(i).varOfInfo['p'] for i in range(drift_meta.numSubPop())]


    stat_data['var_p'] = vars_of_p
    vars_of_p[:, 0] = gens
    vars_of_p[:, 1] = vars_selection
    vars_of_p[:, 2] = vars_drift
    vars_of_p[:, 3] = selection_meta_var
    vars_of_p[:, 4] = drift_meta_var
    vars_of_p[:, 5] = selection_aggregate_variance
    vars_of_p[:, 6] = drift_aggregate_variance


    var_selected = ax[1].plot(vars_of_p[:, 0], vars_of_p[:, 1], markers['variance']+colors['selected'],
                               markersize=8, alpha=0.6, label='Selection')
    var_drift = ax[1].plot(vars_of_p[:, 0], vars_of_p[:, 2], markers['variance']+colors['drift'], markersize=8,
              alpha=0.6, label='Drift')
    var_seleected = ax[1].plot(vars_of_p[:, 0], vars_of_p[:, 3],
                               markers['variance']+colors['meta-selected'], markersize=8,
              alpha=0.6, label='Selection Meta-Population')
    drift_meta_var = ax[1].plot(vars_of_p[:, 0], vars_of_p[:, 4],
                          markers['variance']+colors['meta-drift'],
                          markersize=8, alpha=0.6, label='Drift Meta-Population')
    """
    selection_aggregate_variance = ax[1].plot(vars_of_p[:, 0], vars_of_p[:, 5],
                               markers['variance']+colors['aggregate-selected'], markersize=8,
                                              alpha=0.6, label='Selection Aggregate Population')
    drift_aggregate_variance = ax[1].plot(vars_of_p[:, 0], vars_of_p[:, 6],
                          markers['variance']+colors['aggregate-drift'],
                          markersize=8, alpha=0.6, label='Drift Aggregate Population')
    """
    ax[0].set_xlim(-2.0, 22.0)
    ax[1].set_xlim(-2.0, 22.0)
    var_max = np.max(vars_of_p) + 10
    ax[1].set_ylim(0, var_max)

    mean_handles, mean_labels = ax[0].get_legend_handles_labels()
    var_handles, var_labels = ax[1].get_legend_handles_labels()
    ax[0].legend(mean_handles, mean_labels)
    ax[1].legend(var_handles, var_labels)


    ax[0].set_xlabel("Generation", fontsize=18)
    ax[0].set_xticks(gens)
    ax[0].set_xticklabels(gen_labels)
    ax[1].set_xlabel("Generation", fontsize=18)
    ax[1].set_xticks(gens)
    ax[0].set_xticklabels(gen_labels)
    ax[0].set_ylabel("Phenotype", fontsize=18)
    ax[1].set_ylabel("Phenotype", fontsize=18)
    ax[0].set_title("Mean", fontsize=24)
    ax[1].set_title("Variance", fontsize=24)

    f.suptitle("Means and Variances Over 20 Generations of Selection", fontsize=30)

    f.savefig(figure_filename, dpi=300)

def plot_frequency_vs_effect(pop, haplotype_table, plot_title,
                                 plot_file_name,
                                 color_map='Dark2'):


    """
    Uses the haplotype data table to arrange data into a chromosome
    color coded multiple generation plot which shows the change in
    haplotype frequency over time. Haplotypes are dots with fixed
    x-position which shows their effect. Their motion along the y-axis
    which is frequency shows changes over time.
    :param plot_title:
    :param plot_file_name:
    :param color_map:
    :param pop:
    :param haplotype_table:
    """

    plt.style.use('ggplot')

    distinct_chromosomes = list(set(haplotype_table['chromosome']))
    number_of_different_colors = len(distinct_chromosomes)
    generation_labels = ['G_' + '{' + str(i) + '}' for i in
                         range(0, 2 * (pop.numSubPop()), 2)]
    generations = ['G_' + str(i) for i in range(0, 2 * (pop.numSubPop()), 2)]

    c_map = plt.get_cmap(color_map)

    colors = c_map(np.linspace(0, 1, number_of_different_colors))

    chromosome_colors = {distinct_chromosomes[i]: colors[i] for i in
                         range(number_of_different_colors)}

    effect_frq_by_chromosome = {}

    for sp in range(pop.numSubPop()):
        effect_frq_by_chromosome[sp] = {}
        for chrom in distinct_chromosomes:
            haplotype_frequencies = np.array(
                haplotype_table.loc[
                    haplotype_table['chromosome'] == chrom][generations[sp]])

            haplotype_effects = np.array(
                haplotype_table.loc[
                    haplotype_table['chromosome'] == chrom]['effect'])

            effect_frq_by_chromosome[sp][chrom] = np.array([
                haplotype_frequencies, haplotype_effects])

    # Figure parameters
    maximum_haplotype_effect = max(haplotype_table['effect'])

    generations = ['G_' + str(i) for i in range(0, 2 * (pop.numSubPop()) + 1, 2)]

    f, ax = plt.subplots(pop.numSubPop(), 1, figsize=(15, 40))
    for sp in range(pop.numSubPop()):
        ax[sp].set_xlim(-0.5, maximum_haplotype_effect + 4)
        ax[sp].set_ylim(-0.1, 1.1)
        for chrom in distinct_chromosomes:
            ax[sp].plot(effect_frq_by_chromosome[sp][chrom][1],
                        effect_frq_by_chromosome[sp][chrom][0],
                        markersize=8, linewidth=0.0, marker='*',
                        color=chromosome_colors[chrom],
                        label="Chrom {}".format(chrom))
        # handles, labels = ax[sp].get_legend_handles_labels()
        ax[sp].set_xlabel("Effect")
        ax[sp].set_ylabel("Frequency")
        ax[sp].set_title(r'${gen}$'.format(gen=generation_labels[sp]),
                         fontsize=12)
        ax[sp].legend(loc='best')
    f.suptitle(plot_title,
               fontsize=24)

    f.savefig(plot_file_name, dpi=300)

    return effect_frq_by_chromosome
