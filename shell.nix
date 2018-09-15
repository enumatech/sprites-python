let
  pkgs = import <nixpkgs> { };
  pinnedNixpkgs = pkgs.lib.importJSON ./nixpkgs.json;
in
with import (
  builtins.fetchTarball {
    url = pinnedNixpkgs.url;
    sha256 = pinnedNixpkgs.sha256;
  }
) { };

mkShell rec {

  buildInputs = [
    autoconf
    automake
    coreutils
    direnv
    entr
    glibcLocales
    go-ethereum
    gmp
    grc
    jq
    libffi
    libtool
    locale
    openssl
    # overmind
    (callPackage ./hivemind.nix { })
    pipenv
    pkgconfig
    secp256k1
    solc
  ];

  shellHook = ''
  # Inside docker or with 'nix-shell --pure' we need to set a locale to
  # prevent python CLIs that depend on 'click' (e. g. pipenv) from failing.
  if [ -z "$LANG" ]; then
    export LANG="en_US.UTF-8"
  fi
  '';
}
