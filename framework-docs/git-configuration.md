# Setting up git and Checking Out the Repo

**Note**: These instructions assume you are using SSH keys (and not HTTPS authentication) with github.com. If you haven't set up SSH access to your repo host, see [Configuring SSH Access to Github or Gitlab][git-ssh]. This also includes instructions for using more than one account with SSH keys.

[git-ssh]: https://github.com/hackalog/cookiecutter-easydata/wiki/Configuring-SSH-Access-to-Github-or-GitLab

## Git Configuration
When sharing a git repo with a small team, your code usually lives in at least 3 different places:

* "local" refers to any git checkout on a local machine (or JupyterHub instance). This is where you work most of the time.
* `upstream` refers to the shared Easydata repo on github.com; i.e. the **team repo**,
* `origin` refers to your **personal fork** of the shared Easydata repo. It also lives on github.com.

### Create a Personal Fork

We strongly recommend you make all your edits on a personal fork of this repo. Here's how to create such a fork:

* On Github or Gitlab, press the Fork button in the top right corner.
* On Bitbucket, press the "+" icon on the left and choose **Fork this Repo**

### Local, `origin`, and `upstream`
git calls `upstream` (the **team repo**), and `origin` (your **personal fork** of the team repo) "remote" branches. Here's how to create them.

Create a local git checkout by cloning your personal fork:
```bash
git clone git@github.com:<your_git_handle>/reproallthethings.git
```
Add the team (shared) repo as a remote branch named `upstream`:
```bash
  cd reproallthethings
  git remote add upstream git@github.com:<upstream-repo>/reproallthethings.git
```

You can verify that these branches are configured correctly by typing

```
>>> git remote -v
origin	git@github.com:<your_git_handle>/reproallthethings.git (fetch)
origin	git@github.com:<your_git_handle>/reproallthethings.git (push)
upstream	git@github.com:<upstream-repo>/reproallthethings.git (fetch)
upstream	git@github.com:<upstream-repo>/reproallthethings.git (push)
```

### Work in Branches
To make life easiest, we recommend you do all your development **in branches**, and use your master branch **only** for tracking changes in the shared `upstream/master`. This combination makes it much easier not only to stay up to date with changes in the shared project repo, but also makes it easier to submit Pull/Merge Requests (PRs) against the upstream project repository should you want to share your code or data.
