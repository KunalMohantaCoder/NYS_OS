"""
Main inference engine for text generation.
"""
import torch
from typing import Optional, Dict, Any
import os
import sys

# Handle both relative and absolute imports
try:
    from ..model.model import TransformerModel
    from ..training.tokenizer import BPETokenizer
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from model.model import TransformerModel
    from training.tokenizer import BPETokenizer

from .generator import TextGenerator
from .context_manager import ContextManager


class InferenceEngine:
    """
    Main inference engine for generating text responses.
    
    Args:
        model_path: Path to trained model
        tokenizer_path: Path to tokenizer
        device: Device to run inference on ('cpu' or 'cuda')
        max_len: Maximum generation length
    """
    
    def __init__(self, model_path: str, tokenizer_path: str,
                 device: str = 'cpu', max_len: int = 512):
        self.device = device if torch.cuda.is_available() and device == 'cuda' else 'cpu'
        
        # Load tokenizer
        self.tokenizer = BPETokenizer.load(tokenizer_path)
        
        # Load model
        self.model = TransformerModel.load(model_path, device=self.device)
        self.model.eval()
        
        # Initialize generator
        self.generator = TextGenerator(self.model, self.tokenizer, self.device, max_len)
        
        # Initialize context manager
        self.context_manager = ContextManager()
        
        print(f"Inference engine initialized on {self.device}")
        print(f"Vocabulary size: {len(self.tokenizer.vocab)}")
    
    def generate(self, input_text: str, method: str = 'sample',
                use_context: bool = True, **generation_kwargs) -> str:
        """
        Generate response to input text.
        
        Args:
            input_text: Input text
            method: Generation method ('greedy', 'beam', 'sample')
            use_context: Whether to use conversation context
            **generation_kwargs: Additional arguments for generation
                - beam_size: For beam search
                - temperature: For sampling
                - top_k: For sampling
                - top_p: For sampling
        
        Returns:
            Generated response text
        """
        # Prepare input with context if enabled
        if use_context and len(self.context_manager.conversation_history) > 0:
            context_text = self.context_manager.get_context(input_text, self.tokenizer)
        else:
            context_text = f"User: {input_text}\nAssistant:"
        
        # Encode input
        src_ids = self.tokenizer.encode(context_text, add_special_tokens=True)
        src = torch.tensor([src_ids], device=self.device)
        
        # Generate mask
        src_mask = (src != self.tokenizer.vocab.get('<pad>', 0)).unsqueeze(1).unsqueeze(2)
        src_mask = src_mask.squeeze(2)
        
        # Generate response
        with torch.no_grad():
            if method == 'greedy':
                generated_ids = self.generator.greedy_decode(src, src_mask)
            elif method == 'beam':
                beam_size = generation_kwargs.get('beam_size', 5)
                generated_ids = self.generator.beam_search(src, beam_size, src_mask)
            else:  # sample
                temperature = generation_kwargs.get('temperature', 1.0)
                top_k = generation_kwargs.get('top_k', None)
                top_p = generation_kwargs.get('top_p', 0.9)
                generated_ids = self.generator.sample(src, temperature, top_k, top_p, src_mask)
        
        # Decode response
        response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        # Add to context
        if use_context:
            self.context_manager.add_turn(input_text, response)
        
        return response.strip()
    
    def chat(self, user_input: str, **generation_kwargs) -> str:
        """
        Chat interface - generates response and manages context.
        
        Args:
            user_input: User's message
            **generation_kwargs: Generation parameters
        
        Returns:
            Assistant's response
        """
        return self.generate(user_input, method='sample', use_context=True, **generation_kwargs)
    
    def clear_context(self):
        """Clear conversation context."""
        self.context_manager.clear()
    
    def get_context_history(self):
        """Get conversation history."""
        return self.context_manager.get_history()
    
    def set_context_history(self, history):
        """Set conversation history."""
        self.context_manager.set_history(history)

