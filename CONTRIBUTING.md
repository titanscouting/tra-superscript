# Contributing Guidelines

This project accept contributions via GitHub pull requests.
This document outlines some of the
conventions on development workflow, commit message formatting, contact points,
and other resources to make it easier to get your contribution accepted.

## Certificate of Origin

By contributing to this project, you agree to the [Developer Certificate of
Origin (DCO)](https://developercertificate.org/). This document was created by the Linux Kernel community and is a
simple statement that you, as a contributor, have the legal right to make the
contribution.

In order to show your agreement with the DCO you should include at the end of the commit message,
the following line: `Signed-off-by: John Doe <john.doe@example.com>`, using your real name.

This can be done easily using the [`-s`](https://github.com/git/git/blob/b2c150d3aa82f6583b9aadfecc5f8fa1c74aca09/Documentation/git-commit.txt#L154-L161) flag on the `git commit`.

Visual Studio code also has a flag to enable signoff on commits 

If you find yourself pushed a few commits without `Signed-off-by`, you can still add it afterwards. Read this for help: [fix-DCO.md](https://github.com/src-d/guide/blob/master/developer-community/fix-DCO.md).

## Support Channels

The official support channel, for both users and contributors, is:

- GitHub issues: each repository has its own list of issues.

*Before opening a new issue or submitting a new pull request, it's helpful to
search the project - it's likely that another user has already reported the
issue you're facing, or it's a known issue that we're already aware of.


## How to Contribute
In general, please use conventional approaches to development and contribution such as:
* Create branches for additions or deletions, and or side projects
* Do not commit to master!
* Use Pull Requests (PRs) to indicate that an addition is ready to merge. 
PRs are the main and exclusive way to contribute code to source{d} projects.
In order for a PR to be accepted it needs to pass this list of requirements:

- The contribution must be correctly explained with natural language and providing a minimum working example that reproduces it.
- All PRs must be written idiomaticly:
    - for Node: formatted according to [AirBnB standards](https://github.com/airbnb/javascript), and no warnings from `eslint` using the AirBnB style guide
    - for other languages, similar constraints apply.
- They should in general include tests, and those shall pass.
    - In any case, all the PRs have to pass the personal evaluation of at least one of the [maintainers](MAINTAINERS) of the project.


### Format of the commit message

Every commit message should describe what was changed, under which context and, if applicable, the issue it relates to (mentioning a GitHub issue number when applicable):

For small changes, or changes to a testing or personal branch, the commit message should be a short changelog entry

For larger changes or for changes on branches that are more widely used, the commit message should simply reference an entry to some other changelog system. It is encouraged to use some sort of versioning system to log changes. Example commit messages:
```
superscript.py v 2.0.5.006
```

The format can be described more formally as follows:

```
<package> v <version number>
```