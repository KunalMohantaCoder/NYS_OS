"""
Text generation strategies: beam search and sampling.
"""
import torch
import torch.nn.functional as F
from typing import List, Tuple, Optional


class TextGenerator:
    """
    Text generator with various decoding strategies.
    
    Args:
        model: Trained transformer model
        tokenizer: BPE tokenizer
        device: Device to run inference on
        max_len: Maximum generation length
    """
    
    def __init__(self, model, tokenizer, device: str = 'cpu', max_len: int = 512):
        self.model = model.to(device)
        self.model.eval()
        self.tokenizer = tokenizer
        self.device = device
        self.max_len = max_len
        self.pad_idx = tokenizer.vocab.get('<pad>', 0)
        self.bos_idx = tokenizer.vocab.get('<bos>', 1)
        self.eos_idx = tokenizer.vocab.get('<eos>', 2)
    
    def greedy_decode(self, src: torch.Tensor, src_mask: Optional[torch.Tensor] = None) -> List[int]:
        """
        Greedy decoding (always pick highest probability token).
        
        Args:
            src: Source sequence [1, src_len]
            src_mask: Source attention mask
        
        Returns:
            Generated token sequence
        """
        memory = self.model.encoder(src, src_mask)
        
        tgt = torch.tensor([[self.bos_idx]], device=self.device)
        
        for _ in range(self.max_len):
            tgt_mask = self._generate_square_subsequent_mask(tgt.size(1)).to(self.device)
            output = self.model.decoder(tgt, memory, src_mask, tgt_mask)
            logits = self.model.output_projection(output[:, -1, :])
            next_token = logits.argmax(dim=-1).unsqueeze(0)
            tgt = torch.cat([tgt, next_token], dim=1)
            
            if next_token.item() == self.eos_idx:
                break
        
        return tgt[0].tolist()[1:]  # Remove BOS token
    
    def beam_search(self, src: torch.Tensor, beam_size: int = 5,
                   src_mask: Optional[torch.Tensor] = None,
                   length_penalty: float = 0.6) -> List[int]:
        """
        Beam search decoding.
        
        Args:
            src: Source sequence [1, src_len]
            beam_size: Number of beams
            src_mask: Source attention mask
            length_penalty: Length penalty factor
        
        Returns:
            Generated token sequence
        """
        memory = self.model.encoder(src, src_mask)
        
        # Initialize beams: (sequence, score)
        beams = [([self.bos_idx], 0.0)]
        finished = []
        
        for step in range(self.max_len):
            candidates = []
            
            for seq, score in beams:
                if seq[-1] == self.eos_idx:
                    finished.append((seq, score / (len(seq) ** length_penalty)))
                    continue
                
                tgt = torch.tensor([seq], device=self.device)
                tgt_mask = self._generate_square_subsequent_mask(tgt.size(1)).to(self.device)
                output = self.model.decoder(tgt, memory, src_mask, tgt_mask)
                logits = self.model.output_projection(output[:, -1, :])
                probs = F.log_softmax(logits, dim=-1)
                
                # Get top-k tokens
                top_probs, top_indices = torch.topk(probs, beam_size, dim=-1)
                
                for i in range(beam_size):
                    token = top_indices[0][i].item()
                    token_score = top_probs[0][i].item()
                    candidates.append((seq + [token], score + token_score))
            
            if not candidates:
                break
            
            # Keep top beam_size candidates
            candidates.sort(key=lambda x: x[1] / (len(x[0]) ** length_penalty), reverse=True)
            beams = candidates[:beam_size]
        
        # Add finished sequences
        all_candidates = finished + [(seq, score / (len(seq) ** length_penalty)) 
                                     for seq, score in beams]
        all_candidates.sort(key=lambda x: x[1], reverse=True)
        
        best_seq = all_candidates[0][0]
        return best_seq[1:]  # Remove BOS token
    
    def sample(self, src: torch.Tensor, temperature: float = 1.0,
              top_k: Optional[int] = None, top_p: float = 0.9,
              src_mask: Optional[torch.Tensor] = None) -> List[int]:
        """
        Sampling-based decoding with temperature, top-k, and top-p.
        
        Args:
            src: Source sequence [1, src_len]
            temperature: Sampling temperature (higher = more random)
            top_k: Sample from top-k tokens only
            top_p: Nucleus sampling (cumulative probability threshold)
            src_mask: Source attention mask
        
        Returns:
            Generated token sequence
        """
        memory = self.model.encoder(src, src_mask)
        tgt = torch.tensor([[self.bos_idx]], device=self.device)
        
        for _ in range(self.max_len):
            tgt_mask = self._generate_square_subsequent_mask(tgt.size(1)).to(self.device)
            output = self.model.decoder(tgt, memory, src_mask, tgt_mask)
            logits = self.model.output_projection(output[:, -1, :]) / temperature
            probs = F.softmax(logits, dim=-1)
            
            # Apply top-k filtering
            if top_k is not None:
                top_k_probs, top_k_indices = torch.topk(probs, top_k, dim=-1)
                probs = torch.zeros_like(probs)
                probs.scatter_(1, top_k_indices, top_k_probs)
                probs = probs / probs.sum(dim=-1, keepdim=True)
            
            # Apply top-p (nucleus) sampling
            if top_p < 1.0:
                sorted_probs, sorted_indices = torch.sort(probs, descending=True)
                cumsum_probs = torch.cumsum(sorted_probs, dim=-1)
                
                # Find cutoff point
                sorted_indices_to_remove = cumsum_probs > top_p
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = 0
                
                indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                probs[indices_to_remove] = 0
                probs = probs / probs.sum(dim=-1, keepdim=True)
            
            # Sample from distribution
            next_token = torch.multinomial(probs, 1)
            tgt = torch.cat([tgt, next_token], dim=1)
            
            if next_token.item() == self.eos_idx:
                break
        
        return tgt[0].tolist()[1:]  # Remove BOS token
    
    def _generate_square_subsequent_mask(self, size: int) -> torch.Tensor:
        """Generate causal mask for decoder."""
        mask = torch.triu(torch.ones(size, size), diagonal=1).bool()
        return mask

