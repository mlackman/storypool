from dataclasses import dataclass
from typing import Generator, Sequence
import json

import requests

from .collect import Issue


@dataclass(frozen=True)
class JiraConfig:
    basic_auth: str
    domain_name: str
    done_statuses: Sequence[str]


def search_jira(jql: str, config: JiraConfig) -> Generator[Issue, Issue, None]:

    headers = {
        'authorization': config.basic_auth,
        'content-type': 'application/json'
    }

    start_at = 0
    while True:
        payload = {
            "jql": jql,
            "startAt": start_at
        }

        r = requests.post(f'https://{config.domain_name}/rest/api/2/search', data=json.dumps(payload), headers=headers)
        r.raise_for_status()

        issues = r.json()['issues']
        if len(issues) == 0:  # We are done fetching pages
            return

        for issue in issues:
            id = issue['key']
            fields = issue['fields']

            issue_status = fields['status']['name']
            is_development_done = issue_status in config.done_statuses

            if is_development_done:
                status = 'Done'
            else:
                status = fields['status']['statusCategory']['name']

            issue_type = fields['issuetype']['name']
            priority = fields['priority']['name']
            yield Issue(id, status, issue_type, priority)

        start_at += 50  # To next page
