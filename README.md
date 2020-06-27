Overview
--------

This project allows you to peer into which members of your team create the most pull requests within your organization.
This is important infomration that shows a person's activity within organization and helps make data-driven decisions instead of thinking of someone's performance based on the gut feeling.

Usage
-----

```shell
$ pip3 install pipenv
$ pipenv install
$ pipenv shell
$ python3 -h
```

Once you execute the script, you will be asked for a GitHub token.  
You can either input it every time your run the script or export is an environment variable, e.g. `GITHUB_TOKEN=XYZ`.

Get stats about all of your team's repos for the last 30 days
```shell
$ python3 script.py myorg myteam -d 30
```

Get stats about specific repos
```shell
$ python3 script.py myorg myteam --repos repo1 repo2 -d 30
```

To specify a file name for the report you can pass `--output` parameter to the script
Get stats about specific repos
```shell
$ python3 script.py myorg myteam --repos repoX --output /tmp/repoX.pdf
```

Resulting report
----------------

In the end, you will get a PDF document with a number of PRs submitted by the team members. Each repo will be locted on its own page.

![Example pie chart](https://i.postimg.cc/Y9LFr2gm/example.png "Example pie chart")
