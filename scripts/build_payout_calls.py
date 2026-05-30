#!/usr/bin/env python3
import argparse
import csv
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
WEI_PER_ETH = Decimal("1000000000000000000")
REQUIRED_COLUMNS = ["Name", "Address", "Amount", "Currency", "TxHash", "Date", "Status"]
CHAIN_IDS = {"base": 8453}


def fail(message, details=None):
    payload = {"ok": False, "error": message}
    if details:
        payload["details"] = details
    print(json.dumps(payload, indent=2))
    return 1


def amount_to_wei(raw_amount):
    try:
        amount = Decimal(str(raw_amount).strip())
    except InvalidOperation:
        raise ValueError("amount is not a decimal")
    if amount <= 0:
        raise ValueError("amount must be positive")
    wei = amount * WEI_PER_ETH
    if wei != wei.to_integral_value():
        raise ValueError("amount has more than 18 decimal places")
    return int(wei)


def read_rows(csv_path):
    with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing required columns: {', '.join(missing)}")
        return list(reader)


def build_calls(rows, chain, include_skipped):
    errors = []
    skipped = []
    transactions = []
    pending_addresses = {}
    total_wei = 0

    for index, row in enumerate(rows, start=2):
        status = row.get("Status", "").strip()
        currency = row.get("Currency", "").strip().upper()
        tx_hash = row.get("TxHash", "").strip()
        address = row.get("Address", "").strip()
        name = row.get("Name", "").strip()

        if status.lower() != "pending":
            if include_skipped:
                skipped.append({"row": index, "reason": "status is not Pending", "name": name})
            continue
        if tx_hash:
            if include_skipped:
                skipped.append({"row": index, "reason": "TxHash is already set", "name": name})
            continue
        if currency != "ETH":
            errors.append({"row": index, "error": f"unsupported currency {currency or '<blank>'}"})
            continue
        if not ADDRESS_RE.match(address):
            errors.append({"row": index, "error": "invalid EVM address", "address": address})
            continue
        lowered = address.lower()
        if lowered in pending_addresses:
            errors.append({
                "row": index,
                "error": f"duplicate pending address also used on row {pending_addresses[lowered]}",
                "address": address,
            })
            continue
        pending_addresses[lowered] = index

        try:
            wei = amount_to_wei(row.get("Amount", ""))
        except ValueError as exc:
            errors.append({"row": index, "error": str(exc), "amount": row.get("Amount", "")})
            continue

        total_wei += wei
        transactions.append({
            "step": "payout",
            "row": index,
            "name": name,
            "to": address,
            "value": hex(wei),
            "data": "0x",
            "chainId": CHAIN_IDS[chain],
        })

    if errors:
        return {"ok": False, "error": "CSV validation failed", "details": errors}
    if not transactions:
        return {"ok": False, "error": "No pending ETH payouts found"}

    payload = {
        "ok": True,
        "chain": chain,
        "chainId": CHAIN_IDS[chain],
        "count": len(transactions),
        "totalWei": hex(total_wei),
        "totalEth": format(Decimal(total_wei) / WEI_PER_ETH, "f"),
        "transactions": transactions,
        "calls": [
            {"to": tx["to"], "value": tx["value"], "data": tx["data"]}
            for tx in transactions
        ],
    }
    if include_skipped:
        payload["skipped"] = skipped
    return payload


def main():
    parser = argparse.ArgumentParser(description="Build Base MCP send_calls payload from payouts.csv")
    parser.add_argument("csv_path", nargs="?", default="payouts.csv", help="Path to payouts.csv")
    parser.add_argument("--chain", default="base", choices=sorted(CHAIN_IDS), help="Target chain")
    parser.add_argument("--include-skipped", action="store_true", help="Include skipped rows in output")
    args = parser.parse_args()

    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        return fail(f"CSV file not found: {csv_path}")

    try:
        rows = read_rows(csv_path)
    except Exception as exc:
        return fail(str(exc))

    payload = build_calls(rows, args.chain, args.include_skipped)
    print(json.dumps(payload, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
