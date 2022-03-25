import "rewardsHarnessMethods.spec"


/*
    Unit-Tests
*/

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
