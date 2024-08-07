## BOBILib

The HTML site of this project can be reached via: https://bobilib.org/.

Learn more about GitLab Pages at https://pages.gitlab.io and the official
documentation https://docs.gitlab.com/ce/user/project/pages/.

---
**Table of Contents**

- [Project Overview](#Project-Overview)
	- [Main Structure](#Main-Structure)
	- [Tools to Generate Resources](#Tools-to-Generate-Resources)
	- [tablefilter](#tablefilter)
	- [Instance Data](#Instance-Data)
- [GitLab CI](#gitlab-ci)

### Project Overview
#### Main Structure
The html files on the top level of this repository (documentation.html,etc.) are the website's main pages. The download page uses resources from the BOBILib-instances repository.
The [Gemfile](Gemfile) and [.gitlab-ci.yml](.gitlab-ci.yml) are used to build the website with ruby. The [_config.yml](_config.yml) TODO

#### Tools to Generate Resources
See the ReadMe in the directory [InterneTools](InterneTools).

### tablefilter

This directory contains a copy of the Tablefilter Javascript library.
https://www.tablefilter.com/

#### Instance Data
The htmls directory contains the pages for the different instances, as well as the 
design file for the instance pages. Also the all_instances.json for the tablefilter is provided in this directory.

The solutions directory contains the solution files. These files are extracted from the logfiles generated by the use of the solvers. For the extraction we used the Tools provided in [InterneTools/solutionfiles_extraction](InterneTools/solutionfiles_extraction).


### GitLab CI

This project's static Pages are built by [GitLab CI][ci], following the steps
defined in [`.gitlab-ci.yml`](.gitlab-ci.yml).