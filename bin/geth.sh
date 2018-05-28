#!/usr/bin/env bash

KEYSTORE=$(dirname "$0")/../keystore
ACCOUNTS=$($(dirname "$0")/keystore.sh "$KEYSTORE")

set -x

geth \
    --dev \
    --networkid 60 \
    --keystore "$KEYSTORE" \
    --unlock "$ACCOUNTS" \
    --password /dev/null \
    --verbosity 1 \
    --nousb \
    --ipcdisable \
    --rpc \
    --rpcaddr 0.0.0.0 \
    --rpccorsdomain "*" \
    --rpcapi shh,personal,net,eth,web3 \
    --ws \
    --wsaddr 0.0.0.0 \
    --wsorigins "*" \
    --wsapi shh,personal,net,eth,web3,txpool \
    --shh
