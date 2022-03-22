import "rewardsHarnessMethods.spec"

// STATUS - verified
// check correctness of startNextEpoch() method
rule startNextEpochCheck(method f, env e){
    uint256 epochId = to_uint256(currentEpoch() + 1);

    startNextEpoch(e);

    uint256 epochStartAfter = getEpochsStartTimestamp(epochId);
    uint256 epochEndAfter = getEpochsEndTimestamp(epochId);

    assert epochStartAfter == e.block.timestamp, "wrong start";
    assert epochEndAfter == e.block.timestamp + SECONDS_PER_EPOCH(), "wrong end";
}


// ### Variable Transitions

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

    env e;
    calldataarg args;
    f(e, args);

    uint256 totalSupplyAfter = getTotalSupply(epochId, vault);
    assert totalSupplyAfter > totalSupplyBefore => (
        f.selector == accrueVault(uint256, address).selector ||
        // Since `accrueVault` is called underneath in the following methods
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

// ### High-Level Properties

// points is non-decreasing
rule pointsNonDecreasing(method f, uint256 epochId, address vault, address user)
filtered {
    f -> !f.isView
}
{
    uint256 userPointsBefore = getPoints(epochId, vault, user);

    env e;
    calldataarg args;
    f(e, args);

    uint256 userPointsAfter = getPoints(epochId, vault, user);

    assert (
        (userPointsAfter >= userPointsBefore) ||
        // Except for the case claimBulkTokensOverMultipleEpochsOptimized set the points to 0.
        (userPointsBefore != 0 && userPointsAfter == 0 && f.selector == claimBulkTokensOverMultipleEpochsOptimized(uint256, uint256, address, address[]).selector)
    );
}

// pointsWithdrawn <= points
// invariant pointsWithdrawnNotGreaterThanPoints(uint256 epochId, address vault, address user, address token)
//     getPointsWithdrawn(epochId, vault, user, token) <=
// {
//     uint256 userPointsBefore = getPoints(epochId, vault, user);

//     env e;
//     calldataarg args;
//     f(e, args);

//     uint256 userPointsAfter = getPoints(epochId, vault, user);

//     assert userPointsAfter >= userPointsBefore;
// }


// rule totalPointsNonDecreasing(method f, uint256 epochId, address vault)
// filtered {
//     f -> !f.isView
// }
// {
//     uint256 totalPointsBefore = getTotalPoints(epochId, vault);

//     env e;
//     calldataarg args;
//     f(e, args);

//     uint256 totalPointsAfter = getTotalPoints(epochId, vault);

//     assert totalPointsAfter >= totalPointsBefore;
// }

// ### `totalSupply = sum(shares)`
ghost sumOfAllShares(uint256, address) returns uint256 {
    init_state axiom forall uint256 _epochId. forall address _vault. forall address _user. sumOfAllShares(_epochId, _vault) == 0;
}

hook Sstore shares[KEY uint256 epochId][KEY address vault][KEY address user] uint256 new_shares
    // the old value ↓ already there
    (uint256 old_shares) STORAGE {

    havoc sumOfAllShares assuming forall uint256 _epochId. forall address _vault. forall address _user. (
        ((epochId == _epochId && vault == _vault && user == _user) => (sumOfAllShares@new(_epochId, _vault) == (sumOfAllShares@old(_epochId, _vault) + new_shares - old_shares))) &&
        ((epochId != _epochId || vault != _vault || user != _user) => sumOfAllShares@new(_epochId, _vault) == sumOfAllShares@old(_epochId, _vault))
    );
}

invariant totalSupply_GE_to_sumOfAllShares(uint256 epochId, address vault, address user)
    getTotalSupply(epochId, vault) == sumOfAllShares(epochId, vault)


// // ### `totalPoints = sum(points)`
// ghost sumOfAllPoints(uint256, address) returns uint256 {
//     init_state axiom forall uint256 _epochId. forall address _vault. forall address _user. sumOfAllPoints(_epochId, _vault) == 0;
// }

// hook Sstore points[KEY uint256 epochId][KEY address vault][KEY address user] uint256 new_points
//     // the old value ↓ already there
//     (uint256 old_points) STORAGE {

//     havoc sumOfAllPoints assuming forall uint256 _epochId. forall address _vault. forall address _user. (
//         ((epochId == _epochId && vault == _vault && user == _user) => (sumOfAllPoints@new(_epochId, _vault) == (sumOfAllPoints@old(_epochId, _vault) + new_points - old_points))) &&
//         ((epochId != _epochId || vault != _vault || user != _user) => sumOfAllPoints@new(_epochId, _vault) == sumOfAllPoints@old(_epochId, _vault))
//     );
// }

// invariant totalSupply_GE_to_sumOfAllPoints(uint256 epochId, address vault, address user)
//     getTotalPoints(epochId, vault) == sumOfAllPoints(epochId, vault)
