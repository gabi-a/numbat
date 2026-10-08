"""Configure the SynthNV Pro's power-on state (stored in its EEPROM).

The main change from the factory configuration: the RF output is OFF (PLL/VCO
powered down) when the synth powers up. Sweeps are also stopped so nothing
starts by itself at boot.

By default this is a dry run: it shows the device's current settings and the
changes it would make. Pass --write to apply them, save them to the EEPROM,
reboot the device and check that it came up as configured.

Usage: uv run scripts/configure_synth_power_on.py [--write] [--yes]
       [--frequency MHZ] [--power DBM] [--port PORT]
"""

import argparse
import sys

from SynthNVProDriver import SynthNVPro

# Readings that change on their own (detector, temperature, lock/calibration state).
VOLATILE = {"w", "z", "p", "V", "a"}


def describe(settings):
    return {k: v for k, v in settings.items() if k not in VOLATILE and v != ""}


def print_diff(before, after, title):
    changed = {k: (before.get(k), after.get(k)) for k in sorted(set(before) | set(after))
               if before.get(k) != after.get(k)}
    print(title)
    if not changed:
        print("  (no differences)")
    for key, (old, new) in changed.items():
        print(f"  {key}: {old} -> {new}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", help="serial port (default: auto-discover)")
    parser.add_argument("--frequency", type=float, metavar="MHZ",
                        help="also set the power-on frequency (default: keep the current one)")
    parser.add_argument("--power", type=float, metavar="DBM",
                        help="also set the power-on RF power (default: keep the current one)")
    parser.add_argument("--write", action="store_true",
                        help="apply the changes and save them to the EEPROM (default: dry run)")
    parser.add_argument("--yes", action="store_true", help="do not ask for confirmation")
    args = parser.parse_args()

    with SynthNVPro.connect(args.port, max_power_dbm=args.power) as synth:
        print(synth.info())
        before = synth.read_settings()
        print("\nCurrent settings:")
        for key, value in sorted(describe(before).items()):
            print(f"  {key}: {value}")

        plan = {"E": "0 (RF output OFF at power-on)", "g": "0 (no sweep running)",
                "c": "0 (sweep not continuous)"}
        if args.frequency is not None:
            plan["f"] = f"{args.frequency:g} MHz"
        if args.power is not None:
            plan["W"] = f"{args.power:g} dBm"
        print("\nPower-on configuration to store:")
        for key, value in plan.items():
            print(f"  {key}: {before.get(key)} -> {value}")

        if not args.write:
            print("\nDry run: nothing was changed. Re-run with --write to apply.")
            return 0

        if not args.yes and input("\nWrite this to the device's EEPROM? [y/N] ").lower() != "y":
            print("Aborted; nothing saved.")
            return 1

        # disable() powers the PLL down and stops/un-continues any sweep; the
        # optional values are set (and read back) while the output is off.
        synth.disable()
        if args.frequency is not None:
            synth.set_frequency(args.frequency)
        if args.power is not None:
            synth.set_power(args.power)
        applied = synth.read_settings()
        if applied.get("E") != "0":
            print("error: PLL is not off after disable(); not saving", file=sys.stderr)
            return 2

        synth.save_to_eeprom()
        print("\nSaved to EEPROM. Rebooting to check the power-on state...")
        synth.reboot()

        after = synth.read_settings()
        print_diff(describe(before), describe(after), "\nChanges after reboot (vs. before):")
        if after.get("E") == "0" and after.get("g") == "0":
            print("\nOK: the synth powers up with the RF output off.")
            return 0
        print(f"\nFAILED: after reboot E={after.get('E')} g={after.get('g')} "
              "(expected both 0); the settings were not stored.", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
