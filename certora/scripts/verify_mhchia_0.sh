certoraRun certora/harnesses/RewardsManagerHarness.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    --verify RewardsManagerHarness:certora/specs/Badger_mhchia_0.spec \
    --solc solc8.10 \
    --optimistic_loop \
    --cloud \
    --loop_iter 1 \
    --packages @oz=certora/openzeppelin/contracts \
    --send_only \
    --msg "verify_mhchia_0 $1"
