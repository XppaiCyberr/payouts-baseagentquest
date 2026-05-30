# Payouts BaseAgentQuest Plugin

Local Codex plugin for preparing bundled native ETH payouts from `payouts.csv`.

The plugin reads pending rows from `payouts.csv`, validates recipient addresses and amounts, converts ETH amounts to wei, and emits a Base MCP `send_calls` batch. Each pending row becomes one native ETH transfer call with `data: "0x"`.

## Usage

```powershell
python .\scripts\build_payout_calls.py .\payouts.csv --include-skipped
```

The output includes:

- `transactions`: ordered payout calls with recipient metadata.
- `calls`: the exact array to pass to Base MCP `send_calls`.
- `totalEth` and `totalWei`: total payout amount.

The installed skill at `skills/payouts/SKILL.md` documents the Base MCP onboarding, confirmation, and `send_calls` workflow.
