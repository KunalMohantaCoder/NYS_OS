"""
Transformer encoder-decoder architecture.
"""
import torch
import torch.nn as nn
from .attention import MultiHeadAttention, PositionwiseFeedForward
from .embeddings import TokenEmbedding, PositionalEncoding


class EncoderLayer(nn.Module):
    """
    Single encoder layer with self-attention and feed-forward.
    
    Args:
        d_model: Model dimension
        num_heads: Number of attention heads
        d_ff: Feed-forward dimension
        dropout: Dropout probability
    """
    
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = PositionwiseFeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x, mask=None):
        """
        Forward pass through encoder layer.
        
        Args:
            x: Input tensor [batch_size, seq_len, d_model]
            mask: Attention mask
        
        Returns:
            output: Encoded tensor [batch_size, seq_len, d_model]
        """
        # Self-attention with residual connection
        attn_output, _ = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))
        
        # Feed-forward with residual connection
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_output))
        
        return x


class DecoderLayer(nn.Module):
    """
    Single decoder layer with self-attention, cross-attention, and feed-forward.
    
    Args:
        d_model: Model dimension
        num_heads: Number of attention heads
        d_ff: Feed-forward dimension
        dropout: Dropout probability
    """
    
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.cross_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = PositionwiseFeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x, encoder_output, src_mask=None, tgt_mask=None):
        """
        Forward pass through decoder layer.
        
        Args:
            x: Decoder input [batch_size, tgt_len, d_model]
            encoder_output: Encoder output [batch_size, src_len, d_model]
            src_mask: Source attention mask
            tgt_mask: Target attention mask (for causal masking)
        
        Returns:
            output: Decoded tensor [batch_size, tgt_len, d_model]
        """
        # Self-attention with residual connection
        attn_output, _ = self.self_attn(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout(attn_output))
        
        # Cross-attention with residual connection
        cross_attn_output, _ = self.cross_attn(x, encoder_output, encoder_output, src_mask)
        x = self.norm2(x + self.dropout(cross_attn_output))
        
        # Feed-forward with residual connection
        ff_output = self.feed_forward(x)
        x = self.norm3(x + self.dropout(ff_output))
        
        return x


class Encoder(nn.Module):
    """
    Transformer encoder stack.
    
    Args:
        vocab_size: Vocabulary size
        d_model: Model dimension
        num_layers: Number of encoder layers
        num_heads: Number of attention heads
        d_ff: Feed-forward dimension
        max_len: Maximum sequence length
        dropout: Dropout probability
    """
    
    def __init__(self, vocab_size: int, d_model: int, num_layers: int,
                 num_heads: int, d_ff: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        self.token_embedding = TokenEmbedding(vocab_size, d_model)
        self.positional_encoding = PositionalEncoding(d_model, max_len, dropout)
        self.layers = nn.ModuleList([
            EncoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        
    def forward(self, x, mask=None):
        """
        Forward pass through encoder.
        
        Args:
            x: Input token indices [batch_size, seq_len]
            mask: Attention mask
        
        Returns:
            output: Encoded representation [batch_size, seq_len, d_model]
        """
        x = self.token_embedding(x)
        x = self.positional_encoding(x)
        
        for layer in self.layers:
            x = layer(x, mask)
        
        return self.norm(x)


class Decoder(nn.Module):
    """
    Transformer decoder stack.
    
    Args:
        vocab_size: Vocabulary size
        d_model: Model dimension
        num_layers: Number of decoder layers
        num_heads: Number of attention heads
        d_ff: Feed-forward dimension
        max_len: Maximum sequence length
        dropout: Dropout probability
    """
    
    def __init__(self, vocab_size: int, d_model: int, num_layers: int,
                 num_heads: int, d_ff: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        self.token_embedding = TokenEmbedding(vocab_size, d_model)
        self.positional_encoding = PositionalEncoding(d_model, max_len, dropout)
        self.layers = nn.ModuleList([
            DecoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        
    def forward(self, x, encoder_output, src_mask=None, tgt_mask=None):
        """
        Forward pass through decoder.
        
        Args:
            x: Target token indices [batch_size, tgt_len]
            encoder_output: Encoder output [batch_size, src_len, d_model]
            src_mask: Source attention mask
            tgt_mask: Target attention mask (causal mask)
        
        Returns:
            output: Decoded representation [batch_size, tgt_len, d_model]
        """
        x = self.token_embedding(x)
        x = self.positional_encoding(x)
        
        for layer in self.layers:
            x = layer(x, encoder_output, src_mask, tgt_mask)
        
        return self.norm(x)

