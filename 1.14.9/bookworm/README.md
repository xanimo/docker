# Dogecoin Core 1.14.9 — minimal hardened image

A `FROM scratch` image containing only the verified Dogecoin Core binaries, a
minimal glibc userland, and a POSIX `sh` entrypoint. No OS layer, no package
manager, no root user at runtime.

## Security properties

The image is built to run fully unprivileged:

- Runs as `USER 1000:1000` (the `dogecoin` user); root is never used at runtime.
- No setuid or setgid binaries.
- Binaries and the entrypoint are owned by `root` and are not writable by the
  runtime user — a compromised process cannot overwrite them.
- No package manager, no `su`/`sudo`, and `dash` is the only shell.
- Final stage is `scratch`: only libc/libgcc/libstdc++, a handful of coreutils
  (`mkdir`, `grep`, `sed`), `dash`, and the three Dogecoin binaries are present.

These properties concern the **in-image** surface. They remove in-image
privilege-escalation primitives; they do not by themselves prevent container
escape, which depends on the container runtime, host kernel, and the flags
passed to `docker run`. Run with the restrictions below for a hardened
deployment.

## Recommended hardened invocation

The image runs cleanly with all capabilities dropped, `no-new-privileges`, and
a read-only root filesystem. When using `--read-only`, the data directory must
be a writable mount owned by UID 1000 — a bare `--tmpfs` defaults to root
ownership, so pass `uid=1000,gid=1000`:

```sh
docker run -d --name dogecoin \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --read-only \
  --tmpfs /dogecoin/.dogecoin:uid=1000,gid=1000 \
  -p 22556:22556 \
  <image> dogecoind -printtoconsole
```

For a persistent chain, replace the `--tmpfs` with a named volume or a
bind-mount whose host directory is owned by UID 1000:

```sh
docker run -d --name dogecoin \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --read-only \
  -v dogecoin-data:/dogecoin/.dogecoin \
  -p 22556:22556 \
  <image> dogecoind -printtoconsole
```

> If the data directory is root-owned, `dogecoind` fails at startup with
> `boost::filesystem::create_directory: Permission denied`. This is a mount
> ownership issue, not an image fault: ensure the mount is writable by
> UID 1000.

## Host UID remapping

The image does not bundle any privilege-remapping helper. For bind-mounted
volumes where host file ownership matters, use Docker rootless mode, the
daemon's `--userns-remap`, or pass `--user "$(id -u):$(id -g)"` at runtime.

## Environment variables

Any `dogecoind`/`dogecoin-cli`/`dogecoin-tx` option can be supplied as an
environment variable: uppercase the option name and replace `-` with `_`. For
example, `-rpcuser` becomes `RPCUSER` and `-help-debug` becomes `HELP_DEBUG`.
The entrypoint converts set variables into CLI flags at startup.
