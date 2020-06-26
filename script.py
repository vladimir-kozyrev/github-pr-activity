from github import Github
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from getpass import getpass
import argparse

#
# https://www.yegor256.com/2020/06/23/individual-performance-metrics.html
#

def parse_args():
    parser = argparse.ArgumentParser(description="Collects statistics related to GitHub pull requests.")
    parser.add_argument("org", help="A GitHub organization.")
    parser.add_argument("team", help="A GitHub team within the organzation.")
    #parser.add_argument("config", help="A configuration file for this script.")
    parser.add_argument("--output-file", default="result.pdf", help="A file which should contain PR statistics.")
    return parser.parse_args()

def unique(lst):
    unique_list = []
    for element in lst:
        if element not in unique_list:
            unique_list.append(element)
    return unique_list

def find_team_with_name(teams, name):
    for team in teams:
        if team.name == name:
            return team
    raise Exception(f"Team with name {name} has not been found.")

if __name__ == "__main__":
    args = parse_args()
    token = getpass(prompt="Please enter your GitHub token: ")
    gh = Github(token)
    org_teams = gh.get_organization(args.org).get_teams()
    target_team = find_team_with_name(org_teams, args.team)
    team_members = [team_member.login for team_member in target_team.get_members()]
    team_repos = target_team.get_repos()

    with PdfPages(args.output_file) as pdf:
        for repo in team_repos:
            print(repo.name)
            pulls = repo.get_pulls(state="closed")
            initiators = [pr.user.login for pr in pulls
                        if (pr.merged_at is not None) and
                        (pr.merged_at >= datetime.now()-timedelta(days=90))]
            labels = unique(initiators)
            sizes = [0] * len(labels)
            label_to_percentage = {}

            for label in labels:
                sizes[labels.index(label)] = initiators.count(label)
            total_size = sum(sizes)

            for label in labels:
                percentage = (sizes[labels.index(label)] / total_size) * 100
                label_to_percentage[label] = percentage

            labels = []
            for label, percentage in sorted(label_to_percentage.items(), key=lambda item: item[1], reverse=True):
                labels.append("{} - {:.2f}%".format(label, percentage))

            sizes.sort(reverse=True)
            patches, texts = plt.pie(sizes, startangle=90)
            plt.legend(patches, labels, loc="best")
            plt.axis("equal")
            plt.tight_layout()
            plt.title(f"{repo.name}")
            pdf.savefig()