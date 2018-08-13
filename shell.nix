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
  # LC_ALL="en_US.UTF-8";
  buildInputs = [
    autoconf
    automake
    coreutils
    direnv
    entr
    go-ethereum
    gmp
    grc
    jq
    libffi
    libtool
    openssl
    overmind
    pipenv
    pkgconfig
    secp256k1
    solc
  ];
}
