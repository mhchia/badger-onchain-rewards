import "rewardsHarnessMethods.spec"


definition MAX_UINT256() returns uint256 =
	0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;

definition PRECISION() returns uint256 =
	1000000000000000000;


/*
    Unit-Tests
*/

rule integrityOfClaimReward(uint256 epochId, address vault, address token, address user)
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

// // points *
// rule rewardsCanBeClaimedCorrectly(uint256 epochId, address token, uint256 amount, address user) {
//     require token != 0 && amount > 0;

//     accrueUser(e, epochId, vault, user0);
//     accrueVault(e, epochId, vault);
//     uint256 userPointsWithdrawn = getPointsWithdrawn(epochId, vault, user, token);

//     uint256 userPoints = getPoints(epochId, vault, user);

//     // Only consider the case that points are not withdrawn at all.
//     require userPoints >= userPointsWithdrawn;


//     addReward(epochId, vault, token, amount);

//     assert
// }
