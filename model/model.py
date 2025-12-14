"""
Complete transformer model for sequence-to-sequence tasks.
"""
import torch
import torch.nn as nn
from .transformer import Encoder, Decoder


class TransformerModel(nn.Module):
    """
    Complete transformer model (encoder-decoder architecture).
    
    Args:
        src_vocab_size: Source vocabulary size
        tgt_vocab_size: Target vocabulary size
        d_model: Model dimension (default: 512)
        num_encoder_layers: Number of encoder layers (default: 6)
        num_decoder_layers: Number of decoder layers (default: 6)
        num_heads: Number of attention heads (default: 8)
        d_ff: Feed-forward dimension (default: 2048)
        max_len: Maximum sequence length (default: 1024)
        dropout: Dropout probability (default: 0.1)
    """
    
    def __init__(self, src_vocab_size: int, tgt_vocab_size: int,
                 d_model: int = 512, num_encoder_layers: int = 6,
                 num_decoder_layers: int = 6, num_heads: int = 8,
                 d_ff: int = 2048, max_len: int = 1024, dropout: float = 0.1):
        super().__init__()
        
        self.d_model = d_model
        self.src_vocab_size = src_vocab_size
        self.tgt_vocab_size = tgt_vocab_size
        
        # Encoder and decoder
        self.encoder = Encoder(
            vocab_size=src_vocab_size,
            d_model=d_model,
            num_layers=num_encoder_layers,
            num_heads=num_heads,
            d_ff=d_ff,
            max_len=max_len,
            dropout=dropout
        )
        
        self.decoder = Decoder(
            vocab_size=tgt_vocab_size,
            d_model=d_model,
            num_layers=num_decoder_layers,
            num_heads=num_heads,
            d_ff=d_ff,
            max_len=max_len,
            dropout=dropout
        )
        
        # Output projection to vocabulary
        self.output_projection = nn.Linear(d_model, tgt_vocab_size)
        
        # Initialize parameters
        self._init_parameters()
        
    def _init_parameters(self):
        """Initialize model parameters."""
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def generate_mask(self, src, tgt, pad_idx=0):
        """
        Generate attention masks for source and target sequences.
        
        Args:
            src: Source sequences [batch_size, src_len]
            tgt: Target sequences [batch_size, tgt_len]
            pad_idx: Padding token index
        
        Returns:
            src_mask: Source mask [batch_size, src_len] (for padding)
            tgt_mask: Target causal mask [batch_size, tgt_len, tgt_len]
            src_padding_mask: Source padding mask [batch_size, src_len]
            tgt_padding_mask: Target padding mask [batch_size, tgt_len]
        """
        batch_size = src.size(0)
        src_len = src.size(1)
        tgt_len = tgt.size(1)
        
        # Source padding mask [batch_size, src_len]
        src_padding_mask = (src != pad_idx)
        src_mask = src_padding_mask  # [batch, src_len]
        
        # Target padding mask [batch_size, tgt_len]
        tgt_padding_mask = (tgt != pad_idx)
        
        # Target causal mask (prevents looking at future tokens)
        tgt_causal_mask = torch.tril(torch.ones(tgt_len, tgt_len, device=tgt.device)).bool()
        # Combine padding and causal mask
        tgt_mask = tgt_padding_mask.unsqueeze(1) & tgt_causal_mask.unsqueeze(0)  # [batch, tgt_len, tgt_len]
        
        return src_mask, tgt_mask, src_padding_mask, tgt_padding_mask
    
    def forward(self, src, tgt, src_mask=None, tgt_mask=None):
        """
        Forward pass through the model.
        
        Args:
            src: Source sequences [batch_size, src_len]
            tgt: Target sequences [batch_size, tgt_len]
            src_mask: Source attention mask (optional)
            tgt_mask: Target attention mask (optional)
        
        Returns:
            output: Logits over target vocabulary [batch_size, tgt_len, tgt_vocab_size]
        """
        # Encode source
        encoder_output = self.encoder(src, src_mask)
        
        # Decode target
        decoder_output = self.decoder(tgt, encoder_output, src_mask, tgt_mask)
        
        # Project to vocabulary
        output = self.output_projection(decoder_output)
        
        return output
    
    def count_parameters(self):
        """Count the number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def save(self, path: str):
        """Save model to file."""
        torch.save({
            'model_state_dict': self.state_dict(),
            'src_vocab_size': self.src_vocab_size,
            'tgt_vocab_size': self.tgt_vocab_size,
            'd_model': self.d_model,
            'config': {
                'num_encoder_layers': self.encoder.layers.__len__(),
                'num_decoder_layers': self.decoder.layers.__len__(),
                'num_heads': self.encoder.layers[0].self_attn.num_heads,
                'd_ff': self.encoder.layers[0].feed_forward.linear1.out_features,
            }
        }, path)
    
    @classmethod
    def load(cls, path: str, device='cpu'):
        """Load model from file."""
        checkpoint = torch.load(path, map_location=device)
        config = checkpoint['config']
        
        model = cls(
            src_vocab_size=checkpoint['src_vocab_size'],
            tgt_vocab_size=checkpoint['tgt_vocab_size'],
            d_model=checkpoint['d_model'],
            num_encoder_layers=config['num_encoder_layers'],
            num_decoder_layers=config['num_decoder_layers'],
            num_heads=config['num_heads'],
            d_ff=config['d_ff']
        )
        
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        
        return model

