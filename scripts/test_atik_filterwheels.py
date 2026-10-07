"""Detect all connected Atik external filter wheels and step each through every position.

Usage: uv run scripts/test_atik_filterwheels.py [--timeout SECONDS]
"""

import argparse
import time

from numbat.atik import AtikSDK


def wait_for_move(efw, timeout):
    start = time.monotonic()
    while efw.check_efw_moving():
        if time.monotonic() - start > timeout:
            raise TimeoutError(f"filter wheel still moving after {timeout} s")
        time.sleep(0.1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=30, help="max seconds to wait per move")
    args = parser.parse_args()

    # The SDK has no EFW count, so probe indices until one is absent.
    probe = AtikSDK.AtikSDKCamera()
    n_wheels = 0
    while probe.is_efw_present(n_wheels):
        n_wheels += 1
    print(f"Found {n_wheels} Atik filter wheel(s)")
    if n_wheels == 0:
        return

    wheels = []
    try:
        for i in range(n_wheels):
            efw = AtikSDK.AtikSDKCamera()
            efw.connect_efw(i)
            wheels.append(efw)
            wheel_type, serial = efw.efw_device_details()
            n_pos = efw.efw_num_positons()
            start_pos = efw.get_current_efw_positon()
            print(f"[{i}] {wheel_type.name} (serial {serial.rstrip(chr(0))}), "
                  f"{n_pos} positions, currently at {start_pos}")

            for pos in range(n_pos):
                efw.set_efw_position(pos)
                wait_for_move(efw, args.timeout)
                print(f"[{i}] moved to position {efw.get_current_efw_positon()} (requested {pos})")

            efw.set_efw_position(start_pos)
            wait_for_move(efw, args.timeout)
            print(f"[{i}] returned to position {efw.get_current_efw_positon()}")
    finally:
        for efw in wheels:
            efw.disconnect_efw()
        AtikSDK.ArtemisShutdown()


if __name__ == "__main__":
    main()
