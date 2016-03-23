# -*- coding: utf-8 -*-
import simuPOP as sim
import math
import numpy as np
import pandas as pd
import collections as col
import os
from scipy import linalg
import matplotlib.pyplot as plt





class Frq(object):
    """
    A class to encapsulate information about alleles at quantitative trait
    loci. Requires a list of quantitative trait loci, a dictionary of
    alleles present in prefounder population and allele effects used to
    determine phenotypes for population.
    """
    def __init__(self, pop, *args, **kwargs):
        self.pop = pop

    def allele_frequencies(self, pop: sim.Population, loci: list):
        """
        Determine major and minor alleles in each generation the aggregate
        population. Generations in a meta-populations correspond to
        sub-populations.
        :param pop:
        :type pop:
        :param loci:
        :type loci:
        :return:
        :rtype:
        """
        sim.stat(pop, alleleFreq=loci, vars=['alleleFreq', 'alleleFreq_sp'])
        # removes empty sub-population.
        if pop.subPopSizes()[0] == 0:
            pop.removeSubPops(0)

        reversed_allele_frequencies = {}
        allele_frq = {}

        # Generations
        for i in range(self.pop.numSubPop()):
            for locus in range(self.pop.totNumLoci()):
                reversed_allele_frequencies[i, locus] = {}
                for allele in self.alleles[locus]:
                    frequency = self.pop.dvars(i).alleleFreq[locus][allele]
                    reversed_allele_frequencies[i, locus][frequency] = allele

        # Aggregate population
        for locus in range(pop.totNumLoci()):
            reversed_allele_frequencies[locus] = {}
            for allele in self.alleles[locus]:
                frequency = pop.dvars().alleleFreq[locus][allele]
                reversed_allele_frequencies[locus][frequency] = allele

        for i in range(pop.numSubPop()):
            allele_frq['minor', 'alleles', i] = col.OrderedDict()
            allele_frq['minor', 'frequency', i] = col.OrderedDict()
            allele_frq['frequencies', i] = col.OrderedDict()
            allele_frq['major', 'alleles', i] = col.OrderedDict()
            allele_frq['major', 'frequency', i] = col.OrderedDict()

        # Aggregate
        allele_frq['minor', 'alleles'] = col.OrderedDict()
        allele_frq['minor', 'frequency'] = col.OrderedDict()
        allele_frq['frequencies'] = col.OrderedDict()
        allele_frq['major', 'alleles'] = col.OrderedDict()
        allele_frq['major', 'frequency'] = col.OrderedDict()


        # Determine major/minor allele in aggregate population
        for locus in loci:
            temp_frq = []
            for allele in self.alleles[locus]:
                temp_frq.append(pop.dvars().alleleFreq[locus][allele])
            allele_frq['frequencies'][locus] = temp_frq
            minor_frequency = min(allele_frq['frequencies'][locus])
            major_frequency = max(allele_frq['frequencies'][locus])
            allele_frq['minor', 'alleles'][locus] = \
                reversed_allele_frequencies[locus][minor_frequency]
            allele_frq["major", "alleles"][locus] = \
                reversed_allele_frequencies[locus][major_frequency]


        for i in range(pop.numSubPop()):
            for locus in loci:
                temp_frq = []
                for allele in self.alleles[locus]:
                    temp_frq.append(pop.dvars(i).alleleFreq[locus][allele])
                allele_frq['frequencies', i][locus] = temp_frq

                minor_frequency = min(allele_frq['frequencies', i][locus])
                major_frequency = max(allele_frq['frequencies', i][locus])
                allele_frq['minor', 'alleles', i][locus] = \
                    reversed_allele_frequencies[i, locus][minor_frequency]
                allele_frq['major', 'alleles', i][locus] = \
                    reversed_allele_frequencies[i, locus][major_frequency]

        for locus in loci:
            major_allele = allele_frq['major', 'alleles'][locus]
            minor_allele = allele_frq['minor', 'alleles'][locus]
            allele_frq['major', 'frequency'][locus] = pop.dvars().alleleFreq[locus][major_allele]
            allele_frq['minor', 'frequency'][locus] = pop.dvars(

            ).alleleFreq[locus][minor_allele]
            for i in range(pop.numSubPop()):
                major_allele = allele_frq['major', 'alleles', i][locus]
                minor_allele = allele_frq['minor', 'alleles', i][locus]
                allele_frq['major', 'frequency', i][locus] = \
                    pop.dvars(i).alleleFreq[locus][major_allele]
                allele_frq['minor', 'frequency', i][locus] = \
                    pop.dvars(i).alleleFreq[locus][minor_allele]
        return allele_frq


    def rank_allele_effects(self, pop, loci, alleles,
                           allele_effects):
        """
        Collects information about alleles at quantitative trait loci into a
        dictionary. Determines favorable/unfavorable allele and corresponding
        frequency. Keys of quantitative_trait_alleles have similar hierarchy
        for both the alleles and their frequencies.
        :param pop:
        :param loci:
        :param alleles:
        :param allele_effects:


        """
        quantitative_trait_alleles = {}
        quantitative_trait_alleles['effects'] = col.OrderedDict()
        quantitative_trait_alleles['alleles'] = col.OrderedDict()
        quantitative_trait_alleles['alleles']['favorable'] = col.OrderedDict()
        quantitative_trait_alleles['alleles']['unfavorable'] = col.OrderedDict()
        quantitative_trait_alleles['frequency'] = col.OrderedDict()
        quantitative_trait_alleles['frequency']['favorable'] = col.OrderedDict()
        quantitative_trait_alleles['frequency']['unfavorable'] = col.OrderedDict()
        for locus in loci:
            temp_effects = []
            for allele in alleles[locus]:
                temp_effects.append(allele_effects[locus][allele])
            quantitative_trait_alleles['effects'][locus] = temp_effects

        for locus in loci:
            for allele in alleles[locus]:
                if allele_effects[locus][allele] == max(
                        quantitative_trait_alleles['effects'][locus]):
                    quantitative_trait_alleles['alleles']['favorable'][locus] =\
                        allele
                if allele_effects[locus][allele] == min(
                        quantitative_trait_alleles['effects'][locus]):
                    quantitative_trait_alleles['alleles']['unfavorable'][locus] =\
                        allele

        for locus, allele in quantitative_trait_alleles['alleles']['favorable'].items():
            quantitative_trait_alleles['frequency']['favorable'][locus] = \
                pop.dvars().alleleFreq[locus][allele]
        for locus, allele in quantitative_trait_alleles['alleles']['unfavorable'].items():
            quantitative_trait_alleles['frequency']['unfavorable'][locus] =\
                pop.dvars().alleleFreq[locus][allele]
        for i in range(pop.numSubPop()):
            for locus, allele in quantitative_trait_alleles['alleles']['favorable'].items():
                quantitative_trait_alleles['frequency']['favorable'][i, locus] \
                    = pop.dvars(i).alleleFreq[locus][allele]
            for locus, allele in quantitative_trait_alleles['alleles']['unfavorable'].items():
                quantitative_trait_alleles['frequency']['unfavorable'][i,locus]\
                    = pop.dvars(i).alleleFreq[locus][allele]

        return quantitative_trait_alleles

    def allele_frq_table(self, pop, number_gens,
        allele_frq_data, recombination_rates, genetic_map):
        """
        Generates a large table which centralizes all allele frequency data.
        The data is inserted into a pandas DataFrame object.
        Useful for downstream analysis and insertion into a database.

        Allele frequency data is first built up in a regular *dict* object
        then inserted into a
        :param pop:
        :param number_gens:
        :param allele_frq_data:
        :param recombination_rates:
        :param genetic_map:
        """


        data_columns = ['abs_index', 'chrom', 'locus', 'major',
                        'minor', 'recom_rate', 'cM', 'v']
        generation_labels = ['G_'+str(i)
                             for i in range(0, number_gens+1, 2)]
        data_columns = data_columns + generation_labels + ['aggregate']
        data = {}
        breakpoints = col.OrderedDict()
        for locus in range(pop.totNumLoci()):
            if recombination_rates[locus] == 0.01:
                breakpoints[locus] = locus + 1

        diagram = ["|"]*pop.totNumLoci()

        for locus, point in breakpoints.items():
            try:
                diagram[point] = '*'
            except IndexError:
                pass

        qtl_diagram = ['o']*pop.totNumLoci()
        for locus in pop.dvars().triplet_qtl:
            qtl_diagram[locus] = 'x'

        chromosomes = []
        relative_loci = []
        for locus in range(pop.totNumLoci()):
            pair = pop.chromLocusPair(locus)
            chromosomes.append(pair[0]+1)
            relative_loci.append(pair[1])

        data['chrom'] = chromosomes
        data['locus'] = relative_loci


        data['recom_rate'] = recombination_rates
        data['v'] = diagram
        data['cM'] = genetic_map['cM_pos']
        data['qtl'] = qtl_diagram


        data['abs_index'] = [locus for locus in range(pop.totNumLoci())]
        data['minor'] = [allele_frq_data['minor', 'alleles'][locus] for locus in range(pop.totNumLoci())]
        data['major'] = [allele_frq_data['major', 'alleles'][locus] for locus in range(pop.totNumLoci())]
        for sp_idx, label in enumerate(generation_labels):
            data[label] = [allele_frq_data['minor', 'frequency', sp_idx][
                               locus] for locus in range(pop.totNumLoci())]
        data['aggregate'] = [allele_frq_data['minor', 'frequency'][locus] for locus in range(pop.totNumLoci())]
        af_table = pd.DataFrame(data, columns=data_columns)
        return af_table


def qt_allele_table(pop, qt_alleles, allele_effects,
                    number_of_generations):
    """
    Generates a pd.DataFrame object of data relevant to quantitative
    trait alleles across all generations.
    :param qt_alleles:
    :type qt_alleles:
    :param allele_effects:
    :type allele_effects:
    :return:
    :rtype:
    """
    #qtdata = {}
    data_columns = ['abs_index', 'chrom', 'locus',
     'favorable', 'fav_effect', 'unfavorable', 'unfav_effect',
                    'effect_diff']

    #generation_labels = ['G_'+str(i)
    #                     for i in range(0, number_of_generations+1, 2)]
    #data_columns = data_columns + generation_labels + ['aggregate']

    chromosomes = []
    relative_loci = []
    for locus in range(pop.totNumLoci()):
        pair = pop.chromLocusPair(locus)
        chromosomes.append(pair[0]+1)
        relative_loci.append(pair[1])

    qtdata = dict(chrom=chromosomes,
                  locus=relative_loci,
                  abs_index=np.array([i for i in range(
                      pop.totNumLoci())], dtype=np.int16),
                  favorable=np.zeros((pop.totNumLoci), dtype=np.int8),
                  unfavorable=np.zeros((pop.totNumLoci),
                                       dtype=np.int8),
                  fav_effect=np.zeros((pop.totNumLoci)),
                  unfav_effect=np.zeros((pop.totNumLoci)),
                  effect_diff=np.zeros((pop.totNumLoci)),
                )


# todo Add generation labels back in after extended table works.
#        for subpop, label in zip(range(pop.numSubPop(),
#                                       generation_labels)):
#            qtdata[label] = np.zeros((pop.totNumLoci))

    for qtlocus in pop.dvars().triplet_qtl:
        qtdata['favorable'][qtlocus] = qt_alleles['alleles'][
            'favorable'][qtlocus]
        qtdata['unfavorable'][qtlocus] = qt_alleles['alleles'][
            'favorable'][qtlocus]


    # allele_effects_keyed by [locus][allele]


        for fav_allele in qt_alleles['alleles']['favorable'].values():
            qtdata['fav_effect'][qtlocus] = allele_effects[qtlocus][
                fav_allele]
        for unfav_allele in qt_alleles['alleles']['unfavorable'].values():
            qtdata['unfav_effect'][qtlocus] = allele_effects[qtlocus][
                unfav_allele]


# todo Add sub-population qtallele data in after working table
#            for subpop, label in zip(range(pop.numSubPop()),
#                                 generation_labels):
#                qtdata[label][qtlocus] = [qt_alleles['frequency']['favorable'][
#                                         subpop,
#                                                                 locus] for
#                            locus in pop.dvars().triplet_qtl]
#       qtdata['aggregate'][qtlocus] = [qt_alleles['frequency'][
            # 'favorable'][locus]
#                              for locus in pop.dvars().triplet_qtl]

        qtdata['effect_diff'][qtlocus] = \
            qtdata['fav_effect'][qtlocus] - qtdata['unfav_effect'][qtlocus]

    qta_table = pd.DataFrame(qtdata, columns=data_columns)
    return qta_table


def collect_haplotype_data(pop, allele_effects, quantitative_trait_loci):
    """

    :param pop:
    :type pop:
    :param allele_effects:
    :type allele_effects:
    :param quantitative_trait_loci:
    :type quantitative_trait_loci:
    :return:
    :rtype:
    """

    haplotypes = {}
    haplotypes['loci'] = {}
    for k, i in enumerate(range(0, len(quantitative_trait_loci), 3)):
        haplotypes['loci'][k] = (quantitative_trait_loci[i],
                             quantitative_trait_loci[i+1],
                             quantitative_trait_loci[i+2])

    haplotypes['alleles'] = {}
    haplotypes['effect'] = {}
    haplotypes['frequency'] = {}
    for loci in haplotypes['loci'].values():
        haplotypes['frequency'][loci] = {}
        for sp in range(pop.numSubPop()):
            haplotypes['frequency'][loci][sp] = {}

    sim.stat(pop, haploFreq=list(haplotypes['loci'].values()),
             vars=['haploFreq', 'haploFreq_sp'])

    for k, v in haplotypes['loci'].items():
        haplotypes['alleles'][v] = list(pop.dvars(0).haploFreq[v].keys())

    for sp in range(pop.numSubPop()):
        for loci, triplet in haplotypes['alleles'].items():
            for alleles in triplet:
                haplotypes['frequency'][loci][sp][alleles] = pop.dvars(
                    sp).haploFreq[loci][alleles]

    for htype, triplets in haplotypes['alleles'].items():
        haplotypes['effect'][htype] = {}
        for trip in triplets:
            htype_effect = allele_effects[htype[0]][trip[0]] +\
            allele_effects[htype[1]][trip[1]] +\
            allele_effects[htype[2]][trip[2]]
            haplotypes['effect'][htype][trip] = htype_effect

    return haplotypes


def generate_haplotype_data_table(pop, haplotype_data):
    """
    Generates a table for easy analysis and visualization of haplotypes,
    effects, frequencies and locations.


    :param pop:
    :type pop:
    :param haplotype_data:
    :type haplotype_data:
    :return:
    :rtype:
    """
    integer_to_snp = {0: 'A', 1: 'C', 2: 'G', 3: 'T', 4: '+', 5: '-'}
    haplotype_table = []
    data_columns = ['centered_on', 'relative_position', 'chromosome',
                    'haplotype', 'effect']
    generation_columns = ['G_'+str(i) for i in range(0, 2*(pop.numSubPop()),
                                                     2)]
    data_columns.extend(generation_columns)
    for locus in haplotype_data['loci'].values():
        for triplet in haplotype_data['alleles'][locus]:
            generational_frequencies = [haplotype_data['frequency'][locus][sp][triplet]
                                        for sp in range(pop.numSubPop())]
            effect = haplotype_data['effect'][locus][triplet]
            snp_triplet = integer_to_snp[triplet[0]] + \
                          integer_to_snp[triplet[1]] + \
                          integer_to_snp[triplet[2]]
            chromosome = pop.chromLocusPair(locus[1])[0] + 1
            relative_locus = pop.chromLocusPair(locus[1])[1]
            row = [locus[1]] + \
                  [relative_locus] +\
                  [chromosome] + \
                  [snp_triplet] + \
                  [effect] + \
                  generational_frequencies
            haplotype_table.append(row)
    return pd.DataFrame(haplotype_table, columns=data_columns)


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
                          range(0, 2*(pop.numSubPop()), 2)]
    generations = ['G_' + str(i) for i in range(0, 2*(pop.numSubPop()), 2)]

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

    generations = ['G_'+str(i) for i in range(0, 2*(pop.numSubPop()) + 1, 2)]

    f, ax = plt.subplots(pop.numSubPop(), 1, figsize=(15, 40))
    for sp in range(pop.numSubPop()):
        ax[sp].set_xlim(-0.5, maximum_haplotype_effect+4)
        ax[sp].set_ylim(-0.1, 1.1)
        for chrom in distinct_chromosomes:
            ax[sp].plot(effect_frq_by_chromosome[sp][chrom][1],
                    effect_frq_by_chromosome[sp][chrom][0],
                    markersize=8, linewidth=0.0, marker='*',
                    color=chromosome_colors[chrom],
                        label="Chrom {}".format(chrom))
        #handles, labels = ax[sp].get_legend_handles_labels()
        ax[sp].set_xlabel("Effect")
        ax[sp].set_ylabel("Frequency")
        ax[sp].set_title(r'${gen}$'.format(gen=generation_labels[sp]),
                         fontsize=12)
        ax[sp].legend(loc='best')
    f.suptitle(plot_title,
               fontsize=24)

    f.savefig(plot_file_name, dpi=300)

    return effect_frq_by_chromosome







class MetaData(object):
    """
    The wgs is extensively paramterized. Hence changing one parameter will potentially produce a significantly different
    result in the final population. Therefore, a set of replications is defined by a particular of parameterization.
    The parameterization will be described in a metadata document. The class MetaData is responsible for collecting
    the parameterization information and processing it into a writable file.
    """

    def __init__(self, prefounders, founders, population_sizes, allele_effect_information,
                 allele_effects_table, metadata_filename):
        """
        An instance of MetaData should have enough information to completely specify a population without using any
        external information.
        :param prefounders: Prefounder population of the 26 lines which were used to make the NAM population.
        :param founders: Subset of prefounders used to make a derived population.
        :param population_sizes: Size of the population during the F_one, F_two, 'mate-and-merge' phase and finally
        the selection phase.
        :param allele_effect_information: Information about the distribution of allele effects and the corresponding
        parameters, the random number generator package and random seed used to generate the allele effects.
            Ex: normal(0, 1), numpy.random, seed 1337.
        :param allele_effects_table: The actual tabular/dictionary representation of the realized allele effect values.
        """
        self.prefounders = prefounders
        self.founders = founders
        self.population_sizes = population_sizes
        self.allele_effect_information = allele_effect_information
        self.allele_effects_table = allele_effects_table
        self.metadata_filename = metadata_filename


        # A master function will use other functions to write the necessary information to file.

    @staticmethod
    def ascii_chromosome_representation(pop, reduction_factor, metadata_filename):
        """
        Writes a ascii representation of chromosomes with uninteresting loci
        as * and QTL as |. The representation is has scale 1 /
        reduction_factor to make it viable to put into a .txt document.
        :param pop:
        :param reduction_factor:
        :param metadata_filename:
        """
        reduced_chromosomes = [math.floor(chrom/reduction_factor) for chrom in list(pop.numLoci())]
        reduced_qtl = [math.floor(pop.chromLocusPair(locus)[1]/reduction_factor) for locus in pop.dvars().properQTL]
        chromosomes_of_qtl = [pop.chromLocusPair(qtl)[0] for qtl in pop.dvars().properQTL]
        aster_chroms = [['*']*chrom_len for chrom_len in reduced_chromosomes]
        for red_qtl, chrom_of_qtl in zip(reduced_qtl, chromosomes_of_qtl):
            aster_chroms[chrom_of_qtl][red_qtl] = '|'
        with open(metadata_filename, 'a') as chrom_file:
            chrom_file.write('Scale: 1/%d\n' % reduction_factor)
            for idx, chrom in enumerate(aster_chroms):
                idx += 1
                chrom_file.write('Chromosome: %d\n' % idx)
                chrom_file.write(''.join(chrom) + '\n')

    @staticmethod
    def coefficient_of_dispersion(pop):
        """
        Mean to variance ratio of pairwise sequential distances of quantitative trait loci.
        Note that this statistic contributes nothing if there is only one qtl on a chromosome.
        :param pop:
        """
        chrom_loc_pairs = [pop.chromLocusPair(pop.dvars().properQTL[i]) for i in range(len(pop.dvars().properQTL))]
        chromosomes = [chrom_loc_pairs[i][0] for i in range(len(chrom_loc_pairs))]
        diffs = []
        for i in range(len(chrom_loc_pairs)):
            if chromosomes[i-1] == chromosomes[i]:
                diffs.append(math.fabs(chrom_loc_pairs[i-1][1] - chrom_loc_pairs[i][1]))
        diffs = np.array(diffs)
        mean = np.mean(diffs)
        var = np.var(diffs)
        var_to_mean_ratio = var/mean
        return var_to_mean_ratio

    @staticmethod
    def genomic_dispersal(pop):
        """
        Genomic dispersal is a novel statistics which measures the spread of loci over a genome.z All loci of a chromosome
        are compared to the center of the genetic map (in cMs) and weighted by the length of that chromosome.
        :param pop: Population used for recurrent selection
        :return: Dimensionless constant describing the parameterization
        """
        chrom_loc_pairs = [pop.chromLocusPair(pop.dvars().properQTL[i]) for i in range(len(pop.dvars().properQTL))]
        chromosomes = [chrom_loc_pairs[i][0] for i in range(len(chrom_loc_pairs))]
        qtl_positions = [(chrom_loc_pairs[i][1]) for i in range(len(chrom_loc_pairs))]
        chromosome_midpoints = {i: (pop.numLoci()[i]/2) for i in range(len(pop.numLoci()))}
        diffs = []
        for pos, chrom, i in zip(qtl_positions, chromosomes, range(len(chrom_loc_pairs))):
            diffs.append(pos - chromosome_midpoints[chrom])
        squared_diffs = np.square(np.array(diffs))
        root_squared_diffs = np.sqrt(squared_diffs)
        denominator_lengths = np.array(list(pop.numLoci()))
        pre_genetic_dispersal = np.divide(root_squared_diffs, denominator_lengths)
        genomic_dispersal = sum(pre_genetic_dispersal)
        return genomic_dispersal


class PCA(object):
    """
    Class for performing principal component analyis on genotype matrices.
    Test for population structure significance tests the largest eigenvalue
    of the genotype covarience matrix. Details can be found in the paper:
    Population Structure and Eigenanalysis Patterson et al 2006.
    """
    def __init__(self, pop, loci, qt_data):
        self.pop = pop
        self.loci = loci
        self.qt_data = qt_data

    def __str__(self):
        return "Parameters: PopSize {}, Number of Loci: {}, " \
               "Keys of Data: {}.".format(self.pop.popSize(), len(self.loci),
                                         self.qt_data.keys())

    def calculate_count_matrix(self, pop, alleles, count_matrix_filename):
        """
        A function to calculate the copy numbers of either the minor or
        major allele for each individual at each locus. Minor or major
        alleles parameter is a single set of alleles which determines if the
        return is the minor or major allele count matrix.
        :param pop:
        :param alleles:
        :param count_matrix_filename:
        """
        comparison_array = [alleles[locus] for locus in range(pop.totNumLoci())]
        count_matrix = np.zeros((pop.popSize(), len(alleles)))
        for i, ind in enumerate(pop.individuals()):
            alpha = np.equal(np.array(comparison_array), ind.genotype(
                ploidy=0), dtype=np.int8)
            beta = np.equal(np.array(comparison_array), ind.genotype(ploidy=1),
                            dtype=np.int8)
            counts = np.add(alpha, beta, dtype=np.int8)
            count_matrix[i, :] = counts
        np.savetxt(count_matrix_filename, count_matrix, fmt="%d")
        return count_matrix

    def svd(self, pop, count_matrix):
        """

        Follows procedure of Population Structure and Eigenanalysis
        Patterson et al 2006.
        Constructs a genotype matrix of bi-allelic loci where each entry is
        the number of copies of the major allele at each locus. The genotype
        matrix has dimensions (number_of_individuals)*(number_of_markers).
        :param pop:
        :param count_matrix:

        """
        shift = np.apply_along_axis(np.mean, axis=1, arr=count_matrix)
        p_vector = np.divide(shift, 2)
        scale = np.sqrt(np.multiply(p_vector, (1-p_vector)))

        shift_matrix = np.zeros((pop.popSize(), pop.totNumLoci()))
        scale_matrix = np.zeros((pop.popSize(), pop.totNumLoci()))
        for i in range(pop.totNumLoci()):
            shift_matrix[:, i] = shift
            scale_matrix[:, i] = scale

        corrected_matrix = (count_matrix - shift_matrix)/scale_matrix
        # singular value decomposition using scipy linalg module
        eigenvectors, s, v = linalg.svd(corrected_matrix)
        eigenvalues = np.diagonal(np.square(linalg.diagsvd(s, pop.popSize(),
                                                           pop.totNumLoci()))).T
        sum_of_eigenvalues = np.sum(eigenvalues)
        fraction_of_variance = np.divide(eigenvalues, sum_of_eigenvalues)
        eigen_data = {}
        eigen_data['vectors'] = eigenvectors
        eigen_data['values'] = eigenvalues
        eigen_data['fraction_variance'] = fraction_of_variance
        return eigen_data

    def test_statistic(self, pop, eigenvalues):
        sum_of_eigenvalues = np.sum(eigenvalues)
        n_hat_numerator = (pop.popSize() + 1)*sum_of_eigenvalues
        n_hat_denom = (pop.popSize()-1)*sum_of_eigenvalues - sum_of_eigenvalues
        n_hat = n_hat_numerator/n_hat_denom
        lowercase_l = (pop.popSize() - 1)*eigenvalues[0]
        mu_hat = np.square((np.sqrt(n_hat - 1) +
                            np.sqrt(pop.popSize()))) / n_hat
        sigma_hat = ((np.sqrt(n_hat - 1) + np.sqrt(pop.popSize()))/n_hat) * \
                    (((1/np.sqrt(n_hat - 1)) + 1/np.sqrt(pop.popSize())) ** (
                        1 / 3.0))
        test_statistic = (lowercase_l - mu_hat) / sigma_hat
        return test_statistic

class GWAS(object):
    """
    A class to collect and format all data in preparation for GWAS using TASSEL.
    """

    def __init__(self, pop, individual_names, locus_names, positions, *args,
                 **kwargs):
        self.pop = pop
        self.individual_names = individual_names
        self.locus_names = locus_names
        self.positions = positions


    def hapmap_formatter(self, int_to_snp_conversions, hapmap_matrix_filename):
        """
        Converts genotype data from sim.Population object to HapMap file format
        in expectation to be used in TASSEL for GWAS. At present the column
        names will be hardcoded as will some of the values.
        ``hapmap_matrix_filename`` is the name of the file the formatted
        matrix will be written to.
        :param int_to_snp_conversions:
        :param hapmap_matrix_filename:
        :return:
        :rtype:
        """
        hapmap_data = {}
        hapmap_data['rs'] = self.locus_names
        hapmap_data['alleles'] = ['NA']*self.pop.totNumLoci()
        hapmap_data['chrom'] = [self.pop.chromLocusPair(locus)[0]+1 for
                                locus in
                                range(self.pop.totNumLoci())]
        hapmap_data['pos'] = self.positions

        # Several columns which are set to 'NA'.
        extraneous_columns = ['strand', 'assembly', 'center', 'protLSID',
                              'assayLSID', 'panelLSID', 'QCcode']
        for column in extraneous_columns:
            hapmap_data[column] = ['NA']*self.pop.totNumLoci()

        # Each individual has a column. Simulated individuals will have names
        # reflecting some information about them. 'RS' recurrent selection,
        # 'R' rep, 'G' generation and 'I' ind_id

        # Finally each individual's genotype must be converted to HapMap format

        for ind in self.pop.individuals():
            alpha, beta = ind.genotype(ploidy=0), ind.genotype(ploidy=1)
            hapmap_data[self.individual_names[ind.ind_id]] = [
                ''.join(sorted(int_to_snp_conversions[a]
                               + int_to_snp_conversions[b]))
                                 for a, b in zip(alpha, beta)]


        # Need to guarantee that the column names are in same order as the
        # genoype data. Iterate over individuals in population to build up a
        #  list of names will guarantee that col names are in same order as
        # the hapmap_data
        ordered_names = [self.individual_names[ind.ind_id] for ind in
                         self.pop.individuals()]

        hapmap_ordered_columns = ['rs', 'alleles', 'chrom', 'pos', 'strand',
                           'assembly', 'center', 'protLSID', 'assayLSID',
                               'panelLSID', 'QCcode'] + ordered_names

        hapmap_matrix = pd.DataFrame(columns=hapmap_ordered_columns)
        for k, v in hapmap_data.items():
            hapmap_matrix[k] = v

        hapmap_matrix.to_csv(hapmap_matrix_filename, sep='\t',
                             index=False)

        return hapmap_matrix

    def trait_formatter(self, trait_filename):
        """
        Simple function to automate the formatting of the phenotypic data.
        Because of the way the header must be written the file is opened in
        append mode. Rewriting to the same file many times could introduce an
        unsuspected bug.
        :param trait_filename:
        """
        header = "<Trait> sim\n"

        # Ensure phenotype and name are coming from the same individual


        phenotypes = []
        ind_names = []
        for ind in self.pop.individuals():
            phenotypes.append(ind.p)
            ind_names.append(self.individual_names[ind.ind_id])

        trait_vector = pd.DataFrame([ind_names, phenotypes]).T

        cwd = os.getcwd()
        file_out_path = os.path.join(cwd, trait_filename)

        if os.path.exists(file_out_path):
            os.remove(file_out_path)
        with open(trait_filename, 'a') as f:
            f.write(header)
            trait_vector.to_csv(f, sep=' ', index=False, header=False)

        return trait_vector

    def population_structure_formatter(self, eigen_data, structure_filename):
        """
        Writes the first two of the population structure matrix to a
        file. First column of the file is are names.
        :param structure_filename:
        :param eigen_data:
        """

        ordered_names = [self.individual_names[ind.ind_id] for ind in
                         self.pop.individuals()]

        structure_matrix = pd.DataFrame([list(eigen_data['vectors'][:, 0].T),
                                     list(eigen_data['vectors'][:, 1].T)]).T

        structure_matrix.index = ordered_names

        header = "<Covariate>\t\t\n<Trait>\td1\td2\n"

        cwd = os.getcwd()
        file_out_path = os.path.join(cwd, structure_filename)

        if os.path.exists(file_out_path):
            os.remove(file_out_path)
        with open(structure_filename, 'a') as f:
            f.write(header)
            structure_matrix.to_csv(f, sep='\t', index=True, header=False)

        return structure_matrix

    def calc_kinship_matrix(self, allele_count_matrix, allele_data,
                            kinship_filename):
        """
        Calculates the kinship matrix according to VanRaden 2008:
        Efficient Methods to Compute Genomic Predictions and writes it to a
        file formatted for Tassel. The variable names try to be consistent
        with the variable names in the paper.

        The allele frequencies used for this function are with respect to
        the aggregate population: all individuals sampled during selection.

        Unsure if I should use the G0 allele or not.
        Will decide after TASSEL results.

        :param allele_counts:
        :param allele_data:
        :param kinship_filename:
        :return:
        :rtype:
        """

        M = np.matrix(allele_count_matrix - 1)

        # Second allele in the unselected, un-inbred base population.
        # Refers to major allele in G_0
        allele_frequencies = np.array([allele_data['minor', 'frequency'][locus]
                                    for locus in range(self.pop.totNumLoci())])

        P = 2*(allele_frequencies - 0.5)

        Z = M - P

        scaling_terms = np.zeros((self.pop.totNumLoci()))
        for locus, probability in enumerate(allele_frequencies):
            scaling_terms[locus] = 2*probability*(1 - probability)

        scaling_factor = sum(scaling_terms)

        G = Z*Z.T/scaling_factor

        annotated_G = pd.DataFrame(G, index=[self.individual_names[ind.ind_id]
                                             for ind in
                                             self.pop.individuals()])

        # Tassel example has number of individuals in the header of the G
        # matrix file
        header = "{}\n".format(self.pop.popSize())

        cwd = os.getcwd()
        file_out_path = os.path.join(cwd, kinship_filename)

        if os.path.exists(file_out_path):
            os.remove(file_out_path)
        with open(kinship_filename, 'w') as f:
            f.write(header)
            annotated_G.to_csv(f, sep=' ', index=True, header=False)

        return annotated_G


def generate_tassel_gwas_configs(input_directory_prefix,
                                 out_directory_prefix,
                                 config_file_prefix,
                                 run_identifier_prefix,
                                 xml_pipeline_template):
    """
    Creates an xml file to run TASSEL using a mixed linear model approach.
    Assumes use of hapmap, kinship, phenotype and population structure files.




    The TASSEL command line interface requires a considerable number of
    options to run GWAS. It is impractical to run the command line manually
    for the number of replications in a simulated study. The TASSEL command
    line interface allows the user to input a .xml file with the same
    information which is used in the terminal.

    :param input_directory_prefix: Directory path to send the input files.
    :param run_identifier_prefix: Identifier for single replicate of data
    :param xml_pipeline_template: XML file already setup for running a
    specific kind of GWAS
    :return: XML file to run a single replicate of data using TASSEL
    """


    import xml.etree.ElementTree as ET
    import lxml.etree as etree

    tree = ET.parse(xml_pipeline_template)
    root = tree.getroot()
    lxml_tree = etree.fromstring(ET.tostring(root))
    lxml_root = lxml_tree.getroottree()

    hapmap_filename = input_directory_prefix + run_identifier_prefix + \
                      'simulated_hapmap.txt'
    phenotype_filename = input_directory_prefix + run_identifier_prefix + \
        'phenotype_vector.txt'
    pop_struct_filename = input_directory_prefix + run_identifier_prefix + \
                          'structure_matrix.txt'
    kinship_filename = input_directory_prefix + run_identifier_prefix + \
                       'kinship_matrix.txt'

    tassel_outputs = out_directory_prefix + run_identifier_prefix + 'gwas_out_'

    config_filname = config_file_prefix + run_identifier_prefix + \
                     'sim_gwas_pipeline.xml'

    lxml_root.find('fork1/h').text = hapmap_filename
    lxml_root.find('fork2/t').text = phenotype_filename
    lxml_root.find('fork3/q').text = pop_struct_filename
    lxml_root.find('fork4/k').text = kinship_filename

    lxml_root.find('combine6/export').text = tassel_outputs

    config_file_out = config_filname

    lxml_root.write(config_file_out, encoding="UTF-8",
                   method="xml", xml_declaration=True, standalone='',
                    pretty_print=True)


def parameter_set_writer(directory_prefix, run_prefix, mating,
                         quantitative, effects,
                         genetic_structure):
    """
    Simulation parameters are collected in separate dictionary objects.
    This function writes all parameter information into a set of human
    readable .yaml files.

    :param directory_prefix:
    :param run_prefix: Identifier for a set of simulated data
    :param mating: Parameters which specifying mating
    :param quantitative: Dictionary of qtl for each replicate
    :param effects:
    :param genetic_structure:
    :return:
    """

    import yaml


    file_names = {}

    file_names[run_prefix + 'mating.yaml'] = mating
    file_names[run_prefix + 'qtl.yaml'] = quantitative
    file_names[run_prefix + 'allele_effects.yaml'] = effects
    file_names[run_prefix + 'genetic_structure.yaml'] = genetic_structure

    for name, param_set in file_names.items():
        with open(name, 'w') as p_stream:
            yaml.dump(param_set, p_stream)


def parameter_set_reader(parameter_filename):
    """
    Reads a file of .yaml parameters for an easy way to parameterize a
    simulation. Alternately the user would have to derive a great deal of
    information from raw files.
    :param parameter_filename:
    :return:
    """

    pass


class Synbreed(object):

    def __init__(self, genotypes, phenotypes, genetic_map):
        self.genotypes = genotypes
        self.phenotypes = phenotypes
        self.genetic_map = genetic_map

    def genotype_formatter(self, hap_map, syn_genotype_filename):
        """
        Modifies ``hap_map`` to obtain the format for Synbreed.
        Subtracts extraneous columns, transposes the result, adds 1 to each
        index to convert Python index to R index. Then prepends each locus
        with "M" indicating 'marker'.
        :param hap_map: A simulated hapmap file from hapmap_formatter.
        :param syn_genotype_filename: Name of the file which the modified
        hapmap is written to.

        """

        syn_geno_map = hap_map.drop(["rs", "alleles", "chrom", "pos", "strand",
                   "assembly", "center", "protLSID", "assayLSID",
                  "panelLSID", "QCcode"], axis=1).T
        syn_geno_map.columns = ["M" + str(idx + 1) for idx in syn_geno_map.columns]

        syn_geno_map.to_csv(syn_genotype_filename, sep="\t", index=True,
                            header=False)

        return syn_geno_map