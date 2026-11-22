# Sinnoh Remake (fan project)

Non-commercial fan hack that rebuilds the Sinnoh region on the pokeemerald-expansion engine. The first milestone is a Twinleaf-to-Oreburgh demo with a Platinum-style story.

This repository is not affiliated with Nintendo, Game Freak, The Pokémon Company, or ROM Hacking Hideout.

## Engine

Built on [pokeemerald-expansion](https://github.com/rh-hideout/pokeemerald-expansion) tag [`expansion/1.17.2`](https://github.com/rh-hideout/pokeemerald-expansion/tree/expansion/1.17.2) (commit `79dd436920845ebc145577649de624f65298c209`). That project is maintained by ROM Hacking Hideout (RHH) and is based on [pret/pokeemerald](https://github.com/pret/pokeemerald).

Credit RHH when describing the engine:

> Based off RHH's pokeemerald-expansion 1.17.2 https://github.com/rh-hideout/pokeemerald-expansion/

`expansion/1.17.2` does not include a single project-wide license file. The license files shipped with the bundled tools are kept in this tree (for example [`tools/gbagfx/LICENSE`](tools/gbagfx/LICENSE) and [`tools/gbafix/COPYING`](tools/gbafix/COPYING)). See the upstream repository for how the project is published.

Hack development happens on the `chris-hack` branch. `main` holds this imported engine plus these project notes.

## Building

Install dependencies and build from source by following [INSTALL.md](INSTALL.md). Linux package lists are under [docs/install/linux/](docs/install/linux/).

From the repository root, after the toolchain is installed:

```console
make -j$(nproc)
```

A successful build writes `pokeemerald.gba` in the repository root. That file is a local build output. Do not commit it.

## Legal

No Nintendo ROMs, BIOS files, or ripped copyrighted assets are included. The hack is distributed only as a `.bps` or `.ips` patch, or as source. Players must use their own legally obtained copy. There are no sales or paid access.

This project does not use official Pokémon logos or branding.
