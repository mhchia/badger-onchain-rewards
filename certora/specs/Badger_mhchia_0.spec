import "rewardsHarnessMethods.spec"

/*
    Valid State
*/

definition rewardsManagerInitialized() returns bool = currentEpoch() != 0;

invariant allTimestampsAreZeroWhenUnintialized(uint256 epochId)
    !rewardsManagerInitialized() => getEpochsStartTimestamp(epochId) == 0 && getEpochsEndTimestamp(epochId) == 0


rule epochTimeDoesntChangeAfterStarted(method f, uint256 epochId)
filtered {
    f -> !f.isView
}
{
    require rewardsManagerInitialized();
    require currentEpoch() == epochId;
    require epochHasStarted(epochId);

    uint256 epochStartTimeBefore = getEpochsStartTimestamp(epochId);
    uint256 epochEndTimeBefore = getEpochsEndTimestamp(epochId);

    env e;
    calldataarg args;
    f(e, args);

    uint256 epochStartTimeAfter = getEpochsStartTimestamp(epochId);
    uint256 epochEndTimeAfter = getEpochsEndTimestamp(epochId);
    assert epochStartTimeBefore == epochStartTimeAfter && epochEndTimeBefore == epochEndTimeAfter;
}


/*
    State Transitions
*/

definition epochYetStarted(uint256 epochId) returns bool = (
    getEpochsStartTimestamp(epochId) == 0 &&
    getEpochsEndTimestamp(epochId) == 0
);

definition epochHasStarted(uint256 epochId) returns bool = (
    getEpochsStartTimestamp(epochId) != 0 &&
    getEpochsEndTimestamp(epochId) != 0
);

rule epochStarted(method f, uint256 epochId)
filtered {
    f -> !f.isView
}
{
    require epochYetStarted(epochId);

    env e;
    calldataarg args;
    f(e, args);

    assert epochHasStarted(epochId) => f.selector == startNextEpoch().selector;
}

/*
    Variable Transitions
*/

function shouldUpdateTotalSupply(uint256 epochId, address vault) returns bool {
    uint256 lastTotalSupply; bool _shouldUpdate;
    lastTotalSupply, _shouldUpdate = getTotalSupplyAtEpoch(epochId, vault);
    return _shouldUpdate;
}

rule pointsIncreased(method f, uint256 epochId, address vault, address user)
filtered {
    f -> !f.isView
}
{
    uint256 pointsBefore = getPoints(epochId, vault, user);

    env e;
    calldataarg args;
    f(e, args);

    uint256 pointsAfter = getPoints(epochId, vault, user);
    assert pointsAfter > pointsBefore => (
        f.selector == accrueUser(uint256, address, address).selector ||
        // Since `accrueUser` is called underneath in the following methods
        f.selector == notifyTransfer(address, address, uint256).selector ||
        f.selector == handleDeposit(address, address, uint256).selector ||
        f.selector == handleWithdrawal(address, address, uint256).selector ||
        f.selector == handleTransfer(address, address, address, uint256).selector ||
        f.selector == claimReward(uint256, address, address, address).selector ||
        f.selector == claimRewards(uint256[], address[], address[], address[]).selector ||
        f.selector == claimBulkTokensOverMultipleEpochs(uint256,uint256,address,address[],address).selector ||
        f.selector == claimBulkTokensOverMultipleEpochsOptimized(uint256, uint256, address, address[]).selector
    );
}

rule totalSupplyIncreased(method f, uint256 epochId, address vault)
filtered {
    f -> !f.isView
}
{
    uint256 totalSupplyBefore = getTotalSupply(epochId, vault);
    require !shouldUpdateTotalSupply(epochId, vault);

    env e;
    calldataarg args;
    f(e, args);

    uint256 totalSupplyAfter = getTotalSupply(epochId, vault);
    assert totalSupplyAfter > totalSupplyBefore => (
        f.selector == handleDeposit(address, address, uint256).selector ||
        f.selector == notifyTransfer(address, address, uint256).selector
    );
}

rule pointsWithdrawnIncreased(method f, uint256 epochId, address vault, address userAddress, address rewardToken)
filtered {
    f -> !f.isView
}
{
    uint256 pointsWithdrawnBefore = getPointsWithdrawn(epochId, vault, userAddress, rewardToken);

    env e;
    calldataarg args;
    f(e, args);

    uint256 pointsWithdrawnAfter = getPointsWithdrawn(epochId, vault, userAddress, rewardToken);

    assert pointsWithdrawnAfter > pointsWithdrawnBefore => (
        f.selector == claimReward(uint256, address, address, address).selector ||
        f.selector == claimRewards(uint256[], address[], address[], address[]).selector ||
        f.selector == claimBulkTokensOverMultipleEpochs(uint256,uint256,address,address[],address).selector ||
        f.selector == claimBulkTokensOverMultipleEpochsOptimized(uint256, uint256, address, address[]).selector
    );
}

rule totalPointsIncreased(method f, uint256 epochId, address vault)
filtered {
    f -> (
        !f.isView &&
        f.selector != handleDeposit(address, address, uint256).selector &&
        f.selector != handleWithdrawal(address, address, uint256).selector
    )
}
{
    uint256 totalPointsBefore = getTotalPoints(epochId, vault);

    env e;
    calldataarg args;
    f(e, args);

    uint256 totalPointsAfter = getTotalPoints(epochId, vault);

    assert totalPointsAfter > totalPointsBefore => (
        f.selector == accrueVault(uint256, address).selector ||
        f.selector == notifyTransfer(address, address, uint256).selector ||
        f.selector == claimReward(uint256, address, address, address).selector ||
        f.selector == claimRewards(uint256[], address[], address[], address[]).selector ||
        f.selector == claimBulkTokensOverMultipleEpochs(uint256,uint256,address,address[],address).selector ||
        f.selector == claimBulkTokensOverMultipleEpochsOptimized(uint256, uint256, address, address[]).selector
    );
}


/*
    Unit-Tests
*/


definition MAX_UINT256() returns uint256 =
	0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;

definition PRECISION() returns uint256 =
	1000000000000000000;


rule integrityOfClaimReward(method f, uint256 epochId, address vault, address token, address user)
filtered {
    f -> !f.isView
}
{
    require token != 0 && user != currentContract;

    env e;
    accrueUser(e, epochId, vault, user);
    accrueVault(e, epochId, vault);

    uint256 totalPoints = getTotalPoints(epochId, vault);
    require totalPoints > 0;

    uint256 totalRewards = getRewards(epochId, vault, token);
    uint256 tokenBalanceContractBefore = tokenBalanceOf(token, currentContract);
    require totalRewards >= 0 && totalRewards <= tokenBalanceContractBefore;

    // Only consider the case that points are not withdrawn at all.
    uint256 userPointsWithdrawn = getPointsWithdrawn(epochId, vault, user, token);
    uint256 userPoints = getPoints(epochId, vault, user);
    require userPoints > userPointsWithdrawn;
    uint256 pointsLeft = userPoints - userPointsWithdrawn;

    uint256 tokenBalanceUserBefore = tokenBalanceOf(token, user);
    mathint sumBefore = tokenBalanceContractBefore + tokenBalanceUserBefore;
    require sumBefore <= MAX_UINT256();

    claimReward(e, epochId, vault, token, user);

    uint256 userPointsWithdrawnAfter = getPointsWithdrawn(epochId, vault, user, token);

    uint256 tokenBalanceContractAfter = tokenBalanceOf(token, currentContract);
    uint256 tokenBalanceUserAfter = tokenBalanceOf(token, user);

    mathint sumAfter = tokenBalanceContractAfter + tokenBalanceUserAfter;
    require sumAfter <= MAX_UINT256();

    // Accounting
    assert userPointsWithdrawnAfter == userPoints;
    assert tokenBalanceContractBefore >= tokenBalanceContractAfter;
    assert tokenBalanceUserAfter >= tokenBalanceUserBefore;
    assert sumBefore == sumAfter;
}
