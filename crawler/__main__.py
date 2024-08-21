import base64
import datetime
from typing import Sequence

from .collect import update_stats, get_stats, calculate_velocity_stats, create_issues_js
from .jira import JiraIssue, search_jira, JiraConfig
from .types import Issue, Stats
import config


def basic_auth(username: str, pat: str) -> str:
    credentials = f'{username}:{pat}'
    encoded_creds: bytes = base64.b64encode(credentials.encode())
    b64_creds: str = encoded_creds.decode()
    return f'Basic {b64_creds}'


def issue_factory(issue: JiraIssue, done_statuses: Sequence[str]) -> Issue:
    id = issue['key']
    fields = issue['fields']

    issue_status = fields['status']['name']
    is_development_done = issue_status in done_statuses

    if is_development_done:
        status = 'Done'
    else:
        status = fields['status']['statusCategory']['name']

    issue_type = fields['issuetype']['name']
    priority = fields['priority']['name']
    return Issue(id, status, issue_type, priority)


if __name__ == '__main__':
    auth = basic_auth(config.USERNAME, config.PAT)

    done_statuses = [status.upper() for status in config.DONE_STATUSES]

    jira_config = JiraConfig(auth, config.DOMAIN_NAME, done_statuses)

    issues = [issue for issue in search_jira(config.JQL, issue_factory, jira_config)]

    checked_at: str = datetime.datetime.now().isoformat()

    update_stats(checked_at, issues)
    stats: list[Stats] = get_stats()
    velocity_stats = calculate_velocity_stats(stats)

    create_issues_js(stats, velocity_stats, issues)
