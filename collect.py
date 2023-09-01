from typing import Generator, Literal
import base64
import requests
import json
import dataclasses
import datetime
import config


@dataclasses.dataclass
class Issue:
    id: str
    status: Literal['To Do', 'In Progress', 'Done']
    type: Literal['Feature', 'Bug', 'Epic']
    priority: Literal['High', 'Medium', 'Low']


@dataclasses.dataclass
class Stats:
    checked_at: str
    todo_count: int
    done_count: int


@dataclasses.dataclass
class VelocityStats:
    done_per_day: float
    estimated_done_date: str


def basic_auth(username: str, pat: str) -> str:
    credentials = f'{username}:{pat}'
    encoded_creds: bytes = base64.b64encode(credentials.encode())
    b64_creds: str = encoded_creds.decode()
    return f'Basic {b64_creds}'


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
            status = fields['status']['statusCategory']['name']
            issue_type = fields['issuetype']['name']
            priority = fields['priority']['name']
            yield Issue(id, status, issue_type, priority)

        start_at += 50  # To next page


def update_stats(checked_at: str, issues: list[Issue]) -> None:
    """
    Keep track of stats in file
    """
    with open('stats', 'at') as f:
        todo_count = len([issue for issue in issues if issue.status in ['In Progress', 'To Do']])
        done_count = len([issue for issue in issues if issue.status in ['Done']])
        f.write(f'{checked_at};{todo_count};{done_count}\n')


def get_stats() -> list[Stats]:
    stats: list[Stats] = []
    with open('stats', 'rt') as f:
        for line in f:
            timestamp, todo_count, done_count = line.split(';')
            stats.append(Stats(checked_at=timestamp, todo_count=int(todo_count), done_count=int(done_count)))

    return stats


def calculate_velocity_stats(stats: list[Stats]) -> VelocityStats:
    first_stats = stats[0]
    last_stats = stats[-1]

    first_date = datetime.datetime.fromisoformat(first_stats.checked_at).date()
    last_date = datetime.datetime.fromisoformat(last_stats.checked_at).date()

    done_count_on_start = first_stats.done_count
    done_count_now = last_stats.done_count

    days_between = (last_date - first_date).days

    velocity: float = (done_count_now - done_count_on_start) / days_between if days_between != 0 else 0

    if velocity != 0:
        days_until_done = int(last_stats.todo_count / velocity)
        date_until_done = (last_date + datetime.timedelta(days=days_until_done)).isoformat()
    else:
        date_until_done = 'Who knows, velocity can not be calculated yet'

    return VelocityStats(done_per_day=velocity, estimated_done_date=date_until_done)


def create_issues_js(stats: list[Stats], velocity_stats: VelocityStats, issues: list[Issue]) -> None:
    results = {
        'stats': [dataclasses.asdict(stat) for stat in stats],
        'velocityStats':  dataclasses.asdict(velocity_stats),
        'issues': [dataclasses.asdict(issue) for issue in issues],
    }

    with open('src/issues.js', 'wt') as f:
        issues_json = json.dumps(results)
        f.write(f'const issues={issues_json}')


if __name__ == '__main__':
    auth = basic_auth(config.USERNAME, config.PAT)

    issues = [issue for issue in search_jira(config.JQL, auth, config.DOMAIN_NAME)]

    checked_at: str = datetime.datetime.now().isoformat()

    update_stats(checked_at, issues)
    stats: list[Stats] = get_stats()
    velocity_stats = calculate_velocity_stats(stats)

    create_issues_js(stats, velocity_stats, issues)
