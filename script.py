from github import Github
from datetime import datetime, timedelta
from matplotlib import pyplot as plt

def unique(lst):
    unique_list = []
    for element in lst:
        if element not in unique_list:
            unique_list.append(element)
    return unique_list

org = "incountry"
token = ""
gh = Github(token)
org = gh.get_organization(org)
repo = org.get_repo("infra")
pulls = repo.get_pulls(state="closed")
initiators = [pr.user.name for pr in pulls
              if (pr.merged_at is not None) and
              (pr.merged_at >= datetime.now()-timedelta(days=50))]
labels = unique(initiators)
sizes = [0] * len(labels)
labels_with_percentage = []
label_to_percentage = {}

for label in labels:
    sizes[labels.index(label)] = initiators.count(label)
total_size = sum(sizes)

for label in labels:
    percentage = (sizes[labels.index(label)] / total_size) * 100
    label_to_percentage[label] = percentage

for label, percentage in sorted(label_to_percentage.items(), key=lambda item: item[1], reverse=True):
    labels_with_percentage.append("{:.2f}% - {}".format(percentage, label))

sizes.sort(reverse=True)
patches, texts = plt.pie(sizes, startangle=90)
plt.legend(patches, labels_with_percentage, loc="best")
plt.axis('equal')
plt.tight_layout()
plt.show()
