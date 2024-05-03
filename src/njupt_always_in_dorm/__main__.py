def main():
    import os
    import argparse
    import logging
    from enum import Enum

    class WebVpnMode(str, Enum):
        ON = "on"
        OFF = "off"
        AUTO = "auto"

    parser = argparse.ArgumentParser(
        description="NJUPT Always In Dorm", prog="njupt-always-in-dorm"
    )
    username_from_env = os.environ.get("NJUPT_USERNAME", None)
    password_from_env = os.environ.get("NJUPT_PASSWORD", None)
    parser.add_argument(
        "--username",
        "-u",
        type=str,
        default=username_from_env,
        help="Your username",
        required=username_from_env is None,
    )
    parser.add_argument(
        "--password",
        "-p",
        type=str,
        default=password_from_env,
        help="Your password",
        required=password_from_env is None,
    )
    parser.add_argument("--oneshot", action="store_true", help="Oneshot mode")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    # on, off, auto
    parser.add_argument(
        "--web-vpn",
        type=WebVpnMode,
        default=WebVpnMode.AUTO,
        help="WebVPN mode",
        choices=[x.value for x in list(WebVpnMode)],
    )
    args = parser.parse_args()

    logging_level = logging.INFO if not args.debug else logging.DEBUG
    logging.basicConfig(
        level=logging_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    if args.debug:
        logging.debug("Debug mode enabled")

    import requests
    import random
    import math
    from .njupt_sso import NjuptSso
    from .njupt_check_in import NjuptCheckIn
    from .njupt_check_in import NjuptCheckInInfo
    from .njupt_web_vpn import NjuptWebVpn

    def __generate_random_geo_coordinates(lat, lon, max_distance):
        rad_lat = math.radians(lat)
        rad_lon = math.radians(lon)
        earth_radius = 6378137
        random_distance = random.uniform(0, max_distance)
        random_bearing = random.uniform(0, 2 * math.pi)
        new_lat_rad = math.asin(
            math.sin(rad_lat) * math.cos(random_distance / earth_radius)
            + math.cos(rad_lat)
            * math.sin(random_distance / earth_radius)
            * math.cos(random_bearing)
        )
        new_lon_rad = rad_lon + math.atan2(
            math.sin(random_bearing)
            * math.sin(random_distance / earth_radius)
            * math.cos(rad_lat),
            math.cos(random_distance / earth_radius)
            - math.sin(rad_lat) * math.sin(new_lat_rad),
        )
        new_lat = math.degrees(new_lat_rad)
        new_lon = math.degrees(new_lon_rad)
        return new_lat, new_lon

    def __checkin():
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            }
        )
        web_vpn = NjuptWebVpn(session)
        if args.web_vpn == WebVpnMode.AUTO:
            use_web_vpn = web_vpn.auto_detect()
        elif args.web_vpn == WebVpnMode.OFF:
            use_web_vpn = False
        elif args.web_vpn == WebVpnMode.ON:
            use_web_vpn = True
        else:
            raise ValueError("Invalid WebVPN mode")
        if use_web_vpn:
            logging.info("Mode: Using WebVPN")
        else:
            logging.info("Mode: Direct")
        sso = NjuptSso(session, use_web_vpn)
        sso.login(args.username, args.password)
        sso.grant_service("https://xgwx.njupt.edu.cn/swms/a/cas")
        checkin = NjuptCheckIn(session, use_web_vpn)
        records = checkin.fetch()
        if len(records) == 0:
            logging.info("No check-in task available")
            return
        for info in records:
            try:
                __handle_checkin_task(checkin, info)
            except Exception as e:
                type = e.__class__.__name__
                logging.error(
                    f"Failed to handle check-in task for {info.id}: ({type}) {e}"
                )

    def __handle_checkin_task(checkin: NjuptCheckIn, info: NjuptCheckInInfo):
        if info.name != "每日考勤":
            logging.info(f"Skipping task: {info.id} (Name={info.name} is not handled)")
            return
        if info.checked_in:
            logging.info(f"Already checked in: {info.id}")
            return
        location_retry = 0
        while True:
            [lat, lon] = __generate_random_geo_coordinates(
                info.required_latitude, info.required_longitude, info.max_distance * 0.5
            )
            address = checkin.coordinates_to_address(lat, lon)
            logging.info(f"Generated location for {info.id}: ({lat}, {lon}) {address}")
            if checkin.check_location(info, lat, lon):
                break
            logging.error(f"Location invalid, regenerating...")
            location_retry += 1
            if location_retry > 3:
                logging.error(
                    f"Failed to generate valid location for {info.id} after 3 retries"
                )
        checkin.check_in(info, lat, lon, address)
        logging.info(f"Checked in: {info.id}")

    def __checkin_noexcept():
        try:
            __checkin()
        except Exception as e:
            type = e.__class__.__name__
            logging.error(f"Failed to check in: ({type}) {e}")

    if args.oneshot:
        __checkin()
    else:
        import schedule
        import time

        schedule.every().day.at("23:26", "Asia/Shanghai").do(__checkin_noexcept)
        while True:
            schedule.run_pending()
            logging.info("Next scheduled at %s", schedule.next_run())
            time.sleep(schedule.idle_seconds())


if __name__ == "__main__":
    main()
