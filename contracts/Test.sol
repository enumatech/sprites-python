pragma solidity ^0.4.24;
pragma experimental ABIEncoderV2;

contract Test {

  struct S {
    uint a;
  }
  mapping (int => S) mystructs;

  function Test() public {
    S storage s;
    s.a = 1;
    mystructs[0] = s;
  }

  function incr() public {
    S storage s = mystructs[0];
    s.a = s.a + 1;
  }

  function get() public view returns (uint x) {
      return mystructs[0].a;
  }

  function getStruct() public constant returns (S aStruct) {
    aStruct = mystructs[0];
  }
  function getArrays() public constant returns (uint[2] a, uint[2] b) {
    a[0] = 1;
    a[1] = 2;
    b[0] = 3;
    b[1] = 4;
  }
}
