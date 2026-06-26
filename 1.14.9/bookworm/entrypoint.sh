#!/bin/sh
# Entrypoint for Dogecoin Core — runs as dogecoin user (UID 1000), no root.
# For host UID remapping with bind-mounted volumes, use Docker rootless mode
# or pass --user "$(id -u):$(id -g)" at runtime.
set -e

EXECUTABLES="dogecoind dogecoin-cli dogecoin-tx"

# Default to dogecoind when no args are given, or when the first arg is a flag.
if [ $# -eq 0 ] || [ "${1#-}" != "$1" ]; then
    set -- dogecoind "$@"
fi

EXECUTABLE="$1"; shift

# Pass arbitrary commands through directly (e.g. sh, dogecoin-cli, dogecoin-tx).
case " $EXECUTABLES " in
    *" $EXECUTABLE "*) ;;
    *) exec "$EXECUTABLE" "$@" ;;
esac

# Create the data directory if it is absent.
# No chown needed — the container already runs as dogecoin:dogecoin.
DATADIR="${DATADIR:-/dogecoin/.dogecoin}"
mkdir -p "$DATADIR"

# Discover the set of CLI options supported by this executable.
if [ "$EXECUTABLE" = "dogecoind" ]; then
    HELP=$("$EXECUTABLE" -help -help-debug 2>&1 || true)
else
    HELP=$("$EXECUTABLE" -help 2>&1 || true)
fi

# Convert matching environment variables into CLI arguments, then unset them
# so they are not passed a second time through the inherited environment.
#
# Mapping rule (mirrors the Python entrypoint; sed y// replaces tr):
#   -rpcuser       → RPCUSER
#   -help-debug    → HELP_DEBUG
ENV_ARGS=""
while IFS= read -r line; do
    opt=$(printf '%s' "$line" | sed 's/^[[:space:]]*-//;s/[=<[:space:]].*//')
    [ -z "$opt" ] && continue
    var=$(printf '%s' "$opt" | sed 'y/abcdefghijklmnopqrstuvwxyz-/ABCDEFGHIJKLMNOPQRSTUVWXYZ_/')
    # POSIX: ${VAR+y} expands to "y" if VAR is set (even when empty).
    eval "isset=\${${var}+y}"
    # shellcheck disable=SC2154  # isset is assigned via the eval above
    [ "$isset" != "y" ] && continue
    eval "val=\${${var}}"
    unset "$var" 2>/dev/null || true
    if [ -n "$val" ]; then
        ENV_ARGS="$ENV_ARGS -${opt}=${val}"
    else
        ENV_ARGS="$ENV_ARGS -${opt}"
    fi
done <<HELP_EOF
$(printf '%s' "$HELP" | grep -E '^  -[a-z]')
HELP_EOF

# Replace this shell process with the selected binary (PID 1 stays clean).
if [ "$EXECUTABLE" = "dogecoind" ]; then
    # shellcheck disable=SC2086
    exec dogecoind -printtoconsole $ENV_ARGS "$@"
else
    # shellcheck disable=SC2086
    exec "$EXECUTABLE" $ENV_ARGS "$@"
fi
