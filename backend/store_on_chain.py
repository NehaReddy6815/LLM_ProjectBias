import json
import sqlite3
import hashlib
from datetime import datetime
from web3 import Web3, Account

# ------------------------------
# Configuration
# ------------------------------
# Replace with your Ganache / Ethereum RPC
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# ✅ Updated middleware injection for web3.py v6+
# Only inject if you're using a PoA network (like some testnets)
# For Ganache, you typically don't need this middleware
# w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

# Replace with your private key (ensure it's 0x-prefixed)
private_key = "0x175256ca6ae74782b302e6f774b9ef2c4cd66180a96bdf852d6181d58339b1c8"
account = Account.from_key(private_key).address

# Load ABI from file
with open("contract_abi.json") as f:
    contract_abi = json.load(f)

contract_address = "0x7EF2e0048f5bAeDe046f6BF797943daF4ED8CB47"
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# ------------------------------
# SQLite setup
# ------------------------------
DB_PATH = "records.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS records (
    record_hash TEXT PRIMARY KEY,
    prompt TEXT,
    output TEXT,
    bias_category TEXT,
    bias_score_before REAL,
    bias_score_after REAL,
    stored_on_chain INTEGER DEFAULT 0
)
""")
conn.commit()

# ------------------------------
# Function to store records on-chain
# ------------------------------
def store_on_chain(records):
    """
    records: list of dicts with keys:
        prompt, output, bias_category, bias_score_before, bias_score_after
    Returns list of tx hashes
    """
    tx_hashes = []

    for idx, record in enumerate(records):
        prompt = record["prompt"]
        output = record["output"]
        bias_category = record.get("bias_category", "")
        bias_score_before = int(record.get("bias_score_before", 0))
        bias_score_after = int(record.get("bias_score_after", 0))

        # Generate record hash
        record_hash = hashlib.sha256(f"{prompt}{output}{datetime.now()}".encode()).hexdigest()
        # Convert to bytes32
        record_hash_bytes32 = bytes.fromhex(record_hash[:64])

        # Check if already exists
        c.execute("SELECT * FROM records WHERE record_hash=?", (record_hash,))
        exists = c.fetchone() is not None

        # Optional off-chain pointer (IPFS example)
        off_chain = "ipfs://exampleCID"

        # Build transaction
        tx = contract.functions.storeRecord(
            record_hash_bytes32,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            bias_category,
            bias_score_before,
            bias_score_after,
            off_chain
        ).build_transaction({
            "from": account,
            "nonce": w3.eth.get_transaction_count(account),
            "gas": 3000000,
            "gasPrice": w3.to_wei("20", "gwei")
        })

        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)

        # Insert or update SQLite
        if exists:
            c.execute("UPDATE records SET stored_on_chain=1 WHERE record_hash=?", (record_hash,))
        else:
            c.execute("""
                INSERT INTO records 
                (record_hash, prompt, output, bias_category, bias_score_before, bias_score_after, stored_on_chain)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (record_hash, prompt, output, bias_category, bias_score_before, bias_score_after))
        conn.commit()

        print(f"✅ Stored record {idx+1} with hash {record_hash}")
        tx_hashes.append(tx_hash.hex())

    return tx_hashes