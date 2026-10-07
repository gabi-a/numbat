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
