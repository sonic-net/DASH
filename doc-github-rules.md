---
title: Github basic process
description: Describes basic GitHub rules 
last update: 02/14/2022
---

# GitHub basic process

**Table of contents**
- [Create issues](#create-issues)
- [Create a fork](#create-a-fork)
  - [Create a Pull Request](#create-a-pull-request)
- [Create a Pull Request from a branch in the original repository](#create-a-pull-request-from-a-branch-in-the-original-repository)
- [PR Review Phase](#pr-review-phase)
- [PR Accept Phase](#pr-accept-phase)
- [Directly Editing Artifacts](#directly-editing-artifacts)
- [Use checklists for large issues or PRs](#use-checklists-for-large-issues-or-prs)
- [Tools](#tools)

This document describes a short process to effectively use GitHub to achieve the following main goals:

1. Proposing a change. 
2. Reporting a bug. 
3. Making improvement suggestions.   

> [!NOTE]
> The intent of this document is not to teach the use of GitHub. The document just gathers some basic rules for a quick reference. 

## Create issues

You use the **Issues** mechanism to report problems, bugs and suggest general improvements. This is for both internal and external contributors. 

This approach is useful if you want to 

- Flag items that cannot be addressed by a single PR.
- Request that may need to be analyzed to find the proper course of action.
- Record information to put on backlog.  

Please, include relevant details the rest of the community needs to understand in order to discuss the issue effectively. 

For more information, see [Creating an issue](https://docs.GitHub.com/en/issues/tracking-your-work-with-issues/creating-an-issue). 


## Create a fork

You fork a repository to propose changes to the original repository. This is the recommended practice for community contributions.

For more information, see [Fork a repo](https://docs.github.com/en/get-started/quickstart/fork-a-repo).

If you use the Github desktop app, see [Cloning and forking repositories from GitHub Desktop](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop). 
   
It's good practice to regularly sync your fork with the original repository. 
For more information, see [Syncing a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork).

### Create a Pull Request

You can make any changes to a fork, including making branches and opening pull requests. 
If you want to contribute to the original repository, you can submit a pull request.

For more information, see [Creating a pull request from a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).

If you use the Github desktop app, see [Creating an issue or pull request](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/working-with-your-remote-repository-on-github-or-github-enterprise/creating-an-issue-or-pull-request). 

## Create a Pull Request from a branch in the original repository

> [!WARNING] 
> This approach is for contributors that have write access to the original repository and should be used sparingly. Excessive "topic branches" can clutter the main repository. 

You create a branch off the original repository and then create a PR based on this branch. 

For more information, see [Creating a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request). 

If you use the Github desktop app, see [Creating an issue or pull request](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/working-with-your-remote-repository-on-github-or-github-enterprise/creating-an-issue-or-pull-request). 

## PR Review Phase
Pull requests generally are open to community review and get accepted as-is or with requested changes. The more impactful the changes, the more review activity is to be expected.

## PR Accept Phase
Once a PR has received sufficient review and concerns are satisfied, a designated person with sufficient [permissions](https://docs.github.com/en/organizations/managing-access-to-your-organizations-repositories/repository-roles-for-an-organization#permissions-for-each-role) can accept the Pull Request. 

## Directly Editing Artifacts
Persons with write access permission or higher can directly edit documents and push changes. This practice should be used very sparingly, and only in the draft stages of documents or to make trivial changes in documents already in use.

> [!WARNING]
> Making direct edits to "released" documents which could impact downstream consumers, without proper review phases, short-circuits the normal community process and can result in breaking changes and significant disruption.


## Use checklists for large issues or PRs

When working on a complex issue or PR, it is often preferable to use a checklist within one issue or PR. This avoids the use of multiple issues or PRs that could be difficult to track.  

Especially with an issue related to a feature, all of the pull requests used to implement the feature can refer to the same issue. The progress made can be easily understood by looking at which boxes are checked and which are not. The status is found in one place.

Github even uses this checklist system to print out a small progress summary when looking at the lists of open issues.

You enter the checklist in the comment when you create the issue or the PR. To create a checklist, you use a markdown format similar to the one shown in the example below.

```md
- [x] Fix TOC
- [x] Add checklist section
```

## Tools

- [GitHub desktop](https://desktop.github.com/ "Cntrl+Left Click to open in a new tab")
- [How to Use the Github Workflow ](https://www.youtube.com/watch?v=8UguQzmswC4 "Cntrl+Left Click to open in a new tab")
- [Visual studio code](https://code.visualstudio.com/ "Cntrl+Left Click to open in a new tab")
  - [Gitlens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens "Cntrl+Left Click to open in a new tab"). Supercharge the Git capabilities. 
  - [Markdown All in One](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one "Cntrl+Left Click to open in a new tab"). Create the ToC for an article.
- [Drawing tool: diagrams.net](https://www.diagrams.net/ "Cntrl+Left Click to open in a new tab")

  
