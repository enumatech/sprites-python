pragma solidity ^0.4.24;

contract MyThrow {
    function MyThrow() public {
    }

    function bar(uint a) public pure returns (uint x) {
        return a;
    }
    function maybe_throw(int a) public pure returns (int x){
      require(a < 5);
      return a;
    }
}
