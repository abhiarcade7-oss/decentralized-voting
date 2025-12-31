# backend/services/blockchain_service.py

from web3 import Web3
import json
import os


class BlockchainService:
    def __init__(self):
        # Ganache RPC (Docker / Local)
        self.rpc_url = os.getenv("RPC_URL", "http://voting-ganache:8545")
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))

        # -------- Locate contract JSON (ABI + Bytecode) --------
        possible_paths = [
            "/app/backend/contract/ManagedElection.json",
            "/app/contract/ManagedElection.json",
            "backend/contract/ManagedElection.json",
            "contract/ManagedElection.json",
        ]

        json_path = None
        for p in possible_paths:
            if os.path.exists(p):
                json_path = p
                break

        if not json_path:
            raise Exception("❌ ManagedElection.json NOT FOUND!")

        with open(json_path, "r") as f:
            data = json.load(f)

        # Remix / Hardhat JSON compatibility
        if isinstance(data, list):
            self.abi = data
            self.bytecode = None
        else:
            self.abi = data.get("abi", [])
            self.bytecode = data.get("bytecode")

    # =====================================================
    # DEPLOY CONTRACT (NO CONSTRUCTOR ARGUMENT)
    # =====================================================
    def deploy_contract(self, owner, private_key):
        if not self.bytecode:
            raise Exception("❌ No bytecode found")

        owner = Web3.to_checksum_address(owner)

        contract = self.web3.eth.contract(
            abi=self.abi,
            bytecode=self.bytecode
        )

        txn = contract.constructor().build_transaction({
            "from": owner,
            "nonce": self.web3.eth.get_transaction_count(owner),
            "gas": 6000000,
            "gasPrice": self.web3.to_wei("10", "gwei"),
        })

        signed = self.web3.eth.account.sign_transaction(txn, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

        return receipt.contractAddress, tx_hash.hex()

    # =====================================================
    # LOAD DEPLOYED CONTRACT
    # =====================================================
    def load_contract(self, address):
        return self.web3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=self.abi
        )

    # =====================================================
    # ADD CANDIDATE (BLOCKCHAIN) ✅ FIXED ORDER
    # =====================================================
    def add_candidate(self, contract_address, name, owner, private_key):
        contract = self.load_contract(contract_address)
        owner = Web3.to_checksum_address(owner)

        txn = contract.functions.addCandidate(name).build_transaction({
            "from": owner,
            "nonce": self.web3.eth.get_transaction_count(owner),
            "gas": 300000,
            "gasPrice": self.web3.to_wei("10", "gwei"),
        })

        signed = self.web3.eth.account.sign_transaction(txn, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed.raw_transaction)
        self.web3.eth.wait_for_transaction_receipt(tx_hash)

        # 🔥 THIS IS IMPORTANT
        candidate_id = contract.functions.candidateCount().call()

        return candidate_id


    # =====================================================
    # DEACTIVATE CANDIDATE (OPTIONAL BUT SUPPORTED)
    # =====================================================
    def deactivate_candidate(self, contract_address, owner, private_key, candidate_id):
        contract = self.load_contract(contract_address)
        owner = Web3.to_checksum_address(owner)

        txn = contract.functions.deactivateCandidate(
            int(candidate_id)
        ).build_transaction({
            "from": owner,
            "nonce": self.web3.eth.get_transaction_count(owner),
            "gas": 200000,
            "gasPrice": self.web3.to_wei("10", "gwei"),
        })

        signed = self.web3.eth.account.sign_transaction(txn, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed.raw_transaction)
        self.web3.eth.wait_for_transaction_receipt(tx_hash)

        return tx_hash.hex()

    # =====================================================
    # CAST VOTE (CORE FUNCTION)
    # =====================================================
    def vote(self, voter_hash, candidate_id, contract_address, owner, private_key):
        contract = self.load_contract(contract_address)
        owner = Web3.to_checksum_address(owner)

        # voter_hash → bytes32
        if isinstance(voter_hash, str):
            if voter_hash.startswith("0x"):
                voter_hash = voter_hash[2:]
            voter_hash = Web3.to_bytes(hexstr="0x" + voter_hash)

        if len(voter_hash) != 32:
            raise ValueError("voter_hash must be exactly 32 bytes")

        candidate_id = int(candidate_id)

        txn = contract.functions.vote(
            voter_hash,
            candidate_id
        ).build_transaction({
            "from": owner,
            "nonce": self.web3.eth.get_transaction_count(owner),
            "gas": 300000,
            "gasPrice": self.web3.to_wei("10", "gwei"),
        })

        signed = self.web3.eth.account.sign_transaction(txn, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed.raw_transaction)
        self.web3.eth.wait_for_transaction_receipt(tx_hash)

        return tx_hash.hex()

    # =====================================================
    # GET RESULTS (VOTE COUNT ONLY)
    # =====================================================
    def get_results(self, contract_address):
        contract = self.load_contract(contract_address)
        count = contract.functions.candidateCount().call()

        results = []
        for i in range(1, count + 1):
            c = contract.functions.candidates(i).call()
            results.append({
                "candidate_id": i,
                "name": c[1],        # string name
                "voteCount": c[2],   # uint votes
                "isActive": c[3]
            })

        return results


    # =====================================================
    # DEPLOY NEW ELECTION CONTRACT (HELPER)
    # =====================================================
    def deploy_new_election_contract(self):
        owner = os.getenv("OWNER_ADDRESS")
        private_key = os.getenv("PRIVATE_KEY")

        if not owner or not private_key:
            raise Exception("OWNER_ADDRESS or PRIVATE_KEY missing")

        return self.deploy_contract(owner, private_key)
