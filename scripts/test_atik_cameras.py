"""Detect all connected Atik cameras, take one image on each and display them.

Usage: uv run scripts/test_atik_cameras.py [--exposure SECONDS]
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np

from numbat.atik import AtikSDK


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exposure", type=float, default=0.1, help="exposure time in seconds")
    parser.add_argument("--save", metavar="PNG", help="save the figure to this file instead of showing it")
    args = parser.parse_args()

    probe = AtikSDK.AtikSDKCamera()
    n_cameras = probe.device_count()
    print(f"Found {n_cameras} Atik camera(s)")
    if n_cameras == 0:
        return

    cameras = []
    images = []
    try:
        for i in range(n_cameras):
            name = probe.get_device_name(i).rstrip("\x00")
            cam = AtikSDK.AtikSDKCamera()
            cam.connect(i)
            cameras.append(cam)
            print(f"[{i}] {name} (serial {cam.get_serial_str()})")
            print(f"[{i}] taking {args.exposure} s exposure...")
            img = cam.take_image(args.exposure)
            images.append((name, img))
            print(f"[{i}] image {img.shape} {img.dtype}, min {img.min()}, max {img.max()}, mean {img.mean():.1f}")
    finally:
        for cam in cameras:
            cam.disconnect()
        AtikSDK.ArtemisShutdown()

    fig, axes = plt.subplots(1, len(images), figsize=(5 * len(images), 5), squeeze=False)
    for i, (ax, (name, img)) in enumerate(zip(axes[0], images)):
        lo, hi = np.percentile(img, [1, 99.5])
        im = ax.imshow(img, cmap="gray", vmin=lo, vmax=hi)
        ax.set_title(f"[{i}] {name}")
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    if args.save:
        fig.savefig(args.save, dpi=100)
    else:
        plt.show()


if __name__ == "__main__":
    main()
