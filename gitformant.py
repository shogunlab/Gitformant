#!/usr/bin/env python

import json
import requests
import sys
import time

# Github API token for making requests, insert here if blank
GITHUB_API_TOKEN = ""
# List of repos discovered during investigation
repos = []

def main(inform_keyword, confirm_keywords=""):
    # Page count specifies the current page of the search results
    PAGE_COUNT = 1

    # Check to make sure a Github token is filled in
    try:
        if GITHUB_API_TOKEN != "":
            results_log = ""
            # Perform an initial search and return up to 100 results
            count, results = github_search(inform_keyword, "100", str(PAGE_COUNT))
            # Remaining results are kept track of in results_count
            results_count = count
            # Place the results into a variable with the total number
            github_results = [count, results]
            # Output the results to the user
            print(output(github_results, PAGE_COUNT - 1))
            results_log += output(github_results, PAGE_COUNT - 1)
            print("====== DISCOVERED REPOS ======")
            print(log_repo_list())
            # Tell the user the total number of returned results
            print("\nFound %s results on Github." % count)
        else:
            # Github API token is missing, return an error
            print("[!] Github API token is missing!")
            print("> Please fill in the GITHUB_API_TOKEN variable before continuing.")
            sys.exit(0)
    except Exception as e:
        print(e)

    # Results exceeded the return limit of 100 per page, enter loop to allow
    # user to go to the next page of results
    while True:
        if results_count >= 100:
            next_page_select = input("\nThere are more results to display, go to next page? (y/n) > ")
            if next_page_select == "y" or next_page_select == "Y":
                try:
                    # User has chosen to see next page of results, increment PAGE_COUNT
                    PAGE_COUNT += 1
                    # Make query for next page of 100 results
                    count, results = github_search(inform_keyword, "100", str(PAGE_COUNT))
                    github_results = [count, results]
                    # Output results of search to user
                    print(output(github_results, PAGE_COUNT - 1))
                    results_log += output(github_results, PAGE_COUNT - 1)
                    # Decrement remaining results by 100
                    results_count -= 100
                    print(log_repo_list())
                    print("\nResult count is now at %s" % str(results_count))
                except Exception as e:
                    print(e)
            else:
                # User does not want to see more results, break loop
                break
        else:
            # Break out of the loop
            break

    # Check if user provided confirmation keywords
    if confirm_keywords != "" and results_count != 0:
        try:
            # Ask user if they would like to perform analysis on returned results
            perform_analysis_select = input("\nWould you like to perform a confidentiality level analysis on the repositories found? (y/n) > ")
            if perform_analysis_select == "y" or perform_analysis_select == "Y":
                # Perform an analysis of how confident Gitformant is of repo confidentiality
                analysis_result = informant_analysis(repos, confirm_keywords)
                exit_and_log(results_log, log_repo_list(), analysis_result, inform_keyword, confirm_keywords)
            else:
                exit_and_log(results_log, log_repo_list(), "", inform_keyword, confirm_keywords)
        except Exception as e:
            print(e)
    # Otherwise, just exit and ask for log output
    else:
        exit_and_log(results_log, log_repo_list(), "", inform_keyword)

def exit_and_log(results_log_output, repo_list_results, informant_analysis_results="", inform_keyword="", confirm_keywords=""):
    if len(repo_list_results) != 0:
        log_select = input("\nWould you like to log results before exiting? (y/n) > ")
        if log_select == "y":
            # Allow user to specify log file name
            log_file_name = input("Enter the log file name > ")
            f = open("%s.txt" % log_file_name, "w+")
            # Record the search summary of which keywords were used in the initial query
            f.write("====== SEARCH SUMMARY ======")
            f.write("\nInformant keyword used: %s" % inform_keyword)
            if confirm_keywords != "":
                f.write("\nConfirmation keywords used: %s" % confirm_keywords)
            f.write("\n")
            # Record the results log from Github code search
            f.write("\n====== RESULTS LOG ======")
            f.write(results_log_output)
            # Record the unique repos discovered
            f.write("\n====== DISCOVERED REPOS ======")
            f.write(repo_list_results)
            # If informant analysis was performed, record that as well
            if informant_analysis_results != "":
                f.write("\n\n====== INFORMANT ANALYSIS RESULTS ======")
                f.write(informant_analysis_results)
            print("\nResults have been logged!")
            exit_banner()
            f.close()
            sys.exit(0)
        else:
            exit_banner()
            sys.exit(0)
    else:
        exit_banner()
        sys.exit(0)

def exit_banner():
    print("\n============================================")
    print("Thank you for using Gitformant! Goodbye...")
    print("============================================")

def remove_dupes(seq):
   # Order preserving remove duplicates from list function
   checked = []
   for e in seq:
       if e not in checked:
           checked.append(e)
   return checked

def log_repo_list():
    # Output list of discovered repos to user
    repo_results = ""
    for repo in remove_dupes(repos):
        repo_results += "\n+ https://github.com/%s" % repo
    return repo_results

def output(data, current_page):
    # Check if the current page is greater than one, if so, update index accordingly
    if current_page > 1:
        count = current_page * 100 + 1
    # But, if the current page is one, then at least 100 results
    # have been returned, just add 1
    elif current_page == 1:
        count = 100 + 1
    # Otherwise, we are at the beginning
    else:
        count = 1
    # Display information about the file where the keyword march was found
    # Show the owner and repository
    output_results = ""
    for snip in data[1]:
        output_result = "\n%s.  File: %s" % (str(count).zfill(2), snip['html_url'])
        output_result += "\n     Owner: %s" % snip['repository']['full_name']
        output_result += "\n     Repository: %s" % snip['repository']['html_url']
        output_result += "\n"
        output_results += output_result
        count += 1
    return output_results

def informant_analysis(repo_names, confirm_keywords):
    print("\nStarting analysis, please wait...")
    # For each unique repo, perform an analysis of how confident the assessment is of
    # the confidentiality level
    analysis_results = ""
    for repo_name in remove_dupes(repos):
        analysis_result = "\nRepository: https://github.com/%s" % repo_name
        if confirm_keywords != "":
            confirm_total = len(confirm_keywords)
            confirm_success = 0
            # For each keyword in the confirm_keywords list, check if there was a hit
            # in the repository search
            for keyword in confirm_keywords:
                confirm_count = github_confirmation(repo_name, keyword)
                analysis_result += "\nFound %s hit(s) for: %s" % (confirm_count, keyword)
                if confirm_count != 0:
                    # Increment the successful confirm keyword hit counter
                    confirm_success += 1
            # Confidence level is a measure of how many confirmation keywords were hit
            # and how many in total were provided by the user
            confidence_level = (float(confirm_success) / float(confirm_total)) * 100
            # Depending on the percentage of keywords hit vs keywords provided,
            # assign a description for level of confidence from VERY LOW to VERY HIGH
            if confidence_level >= 75:
                analysis_result += "\nConfidence level: VERY HIGH (%s%%)" % confidence_level
            elif confidence_level >= 50:
                analysis_result += "\nConfidence level: HIGH (%s%%)" % confidence_level
            elif confidence_level >= 25:
                analysis_result += "\nConfidence level: MODERATE (%s%%)" % confidence_level
            elif confidence_level < 25:
                analysis_result += "\nConfidence level: LOW (%s%%)" % confidence_level
            elif confidence_level == 0:
                analysis_result += "\nConfidence level: VERY LOW (%s%%)" % confidence_level
        analysis_result += "\n"
        print(analysis_result)
        analysis_results += analysis_result
    return analysis_results

def github_search(query, per_page="100", page_num="1"):
    # Github Search API endpoint for code on Github
    github_endpoint = "https://api.github.com/search/code?q=\"%s\"&per_page=%s&page=%s&access_token=%s" % (keyword, per_page, page_num, GITHUB_API_TOKEN)
    # Make the request
    req = requests.get(github_endpoint)
    # Save the response in data
    data = json.loads(req.content)
    # For each repo name, append it to the global repo list
    for result in data.get('items'):
        # Fetch the repo name and add it to the list of repos seen in results
        repo_name = result['repository']['full_name']
        repos.append(repo_name)
    # Return the total number of results and the items
    return data.get('total_count'), data.get('items')

def github_confirmation(repo, confirms):
    try:
        # Sleep for 5 seconds to avoid going over the API rate limit
        time.sleep(5)
        # Github Search API endpoint, limited to specific repository code
        github_endpoint = "https://api.github.com/search/code?q=\"%s\"+repo:%s&access_token=%s" % (confirms, repo, GITHUB_API_TOKEN)
        # Make the request
        req = requests.get(github_endpoint)
        # Save the response in data
        data = json.loads(req.content)
        result_count = data.get('total_count')
        # Rate limit has been hit, sleep and try again
        while result_count == None:
            print("Rate limit is being hit, sleeping for 10 seconds...")
            time.sleep(10)
            result_count = data.get('total_count')
        # Return total number of successful confirm keyword hits
        return result_count
    except Exception as e:
        return e

if __name__ == "__main__":
    try:
        # If user supplied a second argument, then perform a search with confirmation keywords
        if len(sys.argv) == 3:
            keyword = sys.argv[1]
            confirm_words = sys.argv[2].split(",")
            result = main(keyword, confirm_words)
        # Otherwise, just perform a search with informant keyword
        else:
            keyword = sys.argv[1]
            result = main(keyword)
    except Exception as e:
        print(e)
