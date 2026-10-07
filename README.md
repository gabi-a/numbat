# NuMBAT

Software to run the NuMBAT experiment.

## Setup

Requires [uv](https://docs.astral.sh/uv/). The hardware drivers live in their own
repos and are installed into the environment as editable local packages, so clone
them inside this folder:

```sh
git clone https://github.com/kmpape/sync_board.git
git clone https://github.com/gabi-a/SynthNVProDriver.git
uv sync
```

Then run things with `uv run`, e.g. `uv run python -c "import syncboard, SynthNVProDriver"`.

## Atik camera SDK

The Atik SDKs are proprietary and are not committed. Put these in `vendor/atik/`
(from the Atik Python SDK and Atik Cameras SDK downloads) before `uv sync`:

- `Atik_Python_SDK-1.5.1-py3-none-any.whl`
- `libatikcameras.so` (from `AtikCamerasSDK_*/lib/Linux/64/NoFlyCapture/`)
- `atik.rules` (optional, see below)

Import it via `from numbat.atik import AtikSDK`, which adds `vendor/atik` to
`LD_LIBRARY_PATH` so the native library is found.

To access the cameras over USB without root, install the udev rules once:

```sh
sudo cp vendor/atik/atik.rules /etc/udev/rules.d/ && sudo udevadm control --reload && sudo udevadm trigger
```
