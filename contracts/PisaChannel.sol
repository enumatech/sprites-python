// Author: Patrick McCorry 
// State channel construction from https://eprint.iacr.org/2018/582 
// Can be used for any state channel application - assuming it implements the transition function 

pragma solidity ^0.4.7;

interface Application {

    // Our state channel can only interact with the application via the transition function.
    // We send over the state, list of signers, commands and input for command.
    // i.e. signers[0], cmds[0], inputs[0] relates to a single command.
    // TODO: Convert creditsA, creditsB to a "bytes" state.
    function transition(uint256 creditsA, uint256 creditsB, address[] signers, uint32[] cmds, uint256[] inputs) external returns(bool, address[]);
}

contract StateChannel {
    address[] public players;
    mapping (address => bool) playermap; // List of players in this channel!

    enum Status { PENDING, OK, DISPUTE }

    // Configuration for state channel
    uint256 disputePeriod;  // Minimum time for dispute process (time all parties have to submit a command)
    address public app; // Application we are interested in.

    // Current status for channel
    Status public status;
    uint256 public bestRound = 0;
    uint256 public t_start;
    uint256 public deadline;
    bytes32 public hstate;

    // Stores values for a single dispute
    mapping (address => bool) sent_cmd; // Who has submitted a command this round?
    address[] public signers; // List of signers
    uint256[] public inputs; // List of inputs for each cmd
    uint32[] public cmds; // List of cmds

    // List of disputes (i.e. successful state transitions on-chain)
    struct Dispute {
        uint256 round;
        uint256 t_start;
        uint256 t_settle;
    }

    Dispute[] disputes;

    event EventInput (address indexed player, uint32 cmd, uint256 _input);
    event EventDispute (uint256 indexed deadline);
    event EventResolve (uint256 indexed bestround);
    event EventEvidence (uint256 indexed bestround, bytes32 hstate);

    modifier before (uint256 T) { if (T == 0 || block.number <  T) _; else revert(); }
    modifier onlyplayers { if (playermap[msg.sender]) _; else revert(); }


    // Here we set up the state channel, list of parties, address of appplication and minimum dispute period
    constructor(address[] _players, address _application, uint _disputePeriod) {
        for (uint i = 0; i < _players.length; i++) {
            players.push(_players[i]);
            playermap[_players[i]] = true;
        }

        app = _application;
        disputePeriod = _disputePeriod;
    }

    // Accept a single command from the signer
    function input(uint32 _cmd, uint256 _input) onlyplayers public {
        // Only accept a single command during a dispute
        require( status == Status.DISPUTE && !sent_cmd[msg.sender]);

        // Store signer, input and their command.
        signers.push(msg.sender);
        inputs.push(_input);
        cmds.push(_cmd);
        sent_cmd[msg.sender] = true;

        // Tell the world we have stored a new command for this signer
        emit EventInput(msg.sender, _cmd, _input);
    }


    // Store a state hash that was authorised by all parties in the state channel
    // This cancels any disputes in progress if it is associated with the largest nonce seen so far.
    function setstate(uint256[] sigs, uint256 _i, bytes32 _hstate) public {
        require(_i > bestRound);

        // Commitment to signed message for new state hash.
        bytes32 h = keccak256(_i, _hstate, address(this));

        // Check all parties in channel have signed it.
        for (uint i = 0; i < players.length; i++) {
            uint8 V = uint8(sigs[i*3+0])+27;
            bytes32 R = bytes32(sigs[i*3+1]);
            bytes32 S = bytes32(sigs[i*3+2]);
            verifySignature(players[i], h, V, R, S);
        }

        // Cancel all commands
        for(i = 0; i < signers.length; i++) {
            sent_cmd[signers[i]] = false;
        }

        // Clear array of commands/inputs/signers
        // TODO: Double-check that "delete" command allows future .pushes
        delete signers;
        delete inputs;
        delete cmds;

        // Store new state!
        bestRound = _i;
        hstate = _hstate;
        status = Status.OK;

        // Tell the world about the new state!
        emit EventEvidence(bestRound, hstate);
    }

    // Only a player-signed transaction can trigger a dispute
    function triggerdispute(uint256[3] sig) onlyplayers public {
        require( status == Status.OK );

        uint8 V = uint8(sig[0])+27;
        bytes32 R = bytes32(sig[1]);
        bytes32 S = bytes32(sig[2]);

        // Signed message is: "dispute", hstate for bestRound, channel address.
        bytes32 h = keccak256("dispute", hstate, bestRound, address(this));
        verifySignature(msg.sender, h, V, R, S);

        // Trigger dispute!
        status = Status.DISPUTE;
        t_start = block.number;
        deadline = block.number + disputePeriod;
        emit EventDispute(deadline);
    }

    function resolve(uint256 _creditsA, uint256 _creditsB, uint _r) onlyplayers public {
        require( block.number > deadline); // Dispute process should be finished?
        require(keccak256(_creditsA, _creditsB, _r) == hstate); // Is this the expected state?

        if (status == Status.DISPUTE) {
            bool success;
            address[] memory new_players;

            // Execute the transition. Fetch new list of participants (perhaps someone was added!) and whether it was successful
            // NOTE: It is up to the application how commands are processed! We can't decide at this level.
            (success, new_players) = Application(app).transition(_creditsA, _creditsB, signers, cmds, inputs);

            // Did everything go to plan?
            if(success) {

              // Remove old players
              for(uint i=0; i<players.length; i++) {
                  playermap[players[i]] = false;
              }

              // Update new players
              players = new_players;
              for(i=0; i<players.length; i++) {
                  playermap[players[i]] = true;
              }

              // Return to normal operations and update bestRound
              status = Status.OK;
              bestRound = bestRound + 1;

              // Store dispute... due to successful on-chain transition
              disputes.push(Dispute(bestRound, t_start, deadline));

              emit EventResolve(bestRound);
            }
        }
    }

    // Helper function to verify signatures
    function verifySignature(address pub, bytes32 h, uint8 v, bytes32 r, bytes32 s) public pure {
        address _signer = ecrecover(h,v,r,s);
        if (pub != _signer) revert();
    }

    // How many disputes have been recorded?
    function disputeLength() public view returns (uint) {
        return disputes.length;
    }

    // Fetch a dispute.
    function getDispute(uint i) public view returns (uint256, uint256, uint256) {
        return (disputes[i].round, disputes[i].t_start, disputes[i].t_settle);
    }

    // Latest round in contract
    function latestClaim() public view returns(uint) {
        return bestRound;
    }
}
