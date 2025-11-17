# winnowing.py
import re
from typing import List, Tuple

class WinnowingProcessor:
    def __init__(self, k=50, w=100):
        self.k = k
        self.w = w

    def preprocess_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w]", "", text)
        return text

    def rolling_hash(self, text: str, base=101, mod=1000000007) -> List[Tuple[int, int]]:
        if len(text) < self.k:
            return []
        base = 1000000007
        mod = 2**64 - 1
        base_pow = 1
        for _ in range(self.k - 1):
            base_pow = (base_pow * base) % mod

        # Initial hash
        hash_val = 0
        for i in range(self.k):
            hash_val = (hash_val * base + ord(text[i])) % mod

        hashes = [(hash_val, 0)]

        for i in range(1, len(text) - self.k + 1):
            hash_val = (hash_val - ord(text[i - 1]) * base_pow) % mod
            if hash_val < 0:
                hash_val += mod
            hash_val = (hash_val * base + ord(text[i + self.k - 1])) % mod
            hashes.append((hash_val, i))

        return hashes

    def rolling_hash_double(self, text: str) -> List[Tuple[str, int]]:
        hashes1 = self.rolling_hash(text, base=101, mod=1000000007)
        hashes2 = self.rolling_hash(text, base=103, mod=1000000009)
        return [(f"{h1:x}{h2:x}", pos) for (h1, pos), (h2, _) in zip(hashes1, hashes2)]

    def winnowing(self, hashes: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Chọn fingerprints từ hashes bằng thuật toán Winnowing (chuẩn từ code thứ hai)."""
        if len(hashes) < self.w:
            return hashes if hashes else []
        fingerprints = []
        for i in range(len(hashes) - self.w + 1):
            window = hashes[i : i + self.w]
            min_hash = min(window, key=lambda x: (int(x[0], 16) if isinstance(x[0], str) else x[0], -x[1]))
            if not fingerprints or fingerprints[-1] != min_hash:
                fingerprints.append(min_hash)
        return fingerprints

    def generate_fingerprints(self, text: str, preprocessed=False) -> List[Tuple[str, int]]:
        if not preprocessed:
            text = self.preprocess_text(text)
        hashes = self.rolling_hash_double(text)
        fingerprints = self.winnowing(hashes)
        return fingerprints