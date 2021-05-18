from sys import exit

import requests
from sys import argv
import re
from datetime import datetime


def split_into_chunks(text, delimiters):
    """separates a text into blocks by a list of delimiter criteria"""
    chunks = []
    for start, end in zip(range(0, len(delimiters) - 1), range(1, len(delimiters))):
        chunks.append(
            text[
                text.index(delimiters[start]):text.index(delimiters[end])
            ]
        )
    chunks.append(
        text[text.index(delimiters[-1]):]
    )
    return chunks


# football team
ftb_team = "Bayern"
# stores found results
results = []

# check if CLI arguments are 2 or more and concatenate them if exceeds
if len(argv) == 2:
    fb_script, ftb_team = argv
elif len(argv) == 3:
    fb_script, fb_first_name, fb_second_name = argv
    ftb_team = fb_first_name + " " + fb_second_name

# download file as text
fb_url = 'https://raw.githubusercontent.com/openfootball/europe-champions-league/master/2012-13/cl_finals.txt'
r = requests.get(fb_url)
ftb_db_file = r.text
if ('404: Not Found' in ftb_db_file) or r.status_code == 404:
    print('Error downloading Football DB file from repo')
    exit(1)

try:
    # list of rows which contain year
    find_year_row = re.findall(r"\(\d{1,2}\).*\d{4}", ftb_db_file)

    # separate years into blocks
    blocks_by_year = split_into_chunks(ftb_db_file, find_year_row)

    for block_by_year in blocks_by_year:
        if ftb_team in block_by_year:
            # list of years
            find_year = re.findall(r"(\d{4})", block_by_year)

            # list of game match dates
            find_date_row = re.findall(r"\[[a-zA-Z]{3} [a-zA-Z]{3}/\d{1,2}\]", block_by_year)

            # list of lists of Month and date e.g. [('Feb', '12'), ('Feb', '20')]
            find_date_month = re.findall(r"\[[a-zA-Z]{3} ([a-zA-Z]{3})/(\d{1,2})\]", block_by_year)

            # list of blocks that where split by dates
            blocks_by_day = split_into_chunks(block_by_year, find_date_row)
            for block_by_day, index in zip(blocks_by_day, range(len(find_date_month))):
                if ftb_team in block_by_day:

                    # list of lists that match [team host] [game result] [team guest]
                    find_match_result = re.findall(r"\s+\d+\.\d+\s+(%s)\s*.*\s+(\d+-\d+)\s+(.*)" % ftb_team,
                                                   block_by_day)
                    # if no [team HOST] found in whole block search again in [team GUEST]
                    if not find_match_result:
                        find_match_result = re.findall(r"\s+\d+\.\d+\s+(.*).*\s+(\d+-\d+)\s+(%s)" % ftb_team,
                                                       block_by_day)

                    year = find_year[0]
                    month = find_date_month[index][0]
                    numeric_month = datetime.strptime(month, "%b").month
                    day = find_date_month[index][1]

                    team_host = find_match_result[0][0]
                    match_score = find_match_result[0][1]
                    team_guest = find_match_result[0][2].split('@', 1)[0]

                    # removes all whitespaces starting from second one
                    team_guest = " ".join(team_guest.split(" ", 2)[:2])
                    team_host = " ".join(team_host.split(" ", 2)[:2])

                    results.append((
                        year, numeric_month, day, team_host, match_score, team_guest
                    ))

    for result in results:
        print("{}-{}-{} {} {} {}".format(result[0], result[1], result[2], result[3], result[4], result[5]))
    # output format
    #       [yyyy-mm-dd] [team host] [game result] [team guest]
except:
    raise Exception('This is regex - it wants the exact team name :/')
