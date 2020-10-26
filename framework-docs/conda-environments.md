# Setting up and Maintaining your Conda Environment (Reproducibly)

The `reproallthethings` repo is set up with template code to make managing your conda environments easy and reproducible. Not only will future you appreciate this, but everyone else who tries to run your code will thank you.

If you haven't yet, get your initial environment set up.

### Quickstart Instructions
**WARNING FOR EXISTING CONDA USERS**: If you have conda-forge listed as a channel in your `.condarc` (or any other channels other than defaults), remove it during the course of the project. Even better, don't use a `.condarc` for managing channels, as it overrides the `environment.yml` instructions and makes things less reproducible. Make the changes to the `environment.yml` file if necessary. We've had some conda-forge related issues with version conflicts.

We also recommend [setting your channel priority to 'strict'](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-channels.html) to reduce package incompatibility problems. This will be default in future conda releases, but it is being rolled out gently.

* Make note of the path to your conda binary:
```
   $ which conda
   ~/miniconda3/bin/conda
```
* ensure your `CONDA_EXE` environment variable is set to this value (or edit `Makefile.include` directly)
```
    export CONDA_EXE=~/miniconda3/bin/conda
```
* Create and switch to the virtual environment:
```
cd reproallthethings
make create_environment
conda activate reproallthethings
make update_environment
```
Note: you need to run `make update_environment` for the `src` module to install correctly.

From here on, to use the environment, simply `conda activate reproallthethings` and `conda deactivate` to go back to the base environment.

### Further Instructions

#### Updating your environment
The `make` commands, `make create_environment` and `make update_environment` are wrappers that allow you to easily manage your environment using the `environment.yml` file. If you want to make changes to your environment, do so by editing the `environment.yml` file and then running `make update_environment`.

If you ever forget which make command to run, you can run `make` and it will list a magic menu of which make commands are available.

Your `environment.yml` file will look something like this:
```
name: reproallthethings
  - pip
  - pip:
    - -e .  # conda >= 4.4 only
    - python-dotenv>=0.5.1
    - nbval
    - nbdime
    - umap-learn
    - gdown
  - setuptools
  - wheel
  - git>=2.5  # for git worktree template updating
  - sphinx
  - bokeh
  - click
  - colorcet
  - coverage
  - coveralls
  - datashader
  - holoviews
  - matplotlib
  - jupyter
...
```
To add any package available from conda, add it to the end of the list. If you have a PYPI dependency that's not avaible via conda, add it to the list of pip installable dependencies under `  - pip:`.

You can include any github.com python-based project in the `pip` section via `git+https://github.com/<my_git_handle>/<package>`.

In particular, if you're working off of a fork or a work in progress branch of a repo in github.com (say, your personal version of <package>), you can change `git+https://github.com/<my_git_handle>/<package>` to

* `git+https://github.com/<my_git_handle>/<package>.git` to point to the master branch of your fork and
* `git+https://github.com/<my_git_handle>/<package>.git@<my branch>` to point to a specific branch.

Once you're done your edits, run `make update_environment` and voila, you're updated.

To share your updated environment, check in your `environment.yml` file. (More on this in [Sharing your Work](sharing-your-work.md))


#### Lock files
Now, we'll admit that this workflow isn't perfectly reproducible in the sense that conda still has to resolve versions from the `environment.yml`. To make it more reproducible, running either `make create_environment` or `make update_environment` will generate an `environment.{$ARCH}.lock.yml` (e.g. `environment.i386.lock.yml`). This file keeps a record of the exact environment that is currently installed in your conda environment `reproallthethings`. If you ever need to reproduce an environment exactly, you can install from the `.lock.yml` file. (Note: These are architecture dependent).

#### Using your conda environment in a jupyter notebook
If you make a new notebook, select the `reproallthethings` environment from within the notebook. If you are somehow in another kernel, select **Kernel -> Change kernel -> Python[conda env:reproallthethings]**. If you don't seem to have that option, make sure that you ran `jupyter notebooks` with the `reproallthethings` conda environment enabled, and that `which jupyter` points to the correct (`reproallthethings`) version of jupyter.

If you want your environment changes (or `src` module edits) to be immediately available in your running notebooks, make sure to run a notebook cell containing
```
%load_ext autoreload
%autoreload 2
```

More on notebooks can be found in [Using Notebooks for Analysis](notebooks.md).

### Nuke it from orbit
Sometimes, you need to be sure. Making things reproducible means that blowing things away completely and rebuilding from scratch is always an option. To do so:
```
conda deactivate
make delete_environment
make create_environment
conda activate reproallthethings
touch environment.yml
make update_envrionment
```
and then proceed with managing your environment as above.

### Quick References

* [README](../README.md)
* [Setting up and Maintaining your Conda Environment Reproducibly](conda-environments.md)
* [Getting and Using Datasets](datasets.md)
* [Using Notebooks for Analysis](notebooks.md)
* [Sharing your Work](sharing-your-work.md)
* [Troubleshooting Guide](troubleshooting.md)
