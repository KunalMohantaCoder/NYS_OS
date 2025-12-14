"""
Dataset loading and preprocessing for training.
"""
import torch
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple, Optional
import os
import sys

# Handle both relative and absolute imports
try:
    from .tokenizer import BPETokenizer
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from training.tokenizer import BPETokenizer


class ConversationDataset(Dataset):
    """
    Dataset for conversation pairs.
    
    Args:
        pairs: List of (input, output) text pairs
        tokenizer: BPE tokenizer instance
        max_len: Maximum sequence length
        pad_idx: Padding token index
    """
    
    def __init__(self, pairs: List[Tuple[str, str]], tokenizer: BPETokenizer,
                 max_len: int = 512, pad_idx: int = 0):
        self.pairs = pairs
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.pad_idx = pad_idx
    
    def __len__(self):
        return len(self.pairs)
    
    def __getitem__(self, idx):
        src_text, tgt_text = self.pairs[idx]
        
        # Encode source and target
        src_ids = self.tokenizer.encode(src_text, add_special_tokens=True)
        tgt_ids = self.tokenizer.encode(tgt_text, add_special_tokens=True)
        
        # Truncate if too long
        src_ids = src_ids[:self.max_len - 1]
        tgt_ids = tgt_ids[:self.max_len - 1]
        
        # Create target input (shifted by one for teacher forcing)
        tgt_input = [self.tokenizer.vocab.get('<bos>', 1)] + tgt_ids[:-1]
        tgt_output = tgt_ids
        
        # Pad sequences
        src_ids = self._pad_sequence(src_ids, self.max_len)
        tgt_input = self._pad_sequence(tgt_input, self.max_len)
        tgt_output = self._pad_sequence(tgt_output, self.max_len)
        
        return {
            'src': torch.tensor(src_ids, dtype=torch.long),
            'tgt_input': torch.tensor(tgt_input, dtype=torch.long),
            'tgt_output': torch.tensor(tgt_output, dtype=torch.long)
        }
    
    def _pad_sequence(self, sequence: List[int], max_len: int) -> List[int]:
        """Pad sequence to max_len."""
        if len(sequence) >= max_len:
            return sequence[:max_len]
        return sequence + [self.pad_idx] * (max_len - len(sequence))


def load_text_file(file_path: str) -> List[str]:
    """
    Load texts from a file (one per line or paragraph).
    
    Args:
        file_path: Path to text file
    
    Returns:
        List of texts
    """
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by paragraphs or lines
    texts = [para.strip() for para in content.split('\n\n') if para.strip()]
    if not texts:
        texts = [line.strip() for line in content.split('\n') if line.strip()]
    
    return texts


def create_data_loader(pairs: List[Tuple[str, str]], tokenizer: BPETokenizer,
                      batch_size: int = 32, max_len: int = 512,
                      shuffle: bool = True, pad_idx: int = 0) -> DataLoader:
    """
    Create a DataLoader for training.
    
    Args:
        pairs: List of (input, output) pairs
        tokenizer: BPE tokenizer
        batch_size: Batch size
        max_len: Maximum sequence length
        shuffle: Whether to shuffle data
        pad_idx: Padding token index
    
    Returns:
        DataLoader instance
    """
    dataset = ConversationDataset(pairs, tokenizer, max_len, pad_idx)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=0,  # Set to 0 for Windows compatibility
        pin_memory=True if torch.cuda.is_available() else False
    )

