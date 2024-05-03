import base64
import datetime
import requests
import urllib.parse
import ddddocr
import logging
from Crypto.Cipher import AES
from Crypto.Util import Padding

logger = logging.getLogger(__name__)


class NjuptSsoException(Exception):
    def __init(self, code: int, message: str):
        self.code = code
        self.message = message


class NjuptSso:
    def __init__(self, session: requests.Session, use_web_vpn: bool = False):
        self.session = session
        self.ocr = ddddocr.DdddOcr(show_ad=False)
        self.use_web_vpn = use_web_vpn
        self.base_url = (
            "https://i.njupt.edu.cn"
            if not use_web_vpn
            else "https://vpn.njupt.edu.cn:8443/http/webvpn136ccf6a01ae6ad865c858647c2c1787df24ddb65ef7dc25fd3739a96a22c0ea"
        )

    def login(self, username: str, password: str) -> None:
        skipCaptcha = self._ifSkipCaptcha(username)
        checkKey = str(int(datetime.datetime.now().timestamp() * 1000))
        captcha = ""
        if not skipCaptcha:
            captcha_image = self._getCaptchaImage(checkKey)
            captcha = self.ocr.classification(captcha_image)
            logger.debug(f"Captcha recognized as {captcha} for key {checkKey}")
        else:
            logger.debug("Captcha skipped")

        url = f"{self.base_url}/ssoLogin/login"
        data = {
            "username": NjuptSso._encrypt(username, checkKey),
            "password": NjuptSso._encrypt(password, checkKey),
            "captcha": captcha,
            "checkKey": checkKey,
        }

        response = self.session.post(url, data=data).json()
        if not response["success"]:
            raise NjuptSsoException(response["code"], response["message"])

        if self.use_web_vpn:
            self.grant_service(
                "https://vpn.njupt.edu.cn:8443/enlink/api/client/callback/cas"
            )

    def grant_service(self, service: str) -> None:
        url = f"{self.base_url}/cas/login?service={urllib.parse.quote(service)}"
        response = self.session.get(url)
        if not response.ok:
            raise Exception(
                f"Failed to grant service '{service}', code: {response.status_code}"
            )

    @staticmethod
    def _encrypt(data: str, key: str) -> str:
        key = b"iam" + key.encode()
        iv = key
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return cipher.encrypt(Padding.pad(data.encode(), AES.block_size)).hex()

    def _ifSkipCaptcha(self, username: str) -> bool:
        url = (
            f"{self.base_url}/ssoLogin/getCaptchaStatus/{urllib.parse.quote(username)}"
        )
        response = self.session.get(url).json()
        return response["success"]

    def _getCaptchaImage(self, checkKey: str) -> bytes:
        url = f"{self.base_url}/sys/randomImage/{checkKey}"
        response = self.session.get(url).json()
        if not response["success"]:
            raise NjuptSsoException(response["code"], response["message"])
        data_uri = response["result"]

        data = data_uri.split(",")
        if not data[0] == "data:image/jpg;base64":
            raise Exception(f"Unsupported image type: <{data[0]}>")
        return base64.b64decode(data[1])
