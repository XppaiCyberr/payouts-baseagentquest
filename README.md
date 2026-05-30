# Base MCP + Payouts Plugin

A local BaseAgentQuest plugin for preparing and executing bundled ETH payouts on Base.

Have you ever hated doing payouts manually—sending transactions one by one and signing every single transfer?

I definitely did back when I was managing my Axie scholarship program.

This plugin turns a simple `payouts.csv` file into a validated Base MCP `send_calls` payload, allowing an agent to prepare multiple payouts and submit them through a single coordinated approval flow.

The workflow is powered by Base Smart Wallet and EIP-5792 transaction batching, enabling multiple onchain actions to be bundled into a smoother user experience.

---

## Features

* Read payout data from CSV
* Validate recipient addresses
* Validate ETH amounts
* Skip already processed payouts
* Detect duplicate recipients
* Convert ETH to wei automatically
* Generate Base MCP `send_calls` payloads
* Review total payout amount before execution
* Compatible with Base Mainnet (`8453`)
* Designed for AI agents and Base MCP workflows

---

## Why?

Managing payouts manually is repetitive and error-prone.

Typical examples:

* Axie scholarship rewards
* Community incentives
* Contributor payments
* Grant distributions
* Quest rewards
* Treasury operations

Instead of:

```text
Send → Sign
Send → Sign
Send → Sign
Send → Sign
```

You can:

```text
Prepare CSV
↓
Validate recipients
↓
Review totals
↓
Generate send_calls
↓
Approve bundled request
```

---

## How It Works

The plugin scans `payouts.csv` and includes only rows that:

* Have `Status = Pending`
* Use `ETH`
* Have no existing `TxHash`
* Contain a valid EVM address
* Contain a positive amount

Each valid row becomes a native ETH transfer call:

```json
{
  "to": "0x...",
  "value": "0x...",
  "data": "0x"
}
```

The resulting payload can be passed directly to Base MCP:

```json
{
  "chain": "base",
  "calls": [...]
}
```

---

## CSV Format

```csv
Name,Address,Amount,Currency,TxHash,Date,Status
Alice,0x...,0.01,ETH,,2026-05-01,Pending
Bob,0x...,0.02,ETH,,2026-05-02,Pending
```

---

## Usage

```bash
python ./scripts/build_payout_calls.py ./payouts.csv --include-skipped
```

Example:

```bash
python ./scripts/build_payout_calls.py ./payouts.csv --chain base
```

---

## Agent Workflow

1. Detect wallet using Base MCP `get_wallets`
2. Read and validate `payouts.csv`
3. Show:

   * recipient count
   * total ETH
   * skipped rows
   * validation errors
4. Request user confirmation
5. Execute `send_calls`
6. Wait for confirmation
7. Update CSV records after success

---

## Safety Rules

The plugin intentionally stops when:

* Addresses are invalid
* Amounts are invalid
* Pending addresses are duplicated
* Unsupported currencies are detected
* Required columns are missing

Never:

* Send rows that already contain a `TxHash`
* Change chains automatically
* Update payout records before confirmation

---

## EIP-5792 + Smart Wallets

This plugin becomes significantly more powerful when used with Base Smart Wallet.

EIP-5792 introduces a standard interface for wallets to handle bundled transaction requests (`wallet_sendCalls`), allowing applications and AI agents to coordinate multiple onchain actions with fewer approval prompts.

Instead of signing every payout individually, the wallet can process a batch of transfers through a single user approval flow, creating a much better experience for treasury management, rewards distribution, and community operations.

---

## Ideal Use Cases

* Axie Scholarship payouts
* Community reward programs
* DAO contributor payments
* Quest rewards
* Grant distributions
* Creator payouts
* Treasury operations

---

## Disclaimer

Always verify recipient addresses, payout amounts, and the connected wallet before approving any transaction. Blockchain transactions are irreversible once confirmed.
