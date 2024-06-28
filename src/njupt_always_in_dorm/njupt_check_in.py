from dataclasses import dataclass
import requests
import logging
from .swms_base64 import swms_base64_encode

logger = logging.getLogger(__name__)


@dataclass
class NjuptCheckInInfo:
    id: str
    name: str
    checked_in: bool
    check_location: bool
    required_latitude: float = 0
    required_longitude: float = 0
    max_distance: float = 0
    check_in_count: int | None = None
    max_check_in_count: int | None = None


class NjuptCheckIn:
    def __init__(self, session: requests.Session, use_web_vpn: bool = False):
        self.session = session
        self.use_web_vpn = use_web_vpn
        self.base_url = (
            "https://xgwx.njupt.edu.cn"
            if not use_web_vpn
            else "https://vpn.njupt.edu.cn:8443/http/webvpn49e3a2b7922e8188784e982b822fe767656010788fa00909624b9ed851a748dc"
        )

    def fetch(self) -> list[NjuptCheckInInfo]:
        url = f"{self.base_url}/swms/a/cmobile/sskq/kqrw/getKqrw"
        response = self.session.post(url).json()
        if response["result"] == "noKqrw":  # 没有考勤任务
            return []
        result = []
        for po in response["page"]["list"]:
            check_in_count = po.get("kqcs")  # 考勤次数
            if check_in_count == "" or check_in_count is None:
                check_in_count = None
            else:
                check_in_count = int(check_in_count)
            max_check_in_count = po.get("yxkqcs")  # 有效考勤次数
            if max_check_in_count == "" or max_check_in_count is None:
                max_check_in_count = None
            else:
                max_check_in_count = int(max_check_in_count)
            result.append(
                NjuptCheckInInfo(
                    po["wid"],
                    po["kqmc"],  # 考勤名称
                    po["sfkq"] == "1",  # 是否考勤
                    po["sfdw"] == "1",  # 是否定位
                    float(po["sslwd"]),  # 宿舍楼纬度
                    float(po["ssljd"]),  # 宿舍楼经度
                    float(po["dwfw"]),  # 定位范围
                    check_in_count,
                    max_check_in_count,
                )
            )
        return result

    def coordinates_to_address(self, lat: float, lon: float) -> str:
        url = f"{self.base_url}/swms/a/amobile/authentication/qqCoordToAddr"
        data = {
            "lat": lat,
            "lng": lon,
        }
        response = self.session.post(url, json=data).json()
        if response["code"] != 0:
            raise Exception(
                "Failed to convert coordinates to address, code: " + response["code"]
            )
        return response["result"]["address"]

    def check_location(self, info: NjuptCheckInInfo, lat: float, lon: float) -> bool:
        if not info.check_location:
            return True
        url = f"{self.base_url}/swms/a/sskq/kqrw/checkDz"
        data = {
            "sjkqjd": swms_base64_encode(str(lon)),  # 实际考勤经度
            "sjkqwd": swms_base64_encode(str(lat)),  # 实际考勤纬度
            "wid": swms_base64_encode(info.id),
        }
        response = self.session.post(url, data=data).json()
        return response["res"] == "success"

    def check_in(self, info: NjuptCheckInInfo, lat: float, lon: float, address: str):
        if info.check_in_count is not None and info.max_check_in_count is not None:
            if info.check_in_count >= info.max_check_in_count:
                raise Exception("Maximum check-in count reached")
        url = f"{self.base_url}/swms/a/cmobile/sskq/kqrw/kq"
        data = {
            "wid": swms_base64_encode(info.id),
            "zb": [swms_base64_encode(str(lon)), swms_base64_encode(str(lat))],
            "kqzt": swms_base64_encode("1"),  # 考勤状态
            "sjkqdz": swms_base64_encode(address),  # 实际考勤地址
        }
        response = self.session.post(url, data=data)
        if not response.ok:
            raise Exception(f"Failed to check in, status code: {response.status_code}")
