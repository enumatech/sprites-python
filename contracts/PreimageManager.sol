pragma solidity ^0.4.24;

contract PreimageManager {
    mapping ( bytes32 => uint ) timestamp;

    function submitPreimage(bytes32 x) public {
        if (timestamp[keccak256(x)] == 0)
            timestamp[keccak256(x)] = block.number;
    }

    function revealedBefore(bytes32 h, uint T) public view returns (bool) {
        uint t = timestamp[h];
        return (t > 0 && t <= T);
    }
}
