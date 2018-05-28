#!/usr/bin/env bash

if [ -z "$1" ]; then
    KEYSTORE_DIR=$(dirname "$0")/../keystore
else
    KEYSTORE_DIR="$1"
fi

MNEMONIC="network gain army age zebra tuna bracket fire fall section direct stay"

DEPLOYER_PK=e33292da27178504b848586dcee3011a7e21ee6ed96f9df17487fd6518a128c7
ALICE_PK=d8ae722d3a6876fd27907c434968e7373c6fbb985242e545a427531132ef3a71
BOB_PK=28e58f2f6a924d381e243ec1ca4a2239d2b35ebd9a44cec11aead6848a52630b
CHARLIE_PK=8e1733c6774268aee3db54901086b1f642f51e60300674ae3b33f1e1217ec7f5


DEPLOYER=d124b979f746be85706daa1180227e716eafcc5c
ALICE=a49aad37c34e92236690b93e291ae5f10daf7cbe
BOB=b357fc3dbd4cdb7cbd96aa0a0bd905dbe56cab77
CHARLIE=cBE431FF3fdcd4d735df5706e755D0f8726549f0

for PK in DEPLOYER_PK ALICE_PK BOB_PK CHARLIE_PK; do
    echo Importing private key: $PK > /dev/stderr
    geth --verbosity 2 \
        account import \
        --keystore "$KEYSTORE_DIR" \
        --password /dev/null \
        <(echo ${!PK}) \
        >/dev/null
done

# Print comma separated account list for `geth --unlock ...`
echo $(ls "$KEYSTORE_DIR" | sort | head -n 4 | awk -F '--' '{print$3}') | tr ' ' ,
