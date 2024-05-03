import requests


class NjuptWebVpn:
    def __init__(self, session: requests.Session):
        self.session = session

    def auto_detect(self) -> bool:
        url = "https://i.njupt.edu.cn/"
        response = self.session.get(url, allow_redirects=False)
        response.raise_for_status()
        if response.status_code == 302:
            if "webvpn" in response.headers["Location"]:
                return True
        return False
