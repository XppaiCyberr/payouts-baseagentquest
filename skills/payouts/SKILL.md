---
name: payouts
description: Prepare bundled native ETH payouts from a local payouts.csv file and execute them through Base MCP send_calls.
---

# Payouts Plugin

> [!IMPORTANT]
> ## STOP - COMPLETE BASE MCP ONBOARDING BEFORE USING THIS PLUGIN
>
> Before preparing or sending payouts, you MUST complete the Base MCP onboarding flow:
> 1. Call `get_wallets` to detect the user's wallet.
> 2. Present wallet status and the Base MCP disclaimer.
>
> The sender wallet is only confirmed during detection. Never prepare or submit payout calls before this step.

Payouts reads a local `payouts.csv`, converts pending ETH payout rows into native transfer calls, and executes the full batch through Base MCP's `send_calls` so the user approves one bundled transaction request.

Supported chain: Base mainnet (`8453` / `0x2105`, `chain="base"`).

Supported payout currency: native `ETH`.

## CSV Format

The CSV must include these headers:

```csv
Name,Address,Amount,Currency,TxHash,Date,Status
```

Rows are included only when:

- `Status` is `Pending`.
- `Currency` is `ETH`.
- `TxHash` is empty.
- `Address` is a valid `0x` EVM address.
- `Amount` is a positive decimal ETH value.

Rows with a non-empty `TxHash` are already recorded and must not be sent again.

## Prepare Command

Use the local helper script from this plugin:

```powershell
python C:\Users\xppaicyber\plugins\payouts\scripts\build_payout_calls.py .\payouts.csv
```

Optional flags:

```powershell
python C:\Users\xppaicyber\plugins\payouts\scripts\build_payout_calls.py .\payouts.csv --chain base --include-skipped
```

The script returns JSON:

```json
{
  "ok": true,
  "chain": "base",
  "totalWei": "0x0",
  "totalEth": "0",
  "transactions": [
    {
      "step": "payout",
      "name": "Alice Smith",
      "to": "0x...",
      "value": "0x...",
      "data": "0x",
      "chainId": 8453
    }
  ]
}
```

## send_calls Mapping

Pass every `transactions[*]` to `send_calls` in the same order:

```json
{
  "chain": "base",
  "calls": [
    {
      "to": "<tx.to>",
      "value": "<tx.value>",
      "data": "<tx.data>"
    }
  ]
}
```

## Orchestration Pattern

1. Call `get_wallets` and identify the sender wallet.
2. Read and validate `payouts.csv` using the prepare command.
3. Show the user the recipient count and total ETH.
4. Ask for explicit confirmation before sending.
5. Call `send_calls(chain="base", calls=[...])` with all payout calls.
6. Give the approval link to the user.
7. Poll `get_request_status(requestId)` until confirmed or failed.
8. After confirmation, help update `TxHash` and `Status` in `payouts.csv` only if the user asks.

## Safety Rules

- Never send rows that are not `Pending`.
- Never send rows with an existing `TxHash`.
- Never silently change the chain from Base mainnet.
- Never update `payouts.csv` before the transaction is confirmed.
- If the CSV contains unsupported currencies, invalid addresses, duplicate pending addresses, or invalid amounts, stop and show the validation errors.
