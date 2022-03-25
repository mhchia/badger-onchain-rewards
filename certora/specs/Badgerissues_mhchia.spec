import "rewardsHarnessMethods.spec"

// NOTE: `addReward` and `addRewards` fail. Add `require(vault != address(0))` in `addReward` to fix it.
invariant rewardsShouldNeverBurned(uint256 epochId, address token)
    // if rewards[epochId][address(0)][user] == N > 0, the rewards `N` cannot be redeemed and practically burned.
    getRewards(epochId, 0, token) == 0
