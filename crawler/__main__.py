import base64
import datetime

from .collect import update_stats, get_stats, calculate_velocity_stats, create_issues_js
from .jira import search_jira
from .types import Stats
import config


def basic_auth(username: str, pat: str) -> str:
    credentials = f'{username}:{pat}'
    encoded_creds: bytes = base64.b64encode(credentials.encode())
    b64_creds: str = encoded_creds.decode()
    return f'Basic {b64_creds}'


if __name__ == '__main__':
    auth = basic_auth(config.USERNAME, config.PAT)

    issues = [issue for issue in search_jira(config.JQL, auth, config.DOMAIN_NAME)]

    checked_at: str = datetime.datetime.now().isoformat()

    update_stats(checked_at, issues)
    stats: list[Stats] = get_stats()
    velocity_stats = calculate_velocity_stats(stats)

    create_issues_js(stats, velocity_stats, issues)
