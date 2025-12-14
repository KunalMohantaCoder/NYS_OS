"""
Byte-Pair Encoding (BPE) tokenizer implementation.
"""
import re
import json
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional
import os


class BPETokenizer:
    """
    Byte-Pair Encoding tokenizer for text preprocessing.
    
    Args:
        vocab_size: Target vocabulary size
        special_tokens: List of special tokens (e.g., ['<pad>', '<unk>', '<bos>', '<eos>'])
    """
    
    def __init__(self, vocab_size: int = 10000, special_tokens: Optional[List[str]] = None):
        self.vocab_size = vocab_size
        self.special_tokens = special_tokens or ['<pad>', '<unk>', '<bos>', '<eos>']
        self.word_freqs = Counter()
        self.splits = {}
        self.merges = []
        self.vocab = {}
        self.inverse_vocab = {}
        
    def _get_word_freqs(self, texts: List[str]):
        """Extract word frequencies from texts."""
        self.word_freqs = Counter()
        for text in texts:
            words = text.split()
            self.word_freqs.update(words)
    
    def _get_splits(self, word: str) -> List[str]:
        """Split word into characters with end-of-word marker."""
        return list(word) + ['</w>']
    
    def _compute_pair_freqs(self, splits: Dict[str, List[str]]) -> Counter:
        """Compute frequency of adjacent pairs in splits."""
        pair_freqs = Counter()
        for word, word_splits in splits.items():
            for i in range(len(word_splits) - 1):
                pair = (word_splits[i], word_splits[i + 1])
                pair_freqs[pair] += self.word_freqs[word]
        return pair_freqs
    
    def _merge_pair(self, pair: Tuple[str, str], splits: Dict[str, List[str]]):
        """Merge a pair in all splits."""
        new_splits = {}
        bigram = re.escape(' '.join(pair))
        pattern = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
        
        for word in splits:
            new_word = pattern.sub(''.join(pair), ' '.join(splits[word]))
            new_splits[word] = new_word.split()
        return new_splits
    
    def train(self, texts: List[str]):
        """
        Train BPE tokenizer on texts.
        
        Args:
            texts: List of training texts
        """
        # Get word frequencies
        self._get_word_freqs(texts)
        
        # Initialize splits
        splits = {word: self._get_splits(word) for word in self.word_freqs.keys()}
        
        # Initialize vocabulary with special tokens and characters
        vocab = set()
        for token in self.special_tokens:
            vocab.add(token)
        
        for word in self.word_freqs.keys():
            for char in word:
                vocab.add(char)
        vocab.add('</w>')
        
        # BPE training
        num_merges = self.vocab_size - len(vocab)
        self.merges = []
        
        for i in range(num_merges):
            pair_freqs = self._compute_pair_freqs(splits)
            if not pair_freqs:
                break
            
            best_pair = max(pair_freqs, key=pair_freqs.get)
            splits = self._merge_pair(best_pair, splits)
            self.merges.append(best_pair)
            vocab.add(''.join(best_pair))
        
        # Build vocabulary
        self.vocab = {token: idx for idx, token in enumerate(sorted(vocab))}
        self.inverse_vocab = {idx: token for token, idx in self.vocab.items()}
        
        # Add merged tokens to vocabulary
        for pair in self.merges:
            merged = ''.join(pair)
            if merged not in self.vocab:
                self.vocab[merged] = len(self.vocab)
                self.inverse_vocab[len(self.inverse_vocab)] = merged
    
    def _apply_bpe(self, word: str) -> List[str]:
        """Apply BPE merges to a word."""
        if word in self.splits:
            return self.splits[word]
        
        splits = self._get_splits(word)
        
        for pair in self.merges:
            bigram = re.escape(' '.join(pair))
            pattern = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
            splits = pattern.sub(''.join(pair), ' '.join(splits)).split()
        
        self.splits[word] = splits
        return splits
    
    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """
        Encode text to token IDs.
        
        Args:
            text: Input text
            add_special_tokens: Whether to add BOS/EOS tokens
        
        Returns:
            List of token IDs
        """
        # Normalize text
        text = text.lower().strip()
        
        # Split into words
        words = text.split()
        
        # Apply BPE to each word
        tokens = []
        if add_special_tokens and '<bos>' in self.vocab:
            tokens.append(self.vocab['<bos>'])
        
        for word in words:
            word_tokens = self._apply_bpe(word)
            for token in word_tokens:
                if token in self.vocab:
                    tokens.append(self.vocab[token])
                elif '<unk>' in self.vocab:
                    tokens.append(self.vocab['<unk>'])
        
        if add_special_tokens and '<eos>' in self.vocab:
            tokens.append(self.vocab['<eos>'])
        
        return tokens
    
    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """
        Decode token IDs to text.
        
        Args:
            token_ids: List of token IDs
            skip_special_tokens: Whether to skip special tokens in output
        
        Returns:
            Decoded text
        """
        tokens = []
        for token_id in token_ids:
            if token_id in self.inverse_vocab:
                token = self.inverse_vocab[token_id]
                if skip_special_tokens and token in self.special_tokens:
                    continue
                tokens.append(token)
        
        # Join tokens and remove end-of-word markers
        text = ''.join(tokens).replace('</w>', ' ')
        return text.strip()
    
    def save(self, path: str):
        """Save tokenizer to file."""
        data = {
            'vocab_size': self.vocab_size,
            'special_tokens': self.special_tokens,
            'merges': self.merges,
            'vocab': self.vocab
        }
        
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, path: str):
        """Load tokenizer from file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tokenizer = cls(
            vocab_size=data['vocab_size'],
            special_tokens=data['special_tokens']
        )
        tokenizer.merges = [tuple(pair) for pair in data['merges']]
        tokenizer.vocab = {k: int(v) for k, v in data['vocab'].items()}
        tokenizer.inverse_vocab = {int(v): k for k, v in data['vocab'].items()}
        
        return tokenizer

