from dataclasses import dataclass
from typing import Generator, Sequence, Callable, TypeVar
import base64
import json

import requests


JiraIssue = dict
DoneStatues = Sequence[str]
IssueType = TypeVar('IssueType')
IssueFactory = Callable[[JiraIssue, DoneStatues], IssueType]


@dataclass(frozen=True)
class JiraConfig:
    username: str
    pat: str
    domain_name: str
    done_statuses: Sequence[str]

    def basic_auth(self) -> str:
        credentials = f'{self.username}:{self.pat}'
        encoded_creds: bytes = base64.b64encode(credentials.encode())
        b64_creds: str = encoded_creds.decode()
        return f'Basic {b64_creds}'


def search_jira[T](jql: str, factory: IssueFactory[T], config: JiraConfig) -> Generator[T, T, None]:
    headers = {
        'authorization': config.basic_auth(),
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
            yield factory(issue, config.done_statuses)

        start_at += 50  # To next page
