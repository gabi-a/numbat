"""Loopback test: sweep the SynthNV Pro across a frequency range at low power
and measure the power arriving at its own RFin, then plot it.

Connect RFout to RFin through a cable and enough attenuation that the
detector input stays well below its limit (check the SynthNV Pro manual for
the maximum RFin level; the default -30 dBm output is safe with a plain cable).

Usage: uv run scripts/test_synth_loopback.py [--start MHZ] [--stop MHZ] [--step MHZ]
       [--power DBM] [--averages N] [--settle S] [--port PORT] [--save PNG]
"""

import argparse
import time

import matplotlib.pyplot as plt
import numpy as np

from SynthNVProDriver import SynthNVPro


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=float, default=100.0, help="start frequency, MHz")
    parser.add_argument("--stop", type=float, default=3000.0, help="stop frequency, MHz")
    parser.add_argument("--step", type=float, default=10.0, help="frequency step, MHz")
    parser.add_argument("--power", type=float, default=-30.0, help="output power, dBm (also the safety cap)")
    parser.add_argument("--averages", type=int, default=5, help="detector readings averaged per point")
    parser.add_argument("--settle", type=float, default=0.02, help="settle time after each frequency change, s")
    parser.add_argument("--port", help="serial port (default: auto-discover)")
    parser.add_argument("--save", metavar="PNG", help="save the plot to this file instead of showing it")
    args = parser.parse_args()

    if args.step <= 0 or args.start >= args.stop:
        parser.error("need start < stop and step > 0")
    freqs = np.arange(args.start, args.stop + args.step / 2, args.step)
    measured = np.empty((len(freqs), 2))  # mean, std per point

    with SynthNVPro.connect(args.port, max_power_dbm=args.power) as synth:
        print(f"{synth.info()}")
        synth.disable()  # the device may boot with its output on; start from a known-off state
        synth.set_frequency(float(freqs[0]))
        synth.set_power(args.power)
        synth.enable()
        try:
            for i, f in enumerate(freqs):
                synth.set_frequency(float(f))
                time.sleep(args.settle)
                readings = synth.detector.read(args.averages)
                measured[i] = np.mean(readings), np.std(readings)
                if not synth.is_calibrated():
                    print(f"warning: output not calibrated at {f:.1f} MHz")
                print(f"{f:8.1f} MHz  {measured[i, 0]:7.2f} dBm (±{measured[i, 1]:.2f})")
        finally:
            synth.disable()

    mean, std = measured[:, 0], measured[:, 1]
    print(f"\nreceived power: mean {mean.mean():.2f} dBm, min {mean.min():.2f} at "
          f"{freqs[mean.argmin()]:.1f} MHz, max {mean.max():.2f} at {freqs[mean.argmax()]:.1f} MHz")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(freqs, mean, ".-", label="received (RFin)")
    ax.fill_between(freqs, mean - std, mean + std, alpha=0.3)
    ax.axhline(args.power, color="gray", ls="--", label=f"set power ({args.power:g} dBm)")
    ax.set_xlabel("frequency (MHz)")
    ax.set_ylabel("power (dBm)")
    ax.set_title("SynthNV Pro loopback sweep")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    if args.save:
        fig.savefig(args.save, dpi=100)
    else:
        plt.show()


if __name__ == "__main__":
    main()
