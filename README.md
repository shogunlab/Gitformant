# Gitformant | ギトフルマント
![logo](https://i.imgur.com/rflqsil.png "Gitformant Logo")

Gitformant is an Open Source Intelligence (OSINT) tool developed by [Shogun Lab](http://www.shogunlab.com/) to aid researchers and security professionals in discovering Github repositories that may contain confidential information. It works by [searching Github](https://developer.github.com/v3/search/) for a keyword (internal URL, project specific acronym or terminology, etc) from code or internal documents. Additional checks can be performed if provided with a second list of keywords for verifying that the repository contents belong to a specific entity (ACME, acme.com/employee_login, Project Roadrunner, etc).

## Installation
Gitformant can be installed by downloading the zip file [here](https://github.com/shogunlab/gitformant/archive/master.zip) or by cloning the [Git](https://github.com/shogunlab/gitformant.git) repository:

`git clone https://github.com/shogunlab/gitformant.git`

Gitformant works with [Python](http://www.python.org/download/) **3** on any platform.

The included `requirements.txt` file can be used to install the pre-requisites with the following:
```
pip install -r requirements.txt
```

## Features
- Search Github for keywords belonging to confidential documents and discover leaks.
- Perform checks on discovered repositories to confirm or deny that they belong to a target organization.
- Log all results for further investigation and reporting.

## Usage
To perform a search on Github for an internal keyword, type:

`python gitformant.py "<insert internal keyword here>"`

To check the returned results for the existence of additional keywords, type:

`python gitformant.py "<insert internal keyword here>" "<insert confirmation keywords list here (comma separated)>"`

## Example Use Case
1. Alice is hired by ACME Inc. to perform an Open Source Intelligence assessment and find out if confidential ACME code is being leaked online.
2. She checks multiple search engines to see if the leaked code is being indexed, but doesn't find anything.
3. Alice asks the client if there are internal URLs or company keywords that are frequently used in development code.
4. The client gives Alice "login.acme-portal.com", the URL for their employee login portal and a link that frequently appears in the clients' private Github.
5. Alice performs a search for the keyword using Gitformant:
- `python gitformant.py "login.acme-portal.com"`
6. Alice finds no results, thinking that the keyword may be too specific, she changes the query to "acme-portal.com":
- `python gitformant.py "acme-portal.com"`
7. Alice is surprised to find several hundred results, however many of the findings are simply junk that makes reference to "acme-portal.com" among many other online portals.
8. Undeterred, Alice performs additional checks for ACME specific keywords in the repositories discovered using Gitformant:
- `python gitformant.py "acme-portal.com" "ACME,www.acme.com,ACME Inc"`
9. Alice discovers that one repository contains "acme-portal.com" and also has 32 hits for ACME, 15 hits for acme.com and 3 hits for ACME Inc.
10. Alice investigates the repository and finds that it is source code for an ACME Inc. production website with hardcoded admin login credentials.


### Misc. Usage and Performance Notes
- **Don't forget to add your Github API key!** Find out more [here](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/).
- There is a rate limit on the Github Search API, to avoid going over this limit a delay is built into the calls to Github's API
    - If the rate limit is hit, the application will sleep and then resume after 10 seconds
- Each confirmation keyword provided means an additional check is performed on every discovered repo, which means it can get **slow** FAST!
    - Try to limit confirmation keyword lists to two or three words (or grab a cup of coffee)

## Screenshots
**Basic usage**
![screen_1](https://i.imgur.com/m3OMqiF.png?1 "Gitformant Screenshot #1")

**With confirmation keywords list**
![screen_2](https://i.imgur.com/7lNK9i8.png?1 "Gitformant Screenshot #2")
![screen_3](https://i.imgur.com/EZ30blE.png?2 "Gitformant Screenshot #3")

## Legal
Gitformant was inspired by an excellent OSINT tool, called [Datasploit](https://github.com/DataSploit/datasploit).

The Gitformant OSINT tool is licensed under a GNU General Public License v3.0, you can read it [here](https://github.com/shogunlab/gitformant/blob/master/LICENSE.md).

The Gitformant logo is licensed under a [Creative Commons Creative Attribution 3.0 United States License](https://creativecommons.org/licenses/by/3.0/us/legalcode). Authored by ProSymbols.
