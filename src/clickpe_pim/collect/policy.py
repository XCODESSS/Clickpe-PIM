from urllib.robotparser import RobotFileParser


def check_policy(url: str, user_agent: str, robots_body: str, robots_status: int) -> bool:
    if robots_status == 404:
        return True
    if robots_status != 200:
        return False
    parser = RobotFileParser()
    parser.parse(robots_body.splitlines())
    return parser.can_fetch(user_agent, url)

