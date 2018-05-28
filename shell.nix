with import (
  builtins.fetchTarball {
   # Tue Apr 17 15:50:00 HKT 2018 pipenv 11.10.0
    url = "https://github.com/sveitser/nixpkgs/archive/835e86adfd33b10858751bf329a43e67ae89761f.tar.gz";
    sha256 = "129wvirbp43n8hkz0lywzhdv1sa2cjxs4lwr7wasq7p3sa2zms6b";
  }
) {};

let
  geth = (lib.getBin go-ethereum);

in mkShell rec {
  # LC_ALL="en_US.UTF-8";
  buildInputs = [
    autoconf
    automake
    coreutils
    entr
    geth
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
