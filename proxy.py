import requests

from collections import deque
from datetime import datetime
from typing import List, Dict, Any, Deque, Tuple

from bs4 import BeautifulSoup


class Proxies:

    PROXY_TIMEOUT_SECONDS = 0.75

    def _get_free_proxies(self) -> Deque[Dict[str, str]]:
        url = "https://free-proxy-list.net/"
        # get the HTTP response and construct soup object
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        proxies: Deque[Dict[str, str]] = deque()
        for row in soup.find("div", class_="table-responsive").find_all("tr")[1:]:
            tds = row.find_all("td")
            try:
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                country_code = tds[2].text.strip()
                google = True if tds[5].text.strip() == "yes" else False
                https_available = True if tds[6].text.strip() == "yes" else False
                host = f"{ip}:{port}"
                proxies.append(
                    {
                        "url": host,
                        "country_code": country_code,
                        "google_available": google,
                        "https_available": https_available,
                    }
                )
            except IndexError:
                continue
        return proxies

    def _get_session(self, proxy: str):
        # construct an HTTP session
        session = requests.Session()
        # choose one random proxy
        session.proxies = {"http": proxy, "https": proxy}
        session.trust_env = False
        return session

    def _get_https_session(self, proxy: str, trust_env=False):
        # construct an HTTP session
        session = requests.Session()
        # choose one random proxy
        session.proxies = {"https": proxy}
        session.trust_env = trust_env
        return session

    def _test_session(self, proxy_session, proxy_url: str) -> Tuple[bool, int]:
        proxy_url = proxy_url.split(":")[0]
        start_request = datetime.now()
        response = proxy_session.get("http://icanhazip.com", timeout=self.PROXY_TIMEOUT_SECONDS)
        end_request = datetime.now()
        request_time = end_request - start_request
        response_text: str = response.text.strip()
        if proxy_url == response_text:
            return (True, request_time.microseconds)
        return (False, request_time.microseconds)

    def _get_only_valid_proxies(self, proxies_data: Deque[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid_proxies = list()
        while proxies_data:
            proxy_data = proxies_data.popleft()
            proxy_url = proxy_data["url"]
            try:
                proxy_session = self._get_session(proxy_url)
                is_valid, request_time = self._test_session(proxy_session, proxy_url)
                if is_valid:
                    proxy_data["is_valid"] = is_valid
                    proxy_data["request_time"] = request_time
                    valid_proxies.append(proxy_data)
            except Exception:
                # TODO: at least print error message
                continue
        return valid_proxies

    def get_proxy(self) -> Any:
        print("Get FREE proxies")
        proxies_data = self._get_free_proxies()
        print(f"Got {len(proxies_data)} FREE proxies")

        print("Get valid FREE proxies")
        valid_proxies = self._get_only_valid_proxies(proxies_data)
        print(f"Got {len(valid_proxies)} valid FREE proxies")

        print("Sort proxies by speed")
        sorted_proxies_by_speed = sorted(valid_proxies, key=lambda item: item["request_time"], reverse=False)
        print("Get only HTTPS proxies")
        sorted_proxies_by_speed_https = [proxy for proxy in sorted_proxies_by_speed if proxy["https_available"]]
        if len(sorted_proxies_by_speed_https) == 0:
            raise Exception("No proxy found!")
        print(f"Got {len(sorted_proxies_by_speed_https)} HTTPS proxies")

        print("Get the fastest HTTPS proxy and use it")
        proxy_session = self._get_https_session(sorted_proxies_by_speed_https[0]["url"], trust_env=False)
        return proxy_session
