certoraRun certora/harnesses/RewardsManagerHarness.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    --verify RewardsManagerHarness:certora/specs/sanity.spec \
    --solc solc8.10 \
    --optimistic_loop \
    --loop_iter 1 \
    --cloud \
    --packages @oz=certora/openzeppelin/contracts \
    --rule "$1" \
    --send_only \
    --msg "$1"
