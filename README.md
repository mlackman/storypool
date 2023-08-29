# StoryPool

Shows Jira Features (with certain label) and Bugs in Todo pool and Done pool

Tested with python 3.10.7

# How to run

Copy config.py.COPYME to config.py and add your Jira Personal Access Token (PAT), username and domain name of your Jira.
Also JQL (Jirq qurey language) may be changed here.

Install requirements
```
python3 -m .venv venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run
```
python collect.py
```

View story pool in browser

```
open ./src/index.html
```
