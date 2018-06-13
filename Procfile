geth: bin/geth.sh
solc: trap exit INT; while true; do (find ./ -name '*.sol'; ls .solc-colors bin/solc.sh) | entr -d bin/solc.sh "contracts/*.sol"; done
# pytest: trap exit INT; while true; do (find ./ -name '*.py'; ls out/contracts.json) | entr -d pytest; done
pygen: (find ./ -name '*.py'; echo out/contracts.json) | entr bin/python_code_gen.sh
