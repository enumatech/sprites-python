with import (
  builtins.fetchTarball {
    url = "https://releases.nixos.org/nixpkgs/nixpkgs-18.09pre147700.03e47c388ac/nixexprs.tar.xz";
    sha256 = "06prf50w9w5qkrjhxgj7dkwwxfanh9akv3qfb6ibh8mqp1jmnwqm";
  }
) {};

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
