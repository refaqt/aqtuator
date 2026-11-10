#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Install the stress analysis tools on Linux: FreeCAD 1.1, Gmsh and the
# CalculiX solver (ccx). The cloud environment and the stress cases in
# modules/*/simulation/cases/ need them.
#
#   bash setup-fem.sh
#
# It is safe to run more than once. It needs micromamba and a network
# connection to conda-forge. On Windows you do not need this file: the
# FreeCAD installer already contains Gmsh and CalculiX.
#
# Prefix: /opt/freecad (change it with FEM_PREFIX=/some/path).
set -euo pipefail

PREFIX="${FEM_PREFIX:-/opt/freecad}"
BIN_DIR="${FEM_BIN_DIR:-/usr/local/bin}"

if ! command -v micromamba >/dev/null 2>&1; then
  echo "micromamba is missing. Install it first: https://mamba.readthedocs.io" >&2
  exit 1
fi

if [ -x "$PREFIX/bin/freecadcmd" ]; then
  if [ ! -x "$PREFIX/bin/ccx" ]; then
    micromamba install -y -p "$PREFIX" -c conda-forge calculix
  fi
else
  micromamba create -y -p "$PREFIX" -c conda-forge "freecad=1.1" calculix
fi

for tool in freecadcmd ccx gmsh; do
  if [ -x "$PREFIX/bin/$tool" ]; then
    ln -sf "$PREFIX/bin/$tool" "$BIN_DIR/$tool"
  fi
done

echo "FreeCAD: $("$BIN_DIR/freecadcmd" --version 2>/dev/null | head -n 1 || true)"
echo "Gmsh:    $("$BIN_DIR/gmsh" --version 2>&1 | head -n 1 || true)"
echo "CalculiX: $(micromamba list -p "$PREFIX" calculix 2>/dev/null | awk '/calculix/ {print $2}')"
