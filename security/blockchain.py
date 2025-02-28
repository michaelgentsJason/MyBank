import hashlib
import json
import time
from typing import List, Dict, Any, Optional
from utils.logger import bank_logger
from datetime import datetime


class Block:
    """区块链中的单个区块"""

    def __init__(self, index: int, timestamp: float, transactions: List[Dict],
                 previous_hash: str, nonce: int = 0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """计算区块的哈希值"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int) -> None:
        """'挖掘'区块 - 找到满足特定难度的哈希"""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self) -> Dict:
        """将区块转换为字典"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
            "time": datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        }


class Blockchain:
    """简单的区块链实现"""

    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []
        self.difficulty = difficulty
        self.mining_reward = 0

        # 创建创世区块
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        """创建链的第一个区块"""
        genesis_block = Block(0, time.time(), [{"transaction": "Genesis Block"}], "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        bank_logger.info("创世区块已创建")

    def get_latest_block(self) -> Block:
        """获取最新区块"""
        return self.chain[-1]

    def add_transaction(self, transaction: Dict) -> int:
        """将交易添加到待处理列表"""
        self.pending_transactions.append(transaction)
        return self.get_latest_block().index + 1

    def mine_pending_transactions(self) -> Block:
        """挖掘所有待处理交易"""
        if not self.pending_transactions:
            return None

        block = Block(
            len(self.chain),
            time.time(),
            self.pending_transactions.copy(),
            self.get_latest_block().hash
        )

        block.mine_block(self.difficulty)
        self.chain.append(block)
        self.pending_transactions = []
        return block

    def is_chain_valid(self) -> bool:
        """验证区块链的完整性"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # 验证当前区块的哈希
            if current_block.hash != current_block.calculate_hash():
                return False

            # 验证区块链接
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def get_transaction_history(self, account_id: int = None) -> List[Dict]:
        """获取交易历史，可选按账户ID过滤"""
        all_transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if isinstance(tx, dict) and (account_id is None or
                                             (tx.get('from_account_id') == account_id or
                                              tx.get('to_account_id') == account_id)):
                    tx_copy = tx.copy()
                    tx_copy["block_index"] = block.index
                    tx_copy["block_hash"] = block.hash
                    tx_copy["timestamp"] = block.timestamp
                    all_transactions.append(tx_copy)

        return all_transactions

    def get_blocks(self) -> List[Dict]:
        """获取所有区块"""
        return [block.to_dict() for block in self.chain]

    def verify_transaction(self, transaction_id: int) -> Dict:
        """验证交易是否在区块链中且未被篡改"""
        for block in self.chain:
            for tx in block.transactions:
                if isinstance(tx, dict) and tx.get('transaction_id') == transaction_id:
                    # 验证区块的完整性
                    recalculated_hash = block.calculate_hash()
                    is_valid = recalculated_hash == block.hash

                    return {
                        "transaction_found": True,
                        "block_index": block.index,
                        "block_hash": block.hash,
                        "timestamp": block.timestamp,
                        "is_valid": is_valid
                    }

        return {"transaction_found": False}


# 单例模式：全局区块链实例
blockchain_instance = Blockchain(difficulty=2)