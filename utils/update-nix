#!/usr/bin/env nix-shell
#! nix-shell -i bash -p curl jq nix
set -euxo pipefail

commit_sha=$(curl 'https://api.github.com/repos/nixos/nixpkgs/commits?sha=master' | jq -r 'first.sha')
url="https://github.com/nixos/nixpkgs/archive/${commit_sha}.tar.gz"
digest=$(nix-prefetch-url --unpack "$url")
echo "{\"url\": \"${url}\", \"sha256\": \"${digest}\"}" | jq '.' > nixpkgs.json
