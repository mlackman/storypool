from typing import Generator
import requests
import json

from .collect import Issue


def search_jira(jql: str, basic_auth: str, domain_name: str) -> Generator[Issue, Issue, None]:

    headers = {
        'authorization': basic_auth,
        'content-type': 'application/json'
    }

    start_at = 0
    while True:
        payload = {
            "jql": jql,
            "startAt": start_at
        }

        r = requests.post(f'https://{domain_name}/rest/api/2/search', data=json.dumps(payload), headers=headers)
        r.raise_for_status()

        issues = r.json()['issues']
        if len(issues) == 0:  # We are done fetching pages
            return

        for issue in issues:
            id = issue['key']
            fields = issue['fields']

            if is_development_done(fields['status']['name']):
                status = 'Done'
            else:
                status = fields['status']['statusCategory']['name']
            issue_type = fields['issuetype']['name']
            priority = fields['priority']['name']
            yield Issue(id, status, issue_type, priority)

        start_at += 50  # To next page


def is_development_done(issue_status: str) -> bool:
    return issue_status.upper() in (
        "READY FOR PRODUCTION RELEASE",
        "READY FOR PRODUCTION DEPLOYMENT",
        "READY FOR QA",
        "READY FOR UAT",
        "IN QA",
        "DONE"
    )
