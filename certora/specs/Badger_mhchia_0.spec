import "rewardsHarnessMethods.spec"

/*
    Valid State
*/

rule epochTimeDoesntChangeAfterStarted(method f, uint256 epochId)
filtered {
    f -> !f.isView
}
{
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
    //     // totalSupply should only be increased in 1) `handleDeposit`, otherwise 2) by
    //     // updated from the previous epochs.
    //     !shouldUpdate ? (
    //         // 1) due to `handleDeposit`
    //         f.selector == handleDeposit(address, address, uint256).selector
    //     ):(
    //         // 2) due to updated from previous epochs
    //         f.selector == handleDeposit(address, address, uint256).selector ||
    //         f.selector == accrueVault(uint256, address).selector ||
    //         // Since `accrueVault` is called underneath in the following methods
    //         f.selector == notifyTransfer(address, address, uint256).selector ||
    //         f.selector == handleWithdrawal(address, address, uint256).selector ||
    //         f.selector == handleTransfer(address, address, address, uint256).selector ||
    //         f.selector == claimReward(uint256, address, address, address).selector ||
    //         f.selector == claimRewards(uint256[], address[], address[], address[]).selector ||
    //         f.selector == claimBulkTokensOverMultipleEpochs(uint256,uint256,address,address[],address).selector ||
    //         f.selector == claimBulkTokensOverMultipleEpochsOptimized(uint256, uint256, address, address[]).selector
    //     )
    // );
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

// rule totalPointsIncreased(method f, uint256 epochId, address vault)
// filtered {
//     f -> !f.isView
// }
// {
//     uint256 totalPointsBefore = getTotalPoints(epochId, vault);

//     env e;
//     calldataarg args;
//     f(e, args);

//     uint256 totalPointsAfter = getTotalPoints(epochId, vault);

//     assert totalPointsAfter > totalPointsBefore => (
//         f.selector == claimReward(uint256, address, address, address).selector ||
//         f.selector == claimRewards(uint256[], address[], address[], address[]).selector ||
//         f.selector == claimBulkTokensOverMultipleEpochs(uint256,uint256,address,address[],address).selector ||
//         f.selector == claimBulkTokensOverMultipleEpochsOptimized(uint256, uint256, address, address[]).selector
//     );
// }

