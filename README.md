Overview of SAEGUS
===================================

SAEGUS (Simulation and Evolution of Genomes Under Selection) is a Python
package which is built around the forward-time population genetics simulator
simuPOP. SAEGUS adds functions for modeling quantitative traits, customized
breeding schemes and handling data. SAEGUS only supports Python 3. This readme 
will show you how to get started with SAEGUS by creating a population 
from raw data.

Installing the Anaconda Distribution
================================================

Anaconda is a package manager and a Python distribution which ships with
popular Python packages used in scientific computing. The Anaconda distribution
must be installed in order to proceed with this readme. 
[Anaconda](https://conda.io/docs/user-guide/install/index.html)

Installing simuPOP and h5py
====================================================

simuPOP is very easy to install by using the conda package manager. Once
you have install Anaconda open a terminal and run:

```bash
conda install -c bpeng simupop
```

Anaconda page for simuPOP: [simuPOP Installation](https://anaconda.org/bpeng/simupop)

h5py is a Python package for hdf5 files. I am unsure if it ships by default
with the Anaconda distribution. To be sure you should run the install command
regardless.

```bash
conda install -c anaconda h5py
```

Installing SAEGUS
=============================================

After Anaconda, simuPOP and h5py have been installed we will install SAEGUS. I
caution you that I have not had anyone else attempt to install SAEGUS in a very
long time. You have been warned. A list of the steps:

+ Clone the rjwlab-scripts repository
+ Install saegus
+ Open a Python terminal, preferrably a Jupyter notebook
+ Follow walk through on creating a population from raw data

Clone the rjwlab-scripts repository
---------------------------------------------

Using HTTPS protocol:

```bash
git clone https://github.com/maizeatlas/rjwlab-scripts.git
```

Using SSH protocol

```bash
git clone git@github.com:maizeatlas/rjwlab-scripts.git
```

Alternatively if you already have the repository on your machine then use
`git pull` command to retrieve the most recent version of the repository. 
Navigate to the location of the repository on your machine and run:

```bash
git pull
```

Install saegus
-----------------------------

In the ``rjwlab-scripts`` directory navigate to the saegus_project/src/
directory. You should see: 

```bash
~/rjwlab-scripts/saegus_project/src$ ls
~/rjwlab-scripts/saegus_project/src$ build  data  docs  LICENSE  MANIFEST.in  README.rst  saegus  scripts  setup.py
```
Run the python setup.py install command to install the saegus package. You
should see something like this:

```bash
~/rjwlab-scripts/saegus_project/src$ python setup.py install
running install
running build
running build_py
running install_lib
```

Open a Jupyter Notebook (Formerly IPython Notebook)
-------------------------------------------------------------

In your terminal navigate to the ``saegus_project/docs/user_guide/`` directory.
This is where all the data files are located. In your terminal run:

```bash
jupyter notebook
```
A window in your browser will open. This is a much nicer environment to work
in than a plain Python interpreter. Especially with saegus' long function names.

Creating a Population from Raw Data
------------------------------------------------------------------

Open a new tab in your web browser and follow the walk through:
[saegus walkthrough](http://saegus-user-guide-docs.readthedocs.io/en/latest/population_from_raw_data.html)