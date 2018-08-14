class DSAuth:
    def __init__(self, contract):
        self._contract = contract

    def authority(self):
        return self._contract.functions.authority()

    def owner(self):
        return self._contract.functions.owner()

    def setAuthority(self, authority_):
        return self._contract.functions.setAuthority(authority_)

    def setOwner(self, owner_):
        return self._contract.functions.setOwner(owner_)


class DSAuthEvents:
    def __init__(self, contract):
        self._contract = contract


class DSAuthority:
    def __init__(self, contract):
        self._contract = contract

    def canCall(self, src, dst, sig):
        return self._contract.functions.canCall(src, dst, sig)


class DSExec:
    def __init__(self, contract):
        self._contract = contract


class DSGuard:
    def __init__(self, contract):
        self._contract = contract

    def ANY(self):
        return self._contract.functions.ANY()

    def authority(self):
        return self._contract.functions.authority()

    def canCall(self, src_, dst_, sig):
        return self._contract.functions.canCall(src_, dst_, sig)

    def forbid(self, src, dst, sig):
        return self._contract.functions.forbid(src, dst, sig)

    def owner(self):
        return self._contract.functions.owner()

    def permit(self, src, dst, sig):
        return self._contract.functions.permit(src, dst, sig)

    def setAuthority(self, authority_):
        return self._contract.functions.setAuthority(authority_)

    def setOwner(self, owner_):
        return self._contract.functions.setOwner(owner_)


class DSGuardEvents:
    def __init__(self, contract):
        self._contract = contract


class DSGuardFactory:
    def __init__(self, contract):
        self._contract = contract

    def isGuard(self, arg):
        return self._contract.functions.isGuard(arg)

    def newGuard(self):
        return self._contract.functions.newGuard()


class DSMath:
    def __init__(self, contract):
        self._contract = contract


class DSMultiVault:
    def __init__(self, contract):
        self._contract = contract

    def authority(self):
        return self._contract.functions.authority()

    def burn(self, token, guy, wad):
        return self._contract.functions.burn(token, guy, wad)

    def mint(self, token, guy, wad):
        return self._contract.functions.mint(token, guy, wad)

    def owner(self):
        return self._contract.functions.owner()

    def pull(self, token, src, wad):
        return self._contract.functions.pull(token, src, wad)

    def push(self, token, dst, wad):
        return self._contract.functions.push(token, dst, wad)

    def setAuthority(self, authority_):
        return self._contract.functions.setAuthority(authority_)

    def setOwner(self, owner_):
        return self._contract.functions.setOwner(owner_)


class DSNote:
    def __init__(self, contract):
        self._contract = contract


class DSRoles:
    def __init__(self, contract):
        self._contract = contract

    def authority(self):
        return self._contract.functions.authority()

    def canCall(self, caller, code, sig):
        return self._contract.functions.canCall(caller, code, sig)

    def getCapabilityRoles(self, code, sig):
        return self._contract.functions.getCapabilityRoles(code, sig)

    def getUserRoles(self, who):
        return self._contract.functions.getUserRoles(who)

    def hasUserRole(self, who, role):
        return self._contract.functions.hasUserRole(who, role)

    def isCapabilityPublic(self, code, sig):
        return self._contract.functions.isCapabilityPublic(code, sig)

    def isUserRoot(self, who):
        return self._contract.functions.isUserRoot(who)

    def owner(self):
        return self._contract.functions.owner()

    def setAuthority(self, authority_):
        return self._contract.functions.setAuthority(authority_)

    def setOwner(self, owner_):
        return self._contract.functions.setOwner(owner_)

    def setPublicCapability(self, code, sig, enabled):
        return self._contract.functions.setPublicCapability(code, sig, enabled)

    def setRoleCapability(self, role, code, sig, enabled):
        return self._contract.functions.setRoleCapability(role, code, sig, enabled)

    def setRootUser(self, who, enabled):
        return self._contract.functions.setRootUser(who, enabled)

    def setUserRole(self, who, role, enabled):
        return self._contract.functions.setUserRole(who, role, enabled)


class DSStop:
    def __init__(self, contract):
        self._contract = contract

    def authority(self):
        return self._contract.functions.authority()

    def owner(self):
        return self._contract.functions.owner()

    def setAuthority(self, authority_):
        return self._contract.functions.setAuthority(authority_)

    def setOwner(self, owner_):
        return self._contract.functions.setOwner(owner_)

    def start(self):
        return self._contract.functions.start()

    def stop(self):
        return self._contract.functions.stop()

    def stopped(self):
        return self._contract.functions.stopped()


class DSThing:
    def __init__(self, contract):
        self._contract = contract

    def authority(self):
        return self._contract.functions.authority()

    def owner(self):
        return self._contract.functions.owner()

    def setAuthority(self, authority_):
        return self._contract.functions.setAuthority(authority_)

    def setOwner(self, owner_):
        return self._contract.functions.setOwner(owner_)


class DSToken:
    def __init__(self, contract):
        self._contract = contract

    def allowance(self, src, guy):
        return self._contract.functions.allowance(src, guy)

    def approve(self, guy, wad):
        return self._contract.functions.approve(guy, wad)

    def authority(self):
        return self._contract.functions.authority()

    def balanceOf(self, src):
        return self._contract.functions.balanceOf(src)

    def burn(self, guy, wad):
        return self._contract.functions.burn(guy, wad)

    def mint(self, guy, wad):
        return self._contract.functions.mint(guy, wad)

    def move(self, src, dst, wad):
        return self._contract.functions.move(src, dst, wad)

    def name(self):
        return self._contract.functions.name()

    def owner(self):
        return self._contract.functions.owner()

    def pull(self, src, wad):
        return self._contract.functions.pull(src, wad)

    def push(self, dst, wad):
        return self._contract.functions.push(dst, wad)

    def setAuthority(self, authority_):
        return self._contract.functions.setAuthority(authority_)

    def setName(self, name_):
        return self._contract.functions.setName(name_)

    def setOwner(self, owner_):
        return self._contract.functions.setOwner(owner_)

    def start(self):
        return self._contract.functions.start()

    def stop(self):
        return self._contract.functions.stop()

    def stopped(self):
        return self._contract.functions.stopped()

    def symbol(self):
        return self._contract.functions.symbol()

    def totalSupply(self):
        return self._contract.functions.totalSupply()

    def transfer(self, dst, wad):
        return self._contract.functions.transfer(dst, wad)

    def transferFrom(self, src, dst, wad):
        return self._contract.functions.transferFrom(src, dst, wad)


class DSTokenBase:
    def __init__(self, contract):
        self._contract = contract

    def allowance(self, src, guy):
        return self._contract.functions.allowance(src, guy)

    def approve(self, guy, wad):
        return self._contract.functions.approve(guy, wad)

    def balanceOf(self, src):
        return self._contract.functions.balanceOf(src)

    def totalSupply(self):
        return self._contract.functions.totalSupply()

    def transfer(self, dst, wad):
        return self._contract.functions.transfer(dst, wad)

    def transferFrom(self, src, dst, wad):
        return self._contract.functions.transferFrom(src, dst, wad)


class DSVault:
    def __init__(self, contract):
        self._contract = contract

    def authority(self):
        return self._contract.functions.authority()

    def burn(self, token, guy, wad):
        return self._contract.functions.burn(token, guy, wad)

    def mint(self, token, guy, wad):
        return self._contract.functions.mint(token, guy, wad)

    def owner(self):
        return self._contract.functions.owner()

    def pull(self, token, src, wad):
        return self._contract.functions.pull(token, src, wad)

    def push(self, token, dst, wad):
        return self._contract.functions.push(token, dst, wad)

    def setAuthority(self, authority_):
        return self._contract.functions.setAuthority(authority_)

    def setOwner(self, owner_):
        return self._contract.functions.setOwner(owner_)

    def swap(self, token_):
        return self._contract.functions.swap(token_)

    def token(self):
        return self._contract.functions.token()


class ERC20:
    def __init__(self, contract):
        self._contract = contract

    def allowance(self, src, guy):
        return self._contract.functions.allowance(src, guy)

    def approve(self, guy, wad):
        return self._contract.functions.approve(guy, wad)

    def balanceOf(self, guy):
        return self._contract.functions.balanceOf(guy)

    def totalSupply(self):
        return self._contract.functions.totalSupply()

    def transfer(self, dst, wad):
        return self._contract.functions.transfer(dst, wad)

    def transferFrom(self, src, dst, wad):
        return self._contract.functions.transferFrom(src, dst, wad)


class ERC20Events:
    def __init__(self, contract):
        self._contract = contract
