"""
Training loop and optimization.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Optional, Dict
import os
import sys
import time
from tqdm import tqdm

# Handle both relative and absolute imports
try:
    from ..model.model import TransformerModel
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from model.model import TransformerModel

try:
    from .tokenizer import BPETokenizer
except ImportError:
    from training.tokenizer import BPETokenizer


class Trainer:
    """
    Trainer for transformer model.
    
    Args:
        model: Transformer model
        tokenizer: BPE tokenizer
        device: Device to train on ('cpu' or 'cuda')
        learning_rate: Learning rate
        weight_decay: Weight decay for optimizer
    """
    
    def __init__(self, model: TransformerModel, tokenizer: BPETokenizer,
                 device: str = 'cpu', learning_rate: float = 1e-4,
                 weight_decay: float = 1e-5):
        self.model = model.to(device)
        self.tokenizer = tokenizer
        self.device = device
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        
        # Loss function (ignore padding tokens)
        pad_idx = tokenizer.vocab.get('<pad>', 0)
        self.criterion = nn.CrossEntropyLoss(ignore_index=pad_idx)
        
        # Optimizer
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay,
            betas=(0.9, 0.98),
            eps=1e-9
        )
        
        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=3
        )
        
        self.train_losses = []
        self.val_losses = []
    
    def train_epoch(self, train_loader: DataLoader) -> float:
        """
        Train for one epoch.
        
        Args:
            train_loader: Training data loader
        
        Returns:
            Average training loss
        """
        self.model.train()
        total_loss = 0
        num_batches = 0
        
        progress_bar = tqdm(train_loader, desc='Training')
        
        for batch in progress_bar:
            src = batch['src'].to(self.device)
            tgt_input = batch['tgt_input'].to(self.device)
            tgt_output = batch['tgt_output'].to(self.device)
            
            # Generate masks
            src_mask, tgt_mask, _, _ = self.model.generate_mask(src, tgt_input)
            
            # Forward pass
            self.optimizer.zero_grad()
            output = self.model(src, tgt_input, src_mask, tgt_mask)
            
            # Reshape for loss calculation
            output = output.view(-1, output.size(-1))
            tgt_output = tgt_output.view(-1)
            
            # Calculate loss
            loss = self.criterion(output, tgt_output)
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
            
            # Update progress bar
            progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        avg_loss = total_loss / num_batches if num_batches > 0 else 0.0
        self.train_losses.append(avg_loss)
        return avg_loss
    
    def validate(self, val_loader: DataLoader) -> float:
        """
        Validate model.
        
        Args:
            val_loader: Validation data loader
        
        Returns:
            Average validation loss
        """
        self.model.eval()
        total_loss = 0
        num_batches = 0
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc='Validating'):
                src = batch['src'].to(self.device)
                tgt_input = batch['tgt_input'].to(self.device)
                tgt_output = batch['tgt_output'].to(self.device)
                
                # Generate masks
                src_mask, tgt_mask, _, _ = self.model.generate_mask(src, tgt_input)
                
                # Forward pass
                output = self.model(src, tgt_input, src_mask, tgt_mask)
                
                # Reshape for loss calculation
                output = output.view(-1, output.size(-1))
                tgt_output = tgt_output.view(-1)
                
                # Calculate loss
                loss = self.criterion(output, tgt_output)
                
                total_loss += loss.item()
                num_batches += 1
        
        avg_loss = total_loss / num_batches if num_batches > 0 else 0.0
        self.val_losses.append(avg_loss)
        return avg_loss
    
    def train(self, train_loader: DataLoader, num_epochs: int,
              val_loader: Optional[DataLoader] = None,
              checkpoint_dir: str = 'data/models',
              save_every: int = 5):
        """
        Train model for multiple epochs.
        
        Args:
            train_loader: Training data loader
            num_epochs: Number of epochs
            val_loader: Validation data loader (optional)
            checkpoint_dir: Directory to save checkpoints
            save_every: Save checkpoint every N epochs
        """
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        best_val_loss = float('inf')
        
        print(f"Starting training on {self.device}")
        print(f"Model parameters: {self.model.count_parameters():,}")
        
        for epoch in range(1, num_epochs + 1):
            print(f"\nEpoch {epoch}/{num_epochs}")
            print("-" * 50)
            
            # Train
            train_loss = self.train_epoch(train_loader)
            print(f"Train Loss: {train_loss:.4f}")
            
            # Validate
            if val_loader is not None:
                val_loss = self.validate(val_loader)
                print(f"Val Loss: {val_loss:.4f}")
                self.scheduler.step(val_loss)
                
                # Save best model
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    self.save_checkpoint(
                        os.path.join(checkpoint_dir, 'best_model.pt'),
                        epoch
                    )
                    print(f"Saved best model (val_loss: {val_loss:.4f})")
            else:
                self.scheduler.step(train_loss)
            
            # Save checkpoint periodically
            if epoch % save_every == 0:
                self.save_checkpoint(
                    os.path.join(checkpoint_dir, f'checkpoint_epoch_{epoch}.pt'),
                    epoch
                )
        
        print("\nTraining completed!")
    
    def save_checkpoint(self, path: str, epoch: int):
        """Save training checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
        }
        torch.save(checkpoint, path)
    
    def load_checkpoint(self, path: str):
        """Load training checkpoint."""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.train_losses = checkpoint.get('train_losses', [])
        self.val_losses = checkpoint.get('val_losses', [])
        return checkpoint['epoch']

