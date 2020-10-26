Here's our suggestion for a reliable git workflow that works well in small team settings using [Easydata][cookiecutter-easydata].

**Note**: These instructions assume you are using SSH keys (and not HTTPS authentication) with github.com. If you haven't set up SSH access to your repo host, see [Configuring SSH Access to Github or Gitlab][git-ssh]. This also includes instructions for using more than one account with SSH keys.

[git-ssh]: https://github.com/hackalog/cookiecutter-easydata/wiki/Configuring-SSH-Access-to-Github-or-GitLab

## Git Configuration
### Create a Personal Fork

We strongly recommend you make all your edits on a personal fork of this repo. Here's how to create such a fork:

* On Github or Gitlab, press the Fork button in the top right corner.
* On Bitbucket, press the "+" icon on the left and choose **Fork this Repo**

### Local, `origin`, and `upstream`
Next, you should configure your git remotes so that `origin` refers to your personal github.com fork, and `upstream` refers to the repo you forked from

1. Clone your personal fork to your local machine
   ```git clone git@github.com:<your github handle>/reproallthethings.git```
1. Add the main source repo as a remote branch called `upstream` (to make syncing easier):

  ```cd reproallthethings
  git remote add upstream git@github.com:<upstream-repo>/reproallthethings.git```

To summarize:

* "local" refers to git checkout on your local machine (or JupyterHub instance). This is the one you work with most of the time.
* `upstream` refers to the shared Easydata repo; i.e. the **team repo**,
* `origin` refers to your **personal fork** of the shared Easydata repo on github.com.

### Work in Branches
To make life easiest, we recommend you do all your development **in branches**, and use your master branch **only** for tracking changes in the shared `upstream/master`. This combination makes it much easier not only to stay up to date with changes in the shared project repo, but also makes it easier to submit Pull/Merge Requests (PRs) against the upstream project repository should you want to share your code or data.

## The Easydata git workflow

We suggest you start each day by doing this:

### Where was I? What was I doing? Did I check it in?
Sometimes, you stop work without checking things back in to the repo.
Now, before you do any additional work, is the time to fix that.
```bash
git branch   # what branch am I on?
git status   # are there any files that need checking in?
git add -p   # accept or reject parts of the modified files
git commit -m "put your commit message here"
```

### Did I do any work elsewhere?
Did you make changes to your personal fork, but on a different machine? Make sure your local branch is up-to-date with your personal fork (`origin`):
```bash
git checkout master
git fetch origin --prune
git merge origin/master
```

### What happened upstream?
Did someone make changes to the `upstream` repo in your absense?
Let's fetch and merge those changes

```bash
git checkout master
git fetch upstream --prune
git merge upstream/master
git push origin master
make update_environment
```

### Update your local branches
Now that your `master` branch is up-to-date with both `origin` and `upstream`, you should use it to update your local working branches. If you are already developing in a branch called, e.g. `my_branch`, do this before writing any more code:

```bash
git checkout my_branch
git merge master
git push origin my_branch
```

### Start a new branch for the day's work
Create a clean working branch by doing a:
```bash
git checkout master
git checkout -b new_branch_name
```

### Clean up the old branches
Now that you're up-to-date, you can clean up any of your old branches that are fully merged (and hence, can be deleted.)
```bash
git branch --merged master
git branch -d <name_of_merged_branch>
```

Got any suggestions for improvements to this workflow? File an issue at
[cookiecutter-easydata].

[cookiecutter-easydata]: https://github.com/hackalog/cookiecutter-easydata/