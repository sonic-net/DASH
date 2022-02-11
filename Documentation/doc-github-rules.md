---
title: Github basic process
description: Describe basic GitHub rules 
last update: 02/11/2022
---

# GitHub basic process

**Table of contents**
- [Create issues](#create-issues)
- [Create a fork](#create-a-fork)
  - [Create a Pull Request in the original repository from a fork](#create-a-pull-request-in-the-original-repository-from-a-fork)
- [Create a Pull Request from a branch in the original repository](#create-a-pull-request-from-a-branch-in-the-original-repository)
- [Tools](#tools)

This document describes a short process to effectively use GitHub to achieve the following main goals:

1. Proposing a change. 
2. Reporting a bug. 
3. Making impovement suggestions.   

> [!NOTE]
> The intent of this document is not to teach the use of GitHub. The document just gathers some basic rules for a quick reference. 

## Create issues

You use the **Issues** mechanism to report problems, bugs and suggest general improvements. This is for both internal and external contributors. 

This approach is useful if you want to 

- Flag items that cannot be addressed by a single PR.
- Request that may need to be analyzed to find the proper course of action.
- Record information to put on backlog.  

Please, include relevant details the rest of the team needs to understand in order to discuss the issue effectively. 

For more information, see [Creating an issue](https://docs.GitHub.com/en/issues/tracking-your-work-with-issues/creating-an-issue). 


## Create a fork

You fork a repository to propose changes to the original repository.
This is for external contributors that do not have the ability to create PRs directly against the original repository. It can also be used by internal contributors for longer tasks that cannot be addressed by issuing a single PR against the original repository. 

For more information, see [Fork a repo](https://docs.github.com/en/get-started/quickstart/fork-a-repo).

If you use the Github desktop app, see [Cloning and forking repositories from GitHub Desktop](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop). 

This approach is useful if you want to 

- Fix a pubished artifact.
- Create a new artifact.
- Improve overall readibility, usefulness, and quality.
   
In this case, it's good practice to regularly sync your fork with the original repository. 
For more information, see [Syncing a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork).

### Create a Pull Request in the original repository from a fork

> [!NOTE] 
> This approach is for external contributors and internal contributors that do not have write access to the original repository. This is the best practice to follow. 

You can make any changes to a fork, including making branches and opening pull requests. 
If you want to contribute to the original repository, you can send a request to the original author to pull your fork into their repository by submitting a pull request.

For more information, see [Creating a pull request from a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).

If you use the Github desktop app, see [Creating an issue or pull request](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/working-with-your-remote-repository-on-github-or-github-enterprise/creating-an-issue-or-pull-request). 

As the author, you submit the PR to a review phase. The PR can be approved or rejected. If approved, the proposed changes are merged into the original repository by the people that have the ability to do so.

## Create a Pull Request from a branch in the original repository

> [!WARNING] 
> This approach is for internal contributors that have write access to the original repository. 

You use a pull request (PR) to propose changes to a repository. 
You create a branch off the original repository and then create a PR based on this branch. 

As the author, you submit the PR to a review phase. The PR can be approved or rejected. If approved, the proposed changes are merged into the original repository by the people that have the ability to do so.

For more information, see [Creating a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request). 

If you use the Github desktop app, see [Creating an issue or pull request](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/working-with-your-remote-repository-on-github-or-github-enterprise/creating-an-issue-or-pull-request). 


## Tools

- [GitHub desktop](https://desktop.github.com/)
- [Visual studio code](https://code.visualstudio.com/)
  - [Gitlens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)
- [Drawing tool: diagrams.net](https://www.diagrams.net/)

  
