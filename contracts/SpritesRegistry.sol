pragma solidity ^0.4.20;
// XXX enable returning structs from internal functions
pragma experimental ABIEncoderV2;

import {DSToken as Token} from "contracts/dappsys.sol";

// External interface
interface PreimageManager {
    function submitPreimage(bytes32 x) external;

    function revealedBefore(bytes32 h, uint T) external returns (bool);
}

// Note: Initial version does NOT support concurrent conditional payments!

contract SpritesRegistry {

    // Blocks for grace period
    uint constant DELTA = 2;

    struct Player {
      address addr;
      int credit;
      uint withdrawal;
      uint withdrawn;
      uint deposit;
    }

    enum Status {OK, PENDING}

    struct Payment {
      uint amount;
      uint expiry;
      address recipient;
      bytes32 preimageHash;
    }

    struct Channel {
      address tokenAddress;

      Player left;
      Player right;

      int bestRound;
      Status status;
      uint deadline;

      // Conditional payment
      Payment payment;
    }


    // Events
    event EventInit(uint channelID);
    event EventUpdate(uint channelID, int round);
    event EventPending(uint channelID, uint start, uint deadline);

    // Utility functions
    modifier onlyplayers (uint channelID){
        Channel storage channel = channels[channelID];
        require( channel.left.addr == msg.sender || channel.right.addr == msg.sender);
        _;
    }

    function max(uint a, uint b) internal pure returns (uint) {if (a > b) return a; else return b;}

    function min(uint a, uint b) internal pure returns (uint) {if (a < b) return a; else return b;}

    // providing this separtely to test from application code
    function recoverAddress(bytes32 messageHash, uint[3] sig) public pure returns (address) {
      uint8 V = uint8(sig[0]);
      bytes32 R = bytes32(sig[1]);
      bytes32 S = bytes32(sig[2]);
      return ecrecover(messageHash, V, R, S);
    }

    function isSignatureOkay(address pub, bytes32 messageHash, uint[3] sig) public pure returns (bool) {
      require(pub == recoverAddress(messageHash, sig));
      return true;
    }

    // Contract global data
    mapping(uint => Channel) public channels;
    PreimageManager pm;
    uint channelCounter;

    function sha3int(int r) public pure returns (bytes32) {
        return keccak256(r);
    }

    function SpritesRegistry(address preimageManagerAddress) public
    {
        pm = PreimageManager(preimageManagerAddress);
        channelCounter = 0;
    }

    function createChannel(address other, address tokenAddress) public returns (uint) {
      uint channelID = channelCounter;

      // using memory here reduces gas cost from ~ 300k to 200k
      Channel memory channel;
      Payment memory payment;

      channel.tokenAddress = tokenAddress;
      channel.left.addr = msg.sender;
      channel.right.addr = other;

      channel.bestRound = -1;
      channel.status = Status.OK;
      channel.deadline = 0; // not sure

      payment.expiry = 0;
      payment.amount = 0;
      payment.preimageHash = bytes32(0);
      payment.recipient =  0;

      channel.payment = payment;

      channels[channelID] = channel;

      channelCounter += 1;

      // can't return from state modifying function
      EventInit(channelID);
    }

    function lookupPlayer(uint channelID) internal view onlyplayers(channelID) returns (Player storage) {
      Channel storage channel = channels[channelID];
      if (channel.left.addr == msg.sender)
        return channel.left;
      else
        return channel.right;
    }

    function lookupOtherPlayer(uint channelID) internal view onlyplayers(channelID) returns (Player storage) {
      Channel storage channel = channels[channelID];
      if (channel.left.addr == msg.sender)
        return channel.right;
      else
        return channel.left;
    }

    // Increment on new deposit
    // user first needs to approve us to transfer tokens
    function deposit(uint channelID, uint amount) public onlyplayers(channelID) returns (bool) {
      Channel storage channel = channels[channelID];
      bool status = Token(channel.tokenAddress).transferFrom(msg.sender, this, amount);

      // return status 0 if transfer failed, 1 otherwise
      require(status == true);

      Player storage player = lookupPlayer(channelID);
      player.deposit += amount;
    }

    function getDeposit(uint channelID) public view returns (uint) {
      return lookupPlayer(channelID).deposit;
    }

    function getStatus(uint channelID) public view returns (Status) {
      return channels[channelID].status;
    }

    function getDeadline(uint channelID) public view returns (uint) {
      return channels[channelID].deadline;
    }

    function getWithdrawn(uint channelID) public view returns (uint) {
      return lookupPlayer(channelID).withdrawn;
    }

    // Increment on withdrawal
    // XXX does currently not support incremental withdrawals
    // XXX check if failing assert undoes all changes made in tx
    function withdraw(uint channelID) public onlyplayers(channelID) {
        Player storage player = lookupPlayer(channelID);
        uint toWithdraw = player.withdrawal - player.withdrawn;
        require(Token(channels[channelID].tokenAddress).transferFrom(this, msg.sender, toWithdraw));
        player.withdrawn = player.withdrawal;
    }

    // XXX the experimental ABI encoder supports return struct, but as of 2018 04 08
    // web3.py does not seem to support decoding structs.
    function getState(uint channelID)
      public constant onlyplayers(channelID)
      returns (
        uint[2] deposits,
        int[2] credits,
        uint[2] withdrawals,
        int bestRound,
        bytes32 preimageHash,
        address recipient,
        uint amount,
        uint expiry
      )
    {
      Player storage player = lookupPlayer(channelID);
      Player storage other = lookupOtherPlayer(channelID);
      // Channel storage channel = channels[channelID];
      Payment storage payment = channels[channelID].payment;

      bestRound = channels[channelID].bestRound;
      preimageHash = payment.preimageHash;
      recipient = payment.recipient;
      amount = payment.amount;
      expiry = payment.expiry;

      deposits[0] = player.deposit;
      deposits[1] = other.deposit;
      credits[0] = player.credit;
      credits[1] = other.credit;
      withdrawals[0] = player.withdrawal;
      withdrawals[1] = other.withdrawal;
    }

    function compute_hash(
        uint channelID,
        int[2] credits,
        uint[2] withdrawals,
        int round,
        bytes32 preimageHash,
        address recipient,
        uint amount,
        uint expiry
    ) private pure returns (bytes32) {

      // message length is 32 * number of (flattened) arguments to keccak
      bytes memory prefix = "\x19Ethereum Signed Message:\n320";
      return keccak256(
        prefix,
        channelID,
        credits,
        withdrawals,
        round,
        preimageHash,
        // Addresses are 20 bytes, but currently the client code
        // pads every input to 32 bytes.
        bytes32(recipient),
        amount,
        expiry
       );
    }

    function verifyUpdate(
        uint channelID,
        uint[3] sig,
        int[2] credits,
        uint[2] withdrawals,
        int round,
        bytes32 preimageHash,
        address recipient,
        uint amount,
        uint expiry
    )
    public onlyplayers(channelID)
    view {

      // Do not allow overpayment.
      // TODO conversion? save math?
      // We can't check for overpayment because the chain state might
      // not be up to date?
      // Verify the update does not include an overpayment needs to be done by client?
      // assert(int(amount) <= int(other.deposit) + credits[0]);

      // Only update to states with larger round number
      require(round > channels[channelID].bestRound);

      // Check the signature of the other party
      bytes32 messageHash = compute_hash(
          channelID, credits, withdrawals, round, preimageHash, recipient, amount, expiry
      );
      Player storage other = lookupOtherPlayer(channelID);
      isSignatureOkay(other.addr, messageHash, sig);
    }

    function update(
        uint channelID,
        uint[3] sig,
        int[2] credits,
        uint[2] withdrawals,
        int round,
        bytes32 preimageHash,
        address recipient,
        uint amount,
        uint expiry
    ) public onlyplayers(channelID)
    {
        verifyUpdate(channelID, sig, credits, withdrawals, round, preimageHash, recipient, amount, expiry);

        updatePayment(channelID, preimageHash, recipient, amount, expiry);
        updatePlayers(channelID, credits, withdrawals);
        updateChannel(channelID, round);

        EventUpdate(channelID, round);
    }

    function updatePlayers(
        uint channelID,
        int[2] credits,
        uint[2] withdrawals
    ) private {

      Player storage player = lookupPlayer(channelID);
      Player storage other = lookupOtherPlayer(channelID);

      // Can only submit a message signed by the _other_ party hence the reverse order.
      player.credit = credits[1];
      player.withdrawal = withdrawals[1];
      other.credit = credits[0];
      other.withdrawal = withdrawals[0];

      // prevent over withdrawals
      // TODO conversion? save math? 
      assert(int(player.withdrawal) <= int(player.deposit) + player.credit);

      // FAIL!
      assert(int(other.withdrawal) <= int(other.deposit) + other.credit);
    }

    function updateChannel(uint channelID, int round) private {
      channels[channelID].bestRound = round;
    }

    function updatePayment(
        uint channelID,
        bytes32 preimageHash,
        address recipient,
        uint amount,
        uint expiry
    ) private {
        Payment storage payment = channels[channelID].payment;
        payment.preimageHash = preimageHash;
        payment.recipient = recipient;
        payment.amount = amount;
        payment.expiry = expiry;
    }

    // Causes a timeout for the finalize time
    function trigger(uint channelID) public onlyplayers(channelID) {
        Channel storage channel = channels[channelID];
        require(channel.status == Status.OK);
        channel.status = Status.PENDING;
        channel.deadline = block.number + DELTA;
        // Set the deadline for collecting inputs or updates
        EventPending(channelID, block.number, channel.deadline);
    }

    function finalize(uint channelID) public onlyplayers(channelID) {
        Channel storage channel = channels[channelID];
        Payment storage payment = channel.payment;

        require(channel.status == Status.PENDING);
        require(block.number > channel.deadline);

        // Finalize is safe to call multiple times
        // If "trigger" occurs before a hashlock expires, finalize will need to be called again
        if (payment.amount > 0 && block.number > payment.expiry) {

            bool revealed = pm.revealedBefore(payment.preimageHash, payment.expiry);
            bool paymentToRight = payment.recipient == channel.right.addr;
            bool sendToRight = (revealed && paymentToRight) || (!revealed && !paymentToRight);
            if (sendToRight) {
                 channel.right.withdrawal += payment.amount;
            } else {
                 channel.left.withdrawal += payment.amount;
            }
            // reset the in-flight payment that is now resolved
            payment.amount = 0;
            payment.preimageHash = bytes32(0);
            payment.expiry = 0;
            payment.recipient = 0x0;
        }

        // Withdraw the maximum amounts left in the channel
        channel.left.withdrawal += uint(int(channel.left.deposit) + channel.left.credit);
        channel.right.withdrawal += uint(int(channel.right.deposit) + channel.right.credit);
        channel.left.credit = - int(channel.left.deposit);
        channel.right.credit = - int(channel.right.deposit);
    }
}
