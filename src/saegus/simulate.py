#! usr/bin/python
import simuPOP as sim
import random
import collections as col
import numpy as np
from . import breed, operators



class RandomMating(object):
    """
    ``Truncation`` is a class which encapsulates all parameters and
    functions to perform recurrent truncation selection on a quantitative
    trait. The trait is assumed to have a simple additive basis so all
    phenotypes are calculated by adding contribution of :math:`n` loci plus error.
    """

    def __init__(self,
                 generations_of_random_mating=1,
                 operating_population_size=2000,
                 proportion_of_individuals_saved=0.05,
                 overshoot_as_proportion=0.50,
                 individuals_per_breeding_subpop=5,
                 heritability=0.7,
                 meta_pop_sample_sizes=100,
                 ):
        self.generations_of_random_mating = generations_of_random_mating
        self.operating_population_size = operating_population_size
        self.proportion_of_individuals_saved = proportion_of_individuals_saved
        self.overshoot_as_proportion = overshoot_as_proportion
        self.individuals_per_breeding_subpop = individuals_per_breeding_subpop
        self.heritability = heritability
        self.meta_pop_sample_sizes = meta_pop_sample_sizes

        self.breeding_parameters = col.OrderedDict()
        self.number_of_breeding_individuals = int(
            proportion_of_individuals_saved * operating_population_size)
        self.breeding_parameters['number_of_breeding_individuals'] = \
            self.number_of_breeding_individuals
        self.number_of_breeding_subpops = \
            int(self.number_of_breeding_individuals /\
                self.individuals_per_breeding_subpop)
        self.breeding_parameters['number_of_breeding_subpops'] = \
            self.number_of_breeding_subpops
        self.total_number_of_offspring_per_generation = \
            int(operating_population_size * (1 + self.overshoot_as_proportion))
        self.breeding_parameters['total_number_of_offspring_per_generation'] = \
            self.total_number_of_offspring_per_generation
        self.offspring_per_breeding_subpop = \
            int(self.total_number_of_offspring_per_generation/\
                self.number_of_breeding_subpops)
        self.breeding_parameters['offspring_per_breeding_subpop'] = \
            self.offspring_per_breeding_subpop
        self.offspring_per_female = \
            int(self.offspring_per_breeding_subpop /
                self.individuals_per_breeding_subpop)
        self.breeding_parameters['offspring_per_female'] = \
            self.offspring_per_female
        self.number_of_nonbreeding_individuals = \
            int(self.operating_population_size -
                self.number_of_breeding_individuals)
        self.breeding_parameters['number_of_nonbreeding_individuals'] = \
            self.number_of_nonbreeding_individuals
        self.number_of_offspring_discarded = int(
            self.overshoot_as_proportion * self.operating_population_size)
        self.breeding_parameters['number_of_offspring_discarded'] = \
            self.number_of_offspring_discarded

    def __str__(self):
        rdm_info = 'Type: Random Mating\n' +\
                    '**************************\n' +\
                    'Generations of Random Mating: {}\n'.format(self.generations_of_random_mating) +\
                    'Operating Population Size: {}\n'.format(
                        self.operating_population_size) +\
                    'Proportion of Individuals Saved: {}\n'.format(
                        self.proportion_of_individuals_saved)

        return rdm_info

    def recombinatorial_convergence(self, pop, recombination_rates):
        """
        Implements the MAGIC breeding scheme of breeding single individuals
        in pairs determined by the offspring of the initial population. The
        initial population is given by generate_f_one.
        :param pop:
        :type pop:
        :param recombination_rates:
        :type recombination_rates:
        :return:
        :rtype:
        """
        while pop.numSubPop() > 1:
            new_parents = list(pop.indInfo('ind_id'))
            new_parent_id_pairs = [(pid, pid + 1) for pid in new_parents[::2]]

            if len(new_parent_id_pairs) % 2 != 0 and \
                            len(new_parent_id_pairs) != 1:
                new_parent_id_pairs.append(random.choice(new_parent_id_pairs))

            new_os_size = len(new_parent_id_pairs)

            new_founder_chooser = breed.PairwiseIDChooser(new_parent_id_pairs)

            pop.evolve(
                preOps=[
                    sim.PyEval(r'"Generation: %d\t" % gen',
                               ),
                    sim.Stat(popSize=True, numOfMales=True),
                    sim.PyEval(r'"popSize: %d\n" % popSize',
                               ),
                ],
                matingScheme=sim.HomoMating(
                    sim.PyParentsChooser(new_founder_chooser.by_id_pairs),
                    sim.OffspringGenerator(ops=[
                        sim.IdTagger(), sim.ParentsTagger(),
                        sim.PedigreeTagger(),
                        sim.Recombinator(rates=recombination_rates)],
                        numOffspring=1),
                    subPopSize=new_os_size,
                ),
                gen=1,
            )

    def expand_by_selfing(self, pop, recombination_rates):
        """
        Specific for plant populations capable of selfing.
        Creates an F2 subpopulations generation by selfing the individuals of
        'pop'. Works on a population with one or more subpopulations.
        :param pop:
        """
        # self.odd_to_even(pop)
        num_sub_pops = pop.numSubPop()
        progeny_per_individual = int(self.operating_population_size / 2)
        return pop.evolve(
            preOps=[
                sim.MergeSubPops(),
                sim.PyEval(r'"Generation: %d\n" % gen'),
                sim.SplitSubPops(sizes=[1] * num_sub_pops, randomize=False),
            ],
            matingScheme=sim.SelfMating(subPopSize=[progeny_per_individual] * num_sub_pops,
                                        numOffspring=progeny_per_individual,
                                        ops=[
                                            sim.Recombinator(
                                                rates=recombination_rates),
                                            sim.IdTagger(),
                                            sim.PedigreeTagger()],
                                        ),
            gen=1,
        )

    def interim_random_mating(self, pop, recombination_rates):
        """
        Randomly mates 'pop' for 'gens_of_random_mating' generations to further recombine founder genomes and dissolve
        population structure.
        :param pop: Founder population after mate_and_merge procedure
        :return: Population ready to be subjected to selection
        """
        print("Initiating interim random mating for {} generations.".format(
            self.generations_of_random_mating))
        pop.evolve(
            preOps=[
                sim.PyEval(r'"Generation: %d\n" % gen'),
            ],
            matingScheme=sim.RandomMating(
                subPopSize=self.operating_population_size,
                ops=[sim.IdTagger(), sim.PedigreeTagger(),
                     sim.Recombinator(
                         rates=recombination_rates)]),
            gen=self.generations_of_random_mating,
        )

    def restructure_offspring(self, pop, offspring_per_subpop, number_subpops):
        """
        Rearranges offspring after the F_1 mating scenario. F_1 is merged into
        a single population. This function splits single aggregate population into
        uniformly sized sub-populations to easily choose mating pairs.

        """

#        if type(offspring_per_subpop) != list:
#            offspring_per_subpop = [offspring_per_subpop]
        pop.splitSubPop(0, [offspring_per_subpop] * number_subpops)
        subpop_list = list(range(pop.numSubPop()))

        breeding_groups = []
        for pair in zip(subpop_list[0::2], subpop_list[1::2]):
            first_maters = random.sample(pop.indInfo('ind_id', pair[0]), offspring_per_subpop)
            second_maters = random.sample(pop.indInfo('ind_id', pair[1]), offspring_per_subpop)
            breeding_groups.append([first_maters, second_maters])
        breeding_array = np.array(breeding_groups)

        return breeding_array

    def recurrent_truncation_selection(self, pop, meta_pop, qtl, aes,
                                       recombination_rates, sampling_generations):
        """
        Sets up and runs recurrent selection for a number of generations for a
        single replicate population. Samples individuals at specified
        intervals to make a ``meta_pop``.

        :param pop: Population which undergoes selection.
        :param meta_pop: Population into which sampled individuals are
        deposited
        :param qtl: List of loci to which allele effects have been assigned
        :param aes: Dictionary of allele effects
        """

        pop.dvars().gen = 0
        meta_pop.dvars().gen = 0

        sizes = [self.individuals_per_breeding_subpop] \
                * self.number_of_breeding_subpops + \
                [self.number_of_nonbreeding_individuals]
        offspring_pops = [self.offspring_per_breeding_subpop] \
                         * self.number_of_breeding_subpops + [0]

        assert len(sizes) == len(offspring_pops), "Number of parental " \
                                                  "subpopulations must equal " \
                                                  "the number of offspring " \
                                                  "subpopulations"



        pc = breed.HalfSibBulkBalanceChooser(
            self.individuals_per_breeding_subpop, self.offspring_per_female)

        pop.evolve(
            initOps=[
                sim.InitInfo(0, infoFields=['generation']),
                operators.GenoAdditive(qtl, aes),
                operators.CalculateErrorVariance(self.heritability),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved),
                operators.MetaPopulation(meta_pop,
                                         self.meta_pop_sample_sizes),
                sim.PyEval(r'"Initial: Sampled %d individuals from generation '
                           r'%d Replicate: %d.\n" % (ss, gen_sampled_from, '
                           r'rep)'),
                operators.Sorter('p'),
                sim.SplitSubPops(sizes=[self.number_of_breeding_individuals,
                                        self.number_of_nonbreeding_individuals],
                                 randomize=False),
                sim.MergeSubPops(),
                operators.Sorter('p'),
            ],
            preOps=[
                sim.PyEval(r'"Generation: %d\n" % gen'),
                operators.GenoAdditive(qtl, aes, begin=1),
                sim.InfoExec('generation=gen'),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved, begin=1),
                operators.MetaPopulation(meta_pop,
                                         self.meta_pop_sample_sizes,
                                         at=sampling_generations),
                operators.Sorter('p'),
                sim.SplitSubPops(sizes=sizes, randomize=False),
            ],
            matingScheme=sim.HomoMating(
                sim.PyParentsChooser(pc.recursive_pairwise_parent_chooser),
                sim.OffspringGenerator(
                    ops=[sim.IdTagger(), sim.PedigreeTagger(),
                         sim.Recombinator(
                             rates=recombination_rates)],
                    numOffspring=1),
                subPopSize=offspring_pops,
                subPops=list(range(1, self.number_of_breeding_subpops, 1))
            ),
            postOps=[
            sim.MergeSubPops(),
                operators.DiscardRandomOffspring(self.number_of_offspring_discarded),
            ],
            finalOps=[
                sim.InfoExec('generation=gen'),
                operators.GenoAdditive(qtl, aes),
                operators.PhenotypeCalculator(self.proportion_of_individuals_saved),
                operators.MetaPopulation(meta_pop, self.meta_pop_sample_sizes),
                sim.PyEval(
                    r'"Final: Sampled %d individuals from generation %d\n" '
                    r'% (ss, gen_sampled_from)'),
                operators.Sorter('p'),
            ],
            gen=self.generations_of_selection)

    def replicate_random_mating(self, multi_pop, meta_sample_library, qtl,
                                allele_effects, recombination_rates):
        """
        Runs recurrent truncation selection on a multi-replicate population.

        :param multi_pop: Simulator object of full-sized population
        :param meta_sample_library: Simulator object of meta-populations
        :param qtl: Loci whose alleles have effects
        :param allele_effects: Allele effect container
        :param recombination_rates: Probabilities for recombination at each locus
        """

        for pop_rep in multi_pop.populations():
            pop_rep.dvars().gen = 0

        sizes = [self.individuals_per_breeding_subpop] \
                * self.number_of_breeding_subpops + \
                [self.number_of_nonbreeding_individuals]
        offspring_pops = [self.offspring_per_breeding_subpop] \
                         * self.number_of_breeding_subpops + [0]

        assert len(sizes) == len(offspring_pops), "Number of parental " \
                                                  "subpopulations must equal " \
                                                  "the number of offspring " \
                                                  "subpopulations"

        sampling_generations = [i for i in range(2, self.generations_of_random_mating,
                                                 2)]
        multi_pop.evolve(
            initOps=[
                sim.InitInfo(0, infoFields=['generation']),
                sim.InfoExec('replicate=rep'),
                operators.GenoAdditiveArray(qtl, allele_effects),
                operators.CalculateErrorVariance(self.heritability),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved),
                operators.ReplicateMetaPopulation(meta_sample_library,
                                                  self.meta_pop_sample_sizes),
                sim.PyEval(r'"Initial: Sampled %d individuals from generation '
                           r'%d Replicate: %d.\n" % (ss, gen_sampled_from, '
                           r'rep)'),
            ],
            preOps=[
                sim.PyEval(r'"Generation: %d\n" % gen'),
                operators.GenoAdditiveArray(qtl, allele_effects, begin=1),
                sim.InfoExec('generation=gen'),
                sim.InfoExec('replicate=rep'),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved, begin=1),
                operators.ReplicateMetaPopulation(meta_sample_library,
                                                  self.meta_pop_sample_sizes,
                                                  at=sampling_generations),
            ],
            matingScheme=sim.RandomMating(
                    ops=[sim.IdTagger(), sim.PedigreeTagger(),
                         sim.Recombinator(rates=recombination_rates)]
            ),
            finalOps=[
                sim.InfoExec('generation=gen'),
                sim.InfoExec('replicate=rep'),
                operators.GenoAdditiveArray(qtl, allele_effects),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved),
                operators.ReplicateMetaPopulation(meta_sample_library,
                                                  self.meta_pop_sample_sizes),
                sim.PyEval(
                    r'"Final: Sampled %d individuals from generation %d\n" '
                    r'% (ss, gen_sampled_from)'),
            ],
            gen=self.generations_of_random_mating)



class Truncation(object):
    """
    ``Truncation`` is a class which encapsulates all parameters and
    functions to perform recurrent truncation selection on a quantitative
    trait. The trait is assumed to have a simple additive basis so all
    phenotypes are calculated by adding contribution of :math:`n` loci plus error.
    """

    def __init__(self, generations_of_selection=1,
                 operating_population_size=2000,
                 proportion_of_individuals_saved=0.05,
                 overshoot_as_proportion=0.50,
                 individuals_per_breeding_subpop=5,
                 heritability=0.7,
                 meta_pop_sample_sizes=100,
                 ):
        self.generations_of_selection = generations_of_selection
        self.operating_population_size = operating_population_size
        self.proportion_of_individuals_saved = proportion_of_individuals_saved
        self.overshoot_as_proportion = overshoot_as_proportion
        self.individuals_per_breeding_subpop = individuals_per_breeding_subpop
        self.heritability = heritability
        self.meta_pop_sample_sizes = meta_pop_sample_sizes

        self.breeding_parameters = col.OrderedDict()
        self.number_of_breeding_individuals = int(
            proportion_of_individuals_saved * operating_population_size)
        self.breeding_parameters['number_of_breeding_individuals'] = \
            self.number_of_breeding_individuals
        self.number_of_breeding_subpops = \
            int(self.number_of_breeding_individuals /\
                self.individuals_per_breeding_subpop)
        self.breeding_parameters['number_of_breeding_subpops'] = \
            self.number_of_breeding_subpops
        self.total_number_of_offspring_per_generation = \
            int(operating_population_size * (1 + self.overshoot_as_proportion))
        self.breeding_parameters['total_number_of_offspring_per_generation'] = \
            self.total_number_of_offspring_per_generation
        self.offspring_per_breeding_subpop = \
            int(self.total_number_of_offspring_per_generation/\
                self.number_of_breeding_subpops)
        self.breeding_parameters['offspring_per_breeding_subpop'] = \
            self.offspring_per_breeding_subpop
        self.offspring_per_female = \
            int(self.offspring_per_breeding_subpop /
                self.individuals_per_breeding_subpop)
        self.breeding_parameters['offspring_per_female'] = \
            self.offspring_per_female
        self.number_of_nonbreeding_individuals = \
            int(self.operating_population_size -
                self.number_of_breeding_individuals)
        self.breeding_parameters['number_of_nonbreeding_individuals'] = \
            self.number_of_nonbreeding_individuals
        self.number_of_offspring_discarded = int(
            self.overshoot_as_proportion * self.operating_population_size)
        self.breeding_parameters['number_of_offspring_discarded'] = \
            self.number_of_offspring_discarded

    def __str__(self):
        trunc_info = 'Type: Recurrent Selection\n' +\
                    '**************************\n' +\
                    'Generations of Selection: {}\n'.format(self.generations_of_selection) +\
                    'Operating Population Size: {}\n'.format(
                        self.operating_population_size) +\
                    'Proportion of Individuals Saved: {}\n'.format(
                        self.proportion_of_individuals_saved)

        return trunc_info

    def recombinatorial_convergence(self, pop, recombination_rates):
        """
        Implements the MAGIC breeding scheme of breeding single individuals
        in pairs determined by the offspring of the initial population. The
        initial population is given by generate_f_one.
        :param pop:
        :type pop:
        :param recombination_rates:
        :type recombination_rates:
        :return:
        :rtype:
        """
        while pop.numSubPop() > 1:
            new_parents = list(pop.indInfo('ind_id'))
            new_parent_id_pairs = [(pid, pid + 1) for pid in new_parents[::2]]

            if len(new_parent_id_pairs) % 2 != 0 and \
                            len(new_parent_id_pairs) != 1:
                new_parent_id_pairs.append(random.choice(new_parent_id_pairs))

            new_os_size = len(new_parent_id_pairs)

            new_founder_chooser = breed.PairwiseIDChooser(new_parent_id_pairs)

            pop.evolve(
                preOps=[
                    sim.PyEval(r'"Generation: %d\t" % gen',
                               ),
                    sim.Stat(popSize=True, numOfMales=True),
                    sim.PyEval(r'"popSize: %d\n" % popSize',
                               ),
                ],
                matingScheme=sim.HomoMating(
                    sim.PyParentsChooser(new_founder_chooser.by_id_pairs),
                    sim.OffspringGenerator(ops=[
                        sim.IdTagger(), sim.ParentsTagger(),
                        sim.PedigreeTagger(),
                        sim.Recombinator(rates=recombination_rates)],
                        numOffspring=1),
                    subPopSize=new_os_size,
                ),
                gen=1,
            )

    def expand_by_selfing(self, pop, recombination_rates):
        """
        Specific for plant populations capable of selfing.
        Creates an F2 subpopulations generation by selfing the individuals of
        'pop'. Works on a population with one or more subpopulations.
        :param pop:
        """
        # self.odd_to_even(pop)
        num_sub_pops = pop.numSubPop()
        progeny_per_individual = int(self.operating_population_size / 2)
        return pop.evolve(
            preOps=[
                sim.MergeSubPops(),
                sim.PyEval(r'"Generation: %d\n" % gen'),
                sim.SplitSubPops(sizes=[1] * num_sub_pops, randomize=False),
            ],
            matingScheme=sim.SelfMating(subPopSize=[progeny_per_individual] * num_sub_pops,
                                        numOffspring=progeny_per_individual,
                                        ops=[
                                            sim.Recombinator(
                                                rates=recombination_rates),
                                            sim.IdTagger(),
                                            sim.PedigreeTagger()],
                                        ),
            gen=1,
        )

    def interim_random_mating(self, pop, recombination_rates):
        """
        Randomly mates 'pop' for 'gens_of_random_mating' generations to further recombine founder genomes and dissolve
        population structure.
        :param pop: Founder population after mate_and_merge procedure
        :return: Population ready to be subjected to selection
        """
        print("Initiating interim random mating for {} generations.".format(
            self.generations_of_random_mating))
        pop.evolve(
            preOps=[
                sim.PyEval(r'"Generation: %d\n" % gen'),
            ],
            matingScheme=sim.RandomMating(
                subPopSize=self.operating_population_size,
                ops=[sim.IdTagger(), sim.PedigreeTagger(),
                     sim.Recombinator(
                         rates=recombination_rates)]),
            gen=self.generations_of_random_mating,
        )

    def restructure_offspring(self, pop, offspring_per_subpop, number_subpops):
        """
        Rearranges offspring after the F_1 mating scenario. F_1 is merged into
        a single population. This function splits single aggregate population into
        uniformly sized sub-populations to easily choose mating pairs.

        """

#        if type(offspring_per_subpop) != list:
#            offspring_per_subpop = [offspring_per_subpop]
        pop.splitSubPop(0, [offspring_per_subpop] * number_subpops)
        subpop_list = list(range(pop.numSubPop()))

        breeding_groups = []
        for pair in zip(subpop_list[0::2], subpop_list[1::2]):
            first_maters = random.sample(pop.indInfo('ind_id', pair[0]), offspring_per_subpop)
            second_maters = random.sample(pop.indInfo('ind_id', pair[1]), offspring_per_subpop)
            breeding_groups.append([first_maters, second_maters])
        breeding_array = np.array(breeding_groups)

        return breeding_array

    def recurrent_truncation_selection(self, pop, meta_pop, qtl, aes,
                                       recombination_rates, sampling_generations):
        """
        Sets up and runs recurrent selection for a number of generations for a
        single replicate population. Samples individuals at specified
        intervals to make a ``meta_pop``.

        :param pop: Population which undergoes selection.
        :param meta_pop: Population into which sampled individuals are
        deposited
        :param qtl: List of loci to which allele effects have been assigned
        :param aes: Dictionary of allele effects
        """

        pop.dvars().gen = 0
        meta_pop.dvars().gen = 0

        sizes = [self.individuals_per_breeding_subpop] \
                * self.number_of_breeding_subpops + \
                [self.number_of_nonbreeding_individuals]
        offspring_pops = [self.offspring_per_breeding_subpop] \
                         * self.number_of_breeding_subpops + [0]

        assert len(sizes) == len(offspring_pops), "Number of parental " \
                                                  "subpopulations must equal " \
                                                  "the number of offspring " \
                                                  "subpopulations"



        pc = breed.HalfSibBulkBalanceChooser(
            self.individuals_per_breeding_subpop, self.offspring_per_female)

        pop.evolve(
            initOps=[
                sim.InitInfo(0, infoFields=['generation']),
                operators.GenoAdditive(qtl, aes),
                operators.CalculateErrorVariance(self.heritability),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved),
                operators.MetaPopulation(meta_pop,
                                         self.meta_pop_sample_sizes),
                sim.PyEval(r'"Initial: Sampled %d individuals from generation '
                           r'%d Replicate: %d.\n" % (ss, gen_sampled_from, '
                           r'rep)'),
                operators.Sorter('p'),
                sim.SplitSubPops(sizes=[self.number_of_breeding_individuals,
                                        self.number_of_nonbreeding_individuals],
                                 randomize=False),
                sim.MergeSubPops(),
                operators.Sorter('p'),
            ],
            preOps=[
                sim.PyEval(r'"Generation: %d\n" % gen'),
                operators.GenoAdditive(qtl, aes, begin=1),
                sim.InfoExec('generation=gen'),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved, begin=1),
                operators.MetaPopulation(meta_pop,
                                         self.meta_pop_sample_sizes,
                                         at=sampling_generations),
                operators.Sorter('p'),
                sim.SplitSubPops(sizes=sizes, randomize=False),
            ],
            matingScheme=sim.HomoMating(
                sim.PyParentsChooser(pc.recursive_pairwise_parent_chooser),
                sim.OffspringGenerator(
                    ops=[sim.IdTagger(), sim.PedigreeTagger(),
                         sim.Recombinator(
                             rates=recombination_rates)],
                    numOffspring=1),
                subPopSize=offspring_pops,
                subPops=list(range(1, self.number_of_breeding_subpops, 1))
            ),
            postOps=[
            sim.MergeSubPops(),
                operators.DiscardRandomOffspring(self.number_of_offspring_discarded),
            ],
            finalOps=[
                sim.InfoExec('generation=gen'),
                operators.GenoAdditive(qtl, aes),
                operators.PhenotypeCalculator(self.proportion_of_individuals_saved),
                operators.MetaPopulation(meta_pop, self.meta_pop_sample_sizes),
                sim.PyEval(
                    r'"Final: Sampled %d individuals from generation %d\n" '
                    r'% (ss, gen_sampled_from)'),
                operators.Sorter('p'),
            ],
            gen=self.generations_of_selection)

    def replicate_selection(self, multi_pop, meta_sample_library, qtl, allele_effects,
                            recombination_rates):
        """
        Runs recurrent truncation selection on a multi-replicate population.

        :param multi_pop: Simulator object of full-sized population
        :param meta_sample_library: Simulator object of meta-populations
        :param qtl: Loci whose alleles have effects
        :param allele_effects: Allele effect container
        :param recombination_rates: Probabilities for recombination at each locus
        """

        for pop_rep in multi_pop.populations():
            pop_rep.dvars().gen = 0

        sizes = [self.individuals_per_breeding_subpop] \
                * self.number_of_breeding_subpops + \
                [self.number_of_nonbreeding_individuals]
        offspring_pops = [self.offspring_per_breeding_subpop] \
                         * self.number_of_breeding_subpops + [0]

        assert len(sizes) == len(offspring_pops), "Number of parental " \
                                                  "subpopulations must equal " \
                                                  "the number of offspring " \
                                                  "subpopulations"

        sampling_generations = [i for i in range(2, self.generations_of_selection,
                                                 2)]

        pc = breed.HalfSibBulkBalanceChooser(
            self.individuals_per_breeding_subpop, self.offspring_per_female)

        multi_pop.evolve(
            initOps=[
                sim.InitInfo(0, infoFields=['generation']),
                sim.InfoExec('replicate=rep'),
                operators.GenoAdditiveArray(qtl, allele_effects),
                operators.CalculateErrorVariance(self.heritability),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved),
                operators.ReplicateMetaPopulation(meta_sample_library,
                                                  self.meta_pop_sample_sizes),
                sim.PyEval(r'"Initial: Sampled %d individuals from generation '
                           r'%d Replicate: %d.\n" % (ss, gen_sampled_from, '
                           r'rep)'),
                operators.Sorter('p'),
            ],
            preOps=[
                sim.PyEval(r'"Generation: %d\n" % gen'),
                operators.GenoAdditiveArray(qtl, allele_effects, begin=1),
                sim.InfoExec('generation=gen'),
                sim.InfoExec('replicate=rep'),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved, begin=1),
                operators.ReplicateMetaPopulation(meta_sample_library,
                                                  self.meta_pop_sample_sizes,
                                                  at=sampling_generations),
                operators.Sorter('p'),
                sim.SplitSubPops(sizes=sizes, randomize=False),
            ],
            matingScheme=sim.HomoMating(
                sim.PyParentsChooser(pc.recursive_pairwise_parent_chooser),
                sim.OffspringGenerator(
                    ops=[sim.IdTagger(), sim.PedigreeTagger(),
                         sim.Recombinator(
                             rates=recombination_rates)],
                    numOffspring=1),
                subPopSize=offspring_pops,
                subPops=list(range(1, self.number_of_breeding_subpops, 1))
            ),
            postOps=[
                sim.MergeSubPops(),
                operators.DiscardRandomOffspring(
                    self.number_of_offspring_discarded),
            ],
            finalOps=[
                sim.InfoExec('generation=gen'),
                operators.GenoAdditiveArray(qtl, allele_effects),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved),
                operators.ReplicateMetaPopulation(meta_sample_library,
                                                  self.meta_pop_sample_sizes),
                sim.PyEval(
                    r'"Final: Sampled %d individuals from generation %d\n" '
                    r'% (ss, gen_sampled_from)'),
                operators.Sorter('p'),
            ],
            gen=self.generations_of_selection)


class Drift(object):
    """
    Class which has functions similar to :class Truncation: but simulates
    conditions of genetic drift instead of recurrent truncation selection.
    """

    def __init__(self, generations_of_drift=1,
                 operating_population_size=2000,
                 proportion_of_individuals_saved=0.05,
                 overshoot_as_proportion=0.50,
                 individuals_per_breeding_subpop=5,
                 heritability=0.7,
                 meta_pop_sample_sizes=100):
        self.generations_of_drift = generations_of_drift
        self.operating_population_size = operating_population_size
        self.proportion_of_individuals_saved = proportion_of_individuals_saved
        self.overshoot_as_proportion = overshoot_as_proportion
        self.individuals_per_breeding_subpop = individuals_per_breeding_subpop
        self.heritability = heritability
        self.meta_pop_sample_sizes = meta_pop_sample_sizes

        self.breeding_parameters = col.OrderedDict()
        self.number_of_breeding_individuals = int(
            proportion_of_individuals_saved * operating_population_size)
        self.breeding_parameters['number_of_breeding_individuals'] = \
            self.number_of_breeding_individuals
        self.number_of_breeding_subpops = \
            int(
                self.number_of_breeding_individuals / self.individuals_per_breeding_subpop)
        self.breeding_parameters['number_of_breeding_subpops'] = \
            self.number_of_breeding_subpops
        self.total_number_of_offspring_per_generation = \
            int(operating_population_size * (1 + self.overshoot_as_proportion))
        self.breeding_parameters['total_number_of_offspring_per_generation'] = \
            self.total_number_of_offspring_per_generation
        self.offspring_per_breeding_subpop = \
            int(self.total_number_of_offspring_per_generation
                / self.number_of_breeding_subpops)
        self.breeding_parameters['offspring_per_breeding_subpop'] = \
            self.offspring_per_breeding_subpop
        self.offspring_per_female = \
            int(self.offspring_per_breeding_subpop /
                self.individuals_per_breeding_subpop)
        self.breeding_parameters['offspring_per_female'] = \
            self.offspring_per_female
        self.number_of_nonbreeding_individuals = \
            int(self.operating_population_size -
                self.number_of_breeding_individuals)
        self.breeding_parameters['number_of_nonbreeding_individuals'] = \
            self.number_of_nonbreeding_individuals
        self.number_of_offspring_discarded = int(
            self.overshoot_as_proportion * self.operating_population_size)
        self.breeding_parameters['number_of_offspring_discarded'] = \
            self.number_of_offspring_discarded


    def recurrent_drift(self, pop, meta_pop, qtl, aes,
                                  recombination_rates):
        """
        Sets up and runs recurrent selection for a number of generations for a
        single replicate population. Samples individuals at specified
        intervals to make a ``meta_pop``.
        :param pop: Population which undergoes selection.
        :param meta_pop: Population into which sampled individuals are
        deposited
        :param qtl: List of loci to which allele effects have been assigned
        :param aes: Dictionary of allele effects
        """
        pop.dvars().gen = 0
        meta_pop.dvars().gen = 0

        sizes = [self.individuals_per_breeding_subpop] \
                * self.number_of_breeding_subpops + \
                [self.number_of_nonbreeding_individuals]
        offspring_pops = [self.offspring_per_breeding_subpop] \
                         * self.number_of_breeding_subpops + [0]

        assert len(sizes) == len(offspring_pops), "Number of parental " \
                                                  "subpopulations must equal " \
                                                  "the number of offspring " \
                                                  "subpopulations"

        sampling_generations = [i for i in range(2,
                                                 self.generations_of_drift, 2)]

        pc = breed.HalfSibBulkBalanceChooser(
            self.individuals_per_breeding_subpop, self.offspring_per_female)

        pop.evolve(
            initOps=[
                sim.InitInfo(0, infoFields=['generation']),
                operators.GenoAdditiveArray(qtl, aes),
                operators.CalculateErrorVariance(self.heritability),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved),
                operators.MetaPopulation(meta_pop,
                                         self.meta_pop_sample_sizes),
                sim.PyEval(r'"Initial: Sampled %d individuals from generation '
                           r'%d Replicate: %d.\n" % (ss, gen_sampled_from, '
                           r'rep)'),
            ],
            preOps=[
                sim.PyEval(r'"Generation: %d\n" % gen'),
                operators.GenoAdditiveArray(qtl, aes, begin=1),
                sim.InfoExec('generation=gen'),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved, begin=1),
                operators.MetaPopulation(meta_pop,
                                         self.meta_pop_sample_sizes,
                                         at=sampling_generations),
                sim.SplitSubPops(sizes=sizes, randomize=True),
            ],
            matingScheme=sim.HomoMating(
                sim.PyParentsChooser(pc.recursive_pairwise_parent_chooser),
                sim.OffspringGenerator(
                    ops=[sim.IdTagger(), sim.PedigreeTagger(),
                         sim.Recombinator(
                             rates=recombination_rates)],
                    numOffspring=1),
                subPopSize=offspring_pops,
                subPops=list(range(1, self.number_of_breeding_subpops, 1))
            ),
            postOps=[
                sim.MergeSubPops(),
                operators.DiscardRandomOffspring(
                    self.number_of_offspring_discarded),
            ],
            finalOps=[
                sim.InfoExec('generation=gen'),
                operators.GenoAdditive(qtl, aes),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved),
                operators.MetaPopulation(meta_pop, self.meta_pop_sample_sizes),
                sim.PyEval(
                    r'"Final: Sampled %d individuals from generation %d\n" '
                    r'% (ss, gen_sampled_from)'),
            ],
            gen=self.generations_of_drift)


    def replicate_recurrent_drift(self, multi_pop, meta_sample_library,
                                  qtl, allele_effects, recombination_rates):
        """

        :param multi_pop:
        :param meta_pop_sample_library:
        :param qtl:
        :param allele_effects:
        :param recombination_rates:
        :return:
        """

        for pop in multi_pop.populations():
            pop.dvars().gen = 0

        sizes = [self.individuals_per_breeding_subpop] \
                * self.number_of_breeding_subpops + \
                [self.number_of_nonbreeding_individuals]


        offspring_pops = [self.offspring_per_breeding_subpop] \
                 * self.number_of_breeding_subpops + [0]

        assert len(sizes) == len(offspring_pops), "Number of parental " \
                                          "subpopulations must equal " \
                                          "the number of offspring " \
                                          "subpopulations"

        sampling_generations = [i for i in range(2, self.generations_of_drift,
                                         2)]

        pc = breed.HalfSibBulkBalanceChooser(
            self.individuals_per_breeding_subpop, self.offspring_per_female)

        multi_pop.evolve(
            initOps=[
                sim.InitInfo(0, infoFields=['generation']),
                sim.InfoExec('replicate=rep'),
                operators.GenoAdditiveArray(qtl, allele_effects),
                operators.CalculateErrorVariance(self.heritability),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved),
                operators.ReplicateMetaPopulation(meta_sample_library,
                                                  self.meta_pop_sample_sizes),
                sim.PyEval(r'"Initial: Sampled %d individuals from generation '
                           r'%d Replicate: %d.\n" % (ss, gen_sampled_from, '
                           r'rep)'),
            ],
            preOps=[
                sim.PyEval(r'"Generation: %d\n" % gen'),
                operators.GenoAdditiveArray(qtl, allele_effects, begin=1),
                sim.InfoExec('generation=gen'),
                sim.InfoExec('replicate=rep'),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved, begin=1),
                operators.ReplicateMetaPopulation(meta_sample_library,
                                                  self.meta_pop_sample_sizes,
                                                  at=sampling_generations),
                sim.SplitSubPops(sizes=sizes, randomize=False),
            ],
            matingScheme=sim.HomoMating(
                sim.PyParentsChooser(pc.recursive_pairwise_parent_chooser),
                sim.OffspringGenerator(
                    ops=[sim.IdTagger(), sim.PedigreeTagger(),
                         sim.Recombinator(rates=recombination_rates)],
                    numOffspring=1),
                    subPopSize=offspring_pops,
                    subPops=list(range(1, self.number_of_breeding_subpops, 1))
            ),
            postOps=[
                sim.MergeSubPops(),
                operators.DiscardRandomOffspring(
                    self.number_of_offspring_discarded),
            ],
            finalOps=[
                sim.InfoExec('generation=gen'),
                sim.InfoExec('replicate=rep'),
                operators.GenoAdditiveArray(qtl, allele_effects),
                operators.PhenotypeCalculator(
                    self.proportion_of_individuals_saved),
                operators.ReplicateMetaPopulation(meta_sample_library,
                                                  self.meta_pop_sample_sizes),
                sim.PyEval(
                    r'"Final: Sampled %d individuals from generation %d\n" '
                    r'% (ss, gen_sampled_from)'),
            ],
            gen=self.generations_of_drift)
