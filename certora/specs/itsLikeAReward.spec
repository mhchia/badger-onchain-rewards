import "sanity.spec"

methods {
    // constants
    SECONDS_PER_EPOCH() returns(uint256) envfree // => ALWAYS(604800)
    MAX_BPS() returns(uint256) envfree => ALWAYS(10000)

    // other variables
    currentEpoch() returns(uint256) envfree

    // mapping harness getters
    getEpochsStartTimestamp(uint256) returns(uint256) envfree
    getEpochsEndTimestamp(uint256) returns(uint256) envfree
    getPoints(uint256, address, address) returns(uint256) envfree
    getPointsWithdrawn(uint256, address, address, address) returns(uint256) envfree
    getTotalPoints(uint256, address) returns(uint256) envfree
    getLastAccruedTimestamp(uint256, address) returns(uint256) envfree
    getLastUserAccrueTimestamp(uint256, address, address) returns(uint256) envfree
    getLastVaultDeposit(address) returns(uint256) envfree
    getShares(uint256, address) returns(uint256) envfree
    getTotalSupply(uint256, address) returns(uint256) envfree
    getRewards(uint256 , address, address) returns(uint256) envfree

    // methods
    startNextEpoch()
    accrueVault(uint256, address)
    getVaultTimeLeftToAccrue(uint256, address) returns(uint256)
    claimBulkTokensOverMultipleEpochsOptimized(uint256, uint256, address, address[])
    addRewards(uint256[], address[], address[], uint256[])
    addReward(uint256, address, address, uint256)
    notifyTransfer(address, address, uint256)
    accrueUser(uint256, address, address)
    getUserTimeLeftToAccrue(uint256, address, address) returns(uint256)
    claimRewards(uint256[], address[], address[], address[])
    claimReward(uint256, address, address, address)
    claimBulkTokensOverMultipleEpochs(uint256, uint256, address, address[], address)
    handleDeposit(address, address, uint256)
    handleWithdrawal(address, address, uint256)

    // envfree methods
    getTotalSupplyAtEpoch(uint256, address) returns(uint256, bool) envfree
    handleTransfer(address, address, address, uint256) envfree
    getBalanceAtEpoch(uint256, address, address) returns(uint256, bool) envfree
    requireNoDuplicates(address[]) envfree
    min(uint256, uint256) returns(uint256) envfree
    tokenBalanceOf(address, address) returns(uint256) envfree
}

rule startNextEpochCheck(method f, env e){
    uint256 epochId = to_uint256(currentEpoch() + 1);

    startNextEpoch(e);

    uint256 epochStartAfter = getEpochsStartTimestamp(epochId);
    uint256 epochEndAfter = getEpochsEndTimestamp(epochId);

    assert epochStartAfter == e.block.timestamp, "wrong start";
    assert epochEndAfter == e.block.timestamp + 604800, "wrong end";
}

rule whoChangedMyBalance(address token, address user, method f) {
    uint256 before = tokenBalanceOf(token,user);
    env e;
    calldataarg args;
    f(e,args);
    assert tokenBalanceOf(token,user) == before;
}
