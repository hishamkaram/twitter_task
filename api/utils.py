import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def urljoin(*args):
    """
    Join given arguments into an url. Trailing Slash will be removed.

    Args:
        *args: url parts.

    Returns:
        full url after joining urls parts.

    """
    return "/".join(map(lambda x: str(x).rstrip("/"), args))


def requests_retry_session(status_forcelist=(502, 503, 504),
                           retries=5,
                           backoff_factor=1):
    """Create requests session which support retry mechanism.

    Args:
        status_forcelist (iterable, optional):
            A set of integer HTTP status codes that we should force a retry on.
            Defaults to (502, 503, 504).
        retries (int, optional):
            Total number of retries to allow, Defaults to 15.
        backoff_factor (float, optional):
            A backoff factor to apply between attempts after the second try.

    Returns:
        requests.Session obj.

    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        method_whitelist=frozenset(["GET", "POST", "PUT", "DELETE", "HEAD"]),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
