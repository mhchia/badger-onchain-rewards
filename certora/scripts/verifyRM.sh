certoraRun certora/harnesses/RewardsManagerHarness.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    --verify RewardsManagerHarness:certora/specs/itsLikeAReward.spec \
    --solc solc8.10 \
    --optimistic_loop \
    --cloud \
    --loop_iter 2 \
    --packages @oz=certora/openzeppelin/contracts \
    --rule "$1" \
    --msg "$1 with 2 loops"
