pragma solidity ^0.4.24;

/// math.sol -- mixin for inline numerical wizardry

contract DSMath {
    function add(uint x, uint y) internal pure returns (uint z) {
        require((z = x + y) >= x);
    }

    function sub(uint x, uint y) internal pure returns (uint z) {
        require((z = x - y) <= x);
    }

    function mul(uint x, uint y) internal pure returns (uint z) {
        require(y == 0 || (z = x * y) / y == x);
    }

    function min(uint x, uint y) internal pure returns (uint z) {
        return x <= y ? x : y;
    }

    function max(uint x, uint y) internal pure returns (uint z) {
        return x >= y ? x : y;
    }

    function imin(int x, int y) internal pure returns (int z) {
        return x <= y ? x : y;
    }

    function imax(int x, int y) internal pure returns (int z) {
        return x >= y ? x : y;
    }

    uint constant WAD = 10 ** 18;

    uint constant RAY = 10 ** 27;

    function wmul(uint x, uint y) internal pure returns (uint z) {
        z = add(mul(x, y), WAD / 2) / WAD;
    }

    function rmul(uint x, uint y) internal pure returns (uint z) {
        z = add(mul(x, y), RAY / 2) / RAY;
    }

    function wdiv(uint x, uint y) internal pure returns (uint z) {
        z = add(mul(x, WAD), y / 2) / y;
    }

    function rdiv(uint x, uint y) internal pure returns (uint z) {
        z = add(mul(x, RAY), y / 2) / y;
    }

    function rpow(uint x, uint n) internal pure returns (uint z) {
        z = n % 2 != 0 ? x : RAY;

        for (n /= 2; n != 0; n /= 2) {
            x = rmul(x, x);

            if (n % 2 != 0) {
                z = rmul(z, x);
            }
        }
    }
}




/// erc20.sol -- API for the ERC20 token standard

contract ERC20Events {
    event Approval(address indexed src, address indexed guy, uint wad);

    event Transfer(address indexed src, address indexed dst, uint wad);
}


contract ERC20 is ERC20Events {
    function totalSupply() public view returns (uint);

    function balanceOf(address guy) public view returns (uint);

    function allowance(address src, address guy) public view returns (uint);

    function approve(address guy, uint wad) public returns (bool);

    function transfer(address dst, uint wad) public returns (bool);

    function transferFrom(
        address src, address dst, uint wad
    ) public returns (bool);
}




/// auth.sol -- Authoriaation framework

contract DSAuthority {
    function canCall(
        address src, address dst, bytes4 sig
    ) public view returns (bool);
}


contract DSAuthEvents {
    event LogSetAuthority (address indexed authority);

    event LogSetOwner     (address indexed owner);
}


contract DSAuth is DSAuthEvents {
    DSAuthority  public  authority;

    address      public  owner;

    function DSAuth() public {
        owner = msg.sender;
        LogSetOwner(msg.sender);
    }

    function setOwner(address owner_)
    public
    auth
    {
        owner = owner_;
        LogSetOwner(owner);
    }

    function setAuthority(DSAuthority authority_)
    public
    auth
    {
        authority = authority_;
        LogSetAuthority(authority);
    }

    modifier auth {
        require(isAuthorized(msg.sender, msg.sig));
        _;
    }

    function isAuthorized(address src, bytes4 sig) internal view returns (bool) {
        if (src == address(this)) {
            return true;
        }
        else if (src == owner) {
            return true;
        }
        else if (authority == DSAuthority(0)) {
            return false;
        }
        else {
            return authority.canCall(src, this, sig);
        }
    }
}




/// note.sol -- the `note' modifier, for logging calls as events

contract DSNote {
    event LogNote(
        bytes4   indexed sig,
        address  indexed guy,
        bytes32  indexed foo,
        bytes32  indexed bar,
        uint wad,
        bytes fax
    ) anonymous;

    modifier note {
        bytes32 foo;
        bytes32 bar;

        assembly {
            foo := calldataload(4)
            bar := calldataload(36)
        }

        LogNote(msg.sig, msg.sender, foo, bar, msg.value, msg.data);

        _;
    }
}




/// stop.sol -- mixin for enable/disable functionality

contract DSStop is DSNote, DSAuth {

    bool public stopped;

    modifier stoppable {
        require(!stopped);
        _;
    }
    function stop() public auth note {
        stopped = true;
    }

    function start() public auth note {
        stopped = false;
    }

}




/// guard.sol -- simple whitelist implementation of DSAuthority

contract DSGuardEvents {
    event LogPermit(
        bytes32 indexed src,
        bytes32 indexed dst,
        bytes32 indexed sig
    );

    event LogForbid(
        bytes32 indexed src,
        bytes32 indexed dst,
        bytes32 indexed sig
    );
}


contract DSGuard is DSAuth, DSAuthority, DSGuardEvents {
    bytes32 constant public ANY = bytes32(uint(- 1));

    mapping(bytes32 => mapping(bytes32 => mapping(bytes32 => bool))) acl;

    function canCall(
        address src_, address dst_, bytes4 sig
    ) public view returns (bool) {
        bytes32 src = bytes32(src_);
        bytes32 dst = bytes32(dst_);

        return acl[src][dst][sig]
        || acl[src][dst][ANY]
        || acl[src][ANY][sig]
        || acl[src][ANY][ANY]
        || acl[ANY][dst][sig]
        || acl[ANY][dst][ANY]
        || acl[ANY][ANY][sig]
        || acl[ANY][ANY][ANY];
    }

    function permit(bytes32 src, bytes32 dst, bytes32 sig) public auth {
        acl[src][dst][sig] = true;
        LogPermit(src, dst, sig);
    }

    function forbid(bytes32 src, bytes32 dst, bytes32 sig) public auth {
        acl[src][dst][sig] = false;
        LogForbid(src, dst, sig);
    }

    function permit(address src, address dst, bytes32 sig) public {
        permit(bytes32(src), bytes32(dst), sig);
    }

    function forbid(address src, address dst, bytes32 sig) public {
        forbid(bytes32(src), bytes32(dst), sig);
    }

}


contract DSGuardFactory {
    mapping(address => bool)  public  isGuard;

    function newGuard() public returns (DSGuard guard) {
        guard = new DSGuard();
        guard.setOwner(msg.sender);
        isGuard[guard] = true;
    }
}




/// roles.sol - roled based authentication

contract DSRoles is DSAuth, DSAuthority
{
    mapping(address => bool) _root_users;

    mapping(address => bytes32) _user_roles;

    mapping(address => mapping(bytes4 => bytes32)) _capability_roles;

    mapping(address => mapping(bytes4 => bool)) _public_capabilities;

    function getUserRoles(address who)
    public
    view
    returns (bytes32)
    {
        return _user_roles[who];
    }

    function getCapabilityRoles(address code, bytes4 sig)
    public
    view
    returns (bytes32)
    {
        return _capability_roles[code][sig];
    }

    function isUserRoot(address who)
    public
    view
    returns (bool)
    {
        return _root_users[who];
    }

    function isCapabilityPublic(address code, bytes4 sig)
    public
    view
    returns (bool)
    {
        return _public_capabilities[code][sig];
    }

    function hasUserRole(address who, uint8 role)
    public
    view
    returns (bool)
    {
        bytes32 roles = getUserRoles(who);
        bytes32 shifted = bytes32(uint256(uint256(2) ** uint256(role)));
        return bytes32(0) != roles & shifted;
    }

    function canCall(address caller, address code, bytes4 sig)
    public
    view
    returns (bool)
    {
        if (isUserRoot(caller) || isCapabilityPublic(code, sig)) {
            return true;
        }
        else {
            bytes32 has_roles = getUserRoles(caller);
            bytes32 needs_one_of = getCapabilityRoles(code, sig);
            return bytes32(0) != has_roles & needs_one_of;
        }
    }

    function BITNOT(bytes32 input) internal pure returns (bytes32 output) {
        return (input ^ bytes32(uint(- 1)));
    }

    function setRootUser(address who, bool enabled)
    public
    auth
    {
        _root_users[who] = enabled;
    }

    function setUserRole(address who, uint8 role, bool enabled)
    public
    auth
    {
        bytes32 last_roles = _user_roles[who];
        bytes32 shifted = bytes32(uint256(uint256(2) ** uint256(role)));
        if (enabled) {
            _user_roles[who] = last_roles | shifted;
        }
        else {
            _user_roles[who] = last_roles & BITNOT(shifted);
        }
    }

    function setPublicCapability(address code, bytes4 sig, bool enabled)
    public
    auth
    {
        _public_capabilities[code][sig] = enabled;
    }

    function setRoleCapability(uint8 role, address code, bytes4 sig, bool enabled)
    public
    auth
    {
        bytes32 last_roles = _capability_roles[code][sig];
        bytes32 shifted = bytes32(uint256(uint256(2) ** uint256(role)));
        if (enabled) {
            _capability_roles[code][sig] = last_roles | shifted;
        }
        else {
            _capability_roles[code][sig] = last_roles & BITNOT(shifted);
        }

    }

}




/// base.sol -- basic ERC20 implementation

contract DSTokenBase is ERC20, DSMath {
    uint256                                            _supply;

    mapping(address => uint256)                       _balances;

    mapping(address => mapping(address => uint256))  _approvals;

    function DSTokenBase(uint supply) public {
        _balances[msg.sender] = supply;
        _supply = supply;
    }

    function totalSupply() public view returns (uint) {
        return _supply;
    }

    function balanceOf(address src) public view returns (uint) {
        return _balances[src];
    }

    function allowance(address src, address guy) public view returns (uint) {
        return _approvals[src][guy];
    }

    function transfer(address dst, uint wad) public returns (bool) {
        return transferFrom(msg.sender, dst, wad);
    }

    function transferFrom(address src, address dst, uint wad)
    public
    returns (bool)
    {
        if (src != msg.sender) {
            _approvals[src][msg.sender] = sub(_approvals[src][msg.sender], wad);
        }

        _balances[src] = sub(_balances[src], wad);
        _balances[dst] = add(_balances[dst], wad);

        Transfer(src, dst, wad);

        return true;
    }

    function approve(address guy, uint wad) public returns (bool) {
        _approvals[msg.sender][guy] = wad;

        Approval(msg.sender, guy, wad);

        return true;
    }
}




/// token.sol -- ERC20 implementation with minting and burning

contract DSToken is DSTokenBase(0), DSStop {

    bytes32  public  symbol;


    function DSToken(bytes32 symbol_) public {
        symbol = symbol_;
    }

    event Mint(address indexed guy, uint wad);

    event Burn(address indexed guy, uint wad);

    function approve(address guy) public stoppable returns (bool) {
        return super.approve(guy, uint(- 1));
    }

    function approve(address guy, uint wad) public stoppable returns (bool) {
        return super.approve(guy, wad);
    }

    function transferFrom(address src, address dst, uint wad)
    public
    stoppable
    returns (bool)
    {
        if (src != msg.sender && _approvals[src][msg.sender] != uint(- 1)) {
            _approvals[src][msg.sender] = sub(_approvals[src][msg.sender], wad);
        }

        _balances[src] = sub(_balances[src], wad);
        _balances[dst] = add(_balances[dst], wad);

        Transfer(src, dst, wad);

        return true;
    }

    function push(address dst, uint wad) public {
        transferFrom(msg.sender, dst, wad);
    }

    function pull(address src, uint wad) public {
        transferFrom(src, msg.sender, wad);
    }

    function move(address src, address dst, uint wad) public {
        transferFrom(src, dst, wad);
    }

    function mint(uint wad) public {
        mint(msg.sender, wad);
    }

    function burn(uint wad) public {
        burn(msg.sender, wad);
    }

    function mint(address guy, uint wad) public auth stoppable {
        _balances[guy] = add(_balances[guy], wad);
        _supply = add(_supply, wad);
        Mint(guy, wad);
    }

    function burn(address guy, uint wad) public auth stoppable {
        if (guy != msg.sender && _approvals[guy][msg.sender] != uint(- 1)) {
            _approvals[guy][msg.sender] = sub(_approvals[guy][msg.sender], wad);
        }

        _balances[guy] = sub(_balances[guy], wad);
        _supply = sub(_supply, wad);
        Burn(guy, wad);
    }

    bytes32   public  name = "";

    function setName(bytes32 name_) public auth {
        name = name_;
    }
}




/// multivault.sol -- vault for holding different kinds of ERC20 tokens

contract DSMultiVault is DSAuth {
    function push(ERC20 token, address dst, uint wad) public auth {
        require(token.transfer(dst, wad));
    }

    function pull(ERC20 token, address src, uint wad) public auth {
        require(token.transferFrom(src, this, wad));
    }

    function push(ERC20 token, address dst) public {
        push(token, dst, token.balanceOf(this));
    }

    function pull(ERC20 token, address src) public {
        pull(token, src, token.balanceOf(src));
    }

    function mint(DSToken token, uint wad) public auth {
        token.mint(wad);
    }

    function burn(DSToken token, uint wad) public auth {
        token.burn(wad);
    }

    function mint(DSToken token, address guy, uint wad) public auth {
        token.mint(guy, wad);
    }

    function burn(DSToken token, address guy, uint wad) public auth {
        token.burn(guy, wad);
    }

    function burn(DSToken token) public auth {
        token.burn(token.balanceOf(this));
    }
}




/// vault.sol -- vault for holding a single kind of ERC20 tokens

contract DSVault is DSMultiVault {
    ERC20  public  token;

    function swap(ERC20 token_) public auth {
        token = token_;
    }

    function push(address dst, uint wad) public {
        push(token, dst, wad);
    }

    function pull(address src, uint wad) public {
        pull(token, src, wad);
    }

    function push(address dst) public {
        push(token, dst);
    }

    function pull(address src) public {
        pull(token, src);
    }

    function mint(uint wad) public {
        super.mint(DSToken(token), wad);
    }

    function burn(uint wad) public {
        super.burn(DSToken(token), wad);
    }

    function burn() public {
        burn(DSToken(token));
    }
}




/// exec.sol - base contract used by anything that wants to do "untyped" calls

contract DSExec {
    function tryExec(address target, bytes calldata, uint value)
    internal
    returns (bool call_ret)
    {
        return target.call.value(value)(calldata);
    }

    function exec(address target, bytes calldata, uint value)
    internal
    {
        if (!tryExec(target, calldata, value)) {
            revert();
        }
    }

    function exec(address t, bytes c)
    internal
    {
        exec(t, c, 0);
    }

    function exec(address t, uint256 v)
    internal
    {
        bytes memory c;
        exec(t, c, v);
    }

    function tryExec(address t, bytes c)
    internal
    returns (bool)
    {
        return tryExec(t, c, 0);
    }

    function tryExec(address t, uint256 v)
    internal
    returns (bool)
    {
        bytes memory c;
        return tryExec(t, c, v);
    }
}




/// thing.sol - `auth` with handy mixins. your things should be DSThings

contract DSThing is DSAuth, DSNote, DSMath {
}
