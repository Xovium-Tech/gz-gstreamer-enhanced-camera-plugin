#!/usr/bin/env bash
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DISTRO="${1:-harmonic}"
JOBS="${JOBS:-2}"

if (( $# > 1 )) || [[ ! "$DISTRO" =~ ^(harmonic|jetty)$ ]]; then
    echo "Usage: $0 [harmonic|jetty]" >&2
    exit 2
fi
if [[ ! "$JOBS" =~ ^[1-9][0-9]*$ ]]; then
    echo "JOBS must be a positive integer." >&2
    exit 2
fi

BUILD_DIR="$PLUGIN_ROOT/build-$DISTRO"
cmake -S "$PLUGIN_ROOT" -B "$BUILD_DIR" \
    -DGZ_DISTRO="$DISTRO" -DGST_PLANE_CAMERA_BUILD_PLUGIN=ON \
    -DCMAKE_BUILD_TYPE=Release
cmake --build "$BUILD_DIR" --parallel "$JOBS"

printf '\nBuilt: %s/libGstPlaneCameraSystem.so\n\n' "$BUILD_DIR"
printf 'export GZ_SIM_SYSTEM_PLUGIN_PATH=%q"${GZ_SIM_SYSTEM_PLUGIN_PATH:+:$GZ_SIM_SYSTEM_PLUGIN_PATH}"\n' "$BUILD_DIR"
