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

// Invariant as rule: pointsWithdrawn <= points
rule pointsWithdrawnNotGreaterThanPoints(method f, uint256 epochId, address vault, address user, address token)
filtered {
    f -> (
        !f.isView &&
        // Don't check `claimBulkTokensOverMultipleEpochsOptimized` since it deletes `points`.
        f.selector != claimBulkTokensOverMultipleEpochsOptimized(uint256, uint256, address, address[]).selector
    )
}
{
    require getPointsWithdrawn(epochId, vault, user, token) <= getPoints(epochId, vault, user);

    env e;
    calldataarg args;

    f(e, args);

    assert getPointsWithdrawn(epochId, vault, user, token) <= getPoints(epochId, vault, user);
}


// NOTE: It's very slow, like 5xx seconds.
// Has more points, claim more tokens.
rule morePointsAndClaimMoreRewards(uint256 epochId, address vault, address token, address user0, address user1)
{
    require user0 != user1 && user1 != currentContract;

    env e;

    // Assume users and vault are well accrued.
    accrueUser(e, epochId, vault, user0);
    accrueUser(e, epochId, vault, user1);
    accrueVault(e, epochId, vault);

    uint256 user0PointsWithdrawn = getPointsWithdrawn(epochId, vault, user0, token);
    uint256 user1PointsWithdrawn = getPointsWithdrawn(epochId, vault, user1, token);
    // Only consider the case that points are not withdrawn at all.
    require user0PointsWithdrawn == 0 && user1PointsWithdrawn == 0;

    uint256 user0Points = getPoints(epochId, vault, user0);
    uint256 user1Points = getPoints(epochId, vault, user1);
    require user0Points >= user1Points;


    uint256 user0TokenBalanceBefore = tokenBalanceOf(token, user0);
    uint256 user1TokenBalanceBefore = tokenBalanceOf(token, user1);

    claimReward(e, epochId, vault, token, user0);
    claimReward(e, epochId, vault, token, user1);

    uint256 user0TokenBalanceAfter = tokenBalanceOf(token, user0);
    uint256 user1TokenBalanceAfter = tokenBalanceOf(token, user1);

    // Avoid underflow
    require user0TokenBalanceAfter >= user0TokenBalanceBefore;
    require user1TokenBalanceAfter >= user1TokenBalanceBefore;

    uint256 user0Rewards = user0TokenBalanceAfter - user0TokenBalanceBefore;
    uint256 user1Rewards = user1TokenBalanceAfter - user1TokenBalanceBefore;

    assert user0Rewards >= user1Rewards;
}


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


// NOTE: `addReward` and `addRewards` fail. Add `require(vault != address(0))` in `addReward` to fix it.
invariant rewardsCantBeBurned(uint256 epochId, address token)
    // if rewards[epochId][0][user] != 0, the rewards cannot be redeemed and practically burned.
    getRewards(epochId, 0, token) == 0


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
