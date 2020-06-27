from github import Github
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from getpass import getpass
import os
import yaml
import argparse
import sys
from loguru import logger

def parse_args():
    parser = argparse.ArgumentParser(description="Collects statistics related to GitHub pull requests")
    parser.add_argument("org", help="GitHub organization")
    parser.add_argument("team", help="GitHub team within the organzation")
    parser.add_argument("--repos", nargs='+', help="list of GitHub repos within the organization",
        default="all", metavar="REPO")
    parser.add_argument("-d", "--pr-age-in-days", help="look only for PRs that have been merged in the last N days",
        default=30, metavar="DAYS", type=int, dest="pr_age_in_days")
    parser.add_argument("-o", "--output", default="result.pdf", help="PDF file that will contain PR statistics",
        metavar="EXAMPLE.pdf")
    parser.add_argument("-l", "--log-level", help="log level", default="INFO", dest="log_level")
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

def get_team_repos(team, repos):
    if repos == "all":
        return [repo for repo in team.get_repos()]
    return [repo for repo in team.get_repos() if repo.name in args.repos]

def process_repo(repo, pr_age_in_days):
    logger.info(f"Processing {repo.name} GitHub repository...")
    pulls = repo.get_pulls(state="closed")
    initiators = [pr.user.login for pr in pulls
                    if (pr.merged_at is not None) and
                    (pr.merged_at >= datetime.now()-timedelta(days=pr_age_in_days))]
    labels = unique(initiators)
    sizes = [0] * len(labels)
    for label in labels:
        sizes[labels.index(label)] = initiators.count(label)
    total_size = sum(sizes)
    label_to_percentage = {}
    for label in labels:
        percentage = (sizes[labels.index(label)] / total_size) * 100
        label_to_percentage[label] = percentage
    labels = []
    for label, percentage in sorted(label_to_percentage.items(), key=lambda item: item[1], reverse=True):
        labels.append("{} - {:.2f}%".format(label, percentage))
    sizes.sort(reverse=True)
    patches, _ = plt.pie(sizes, startangle=90)
    plt.legend(patches, labels, loc="best")
    plt.axis("equal")
    plt.tight_layout()
    plt.title(f"{repo.name}")

if __name__ == "__main__":
    args = parse_args()
    logger.remove()
    logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", colorize=True, level=args.log_level)
    if os.environ.get("GITHUB_TOKEN") is None:
        token = getpass(prompt="Please enter your GitHub token: ")
    else:
        token = os.environ["GITHUB_TOKEN"]
    gh = Github(token)
    org_teams = gh.get_organization(args.org).get_teams()
    target_team = find_team_with_name(org_teams, args.team)
    team_members = [team_member.login for team_member in target_team.get_members()]
    team_repos = get_team_repos(target_team, args.repos)
    pdf = PdfPages(args.output)
    logger.info(f"Collecting statistic only about the PRs that have been merged within the last {args.pr_age_in_days} days.")
    number_of_repos = len(team_repos)
    for index, repo in enumerate(team_repos):
        process_repo(repo, args.pr_age_in_days)
        pdf.savefig()
        completion_percentage = ((index+1) / number_of_repos) * 100
        logger.debug("The report is {:.2f}% completed".format(completion_percentage))
    pdf.close()
    logger.info(f"The PDF report has been written to {args.output}")