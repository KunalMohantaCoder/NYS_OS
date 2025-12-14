#!/usr/bin/env python3
"""
Training script for NyxOS AI model.
"""
import os
import sys
import torch
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model.model import TransformerModel
from training.tokenizer import BPETokenizer
from training.dataset import create_data_loader
from training.data_preprocessing import prepare_conversation_data, create_assistant_training_data, clean_text
from training.trainer import Trainer


def main():
    print("=" * 60)
    print("NyxOS AI Model Training")
    print("=" * 60)
    
    # Configuration
    config = {
        'vocab_size': 10000,
        'd_model': 256,
        'num_encoder_layers': 4,
        'num_decoder_layers': 4,
        'num_heads': 8,
        'd_ff': 1024,
        'max_len': 512,
        'dropout': 0.1,
        'batch_size': 16,
        'learning_rate': 1e-4,
        'num_epochs': 10,
        'device': 'cuda' if torch.cuda.is_available() else 'cpu',
    }
    
    print(f"\nConfiguration:")
    print(f"  Device: {config['device']}")
    print(f"  Model size: {config['d_model']} dims, {config['num_encoder_layers']} encoder layers")
    print(f"  Vocabulary size: {config['vocab_size']}")
    print(f"  Batch size: {config['batch_size']}")
    print(f"  Epochs: {config['num_epochs']}")
    
    # Create directories
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    models_dir = data_dir / "models"
    models_dir.mkdir(exist_ok=True)
    training_dir = data_dir / "training"
    training_dir.mkdir(exist_ok=True)
    
    # Step 1: Prepare training data
    print("\n" + "=" * 60)
    print("Step 1: Preparing training data")
    print("=" * 60)
    
    # Get training texts
    training_texts = []
    
    # Add assistant training data
    assistant_pairs = create_assistant_training_data()
    training_texts.extend([f"{inp} {out}" for inp, out in assistant_pairs])
    
    # Add sample conversational data
    sample_conversations = [
        "Hello, how are you? I'm doing well, thank you for asking.",
        "What is the weather like? The weather is sunny and warm today.",
        "Can you help me? Of course, I'd be happy to help you with that.",
        "Tell me a joke. Why don't scientists trust atoms? Because they make up everything!",
        "What time is it? I don't have access to the current time, but you can check your system clock.",
        "How does this work? This system uses neural networks to understand and respond to your questions.",
        "Thank you. You're welcome! Is there anything else I can help you with?",
    ]
    training_texts.extend(sample_conversations)
    
    # Load additional training data if available
    training_file = training_dir / "training_data.txt"
    if training_file.exists():
        with open(training_file, 'r', encoding='utf-8') as f:
            additional_texts = [line.strip() for line in f if line.strip()]
            training_texts.extend(additional_texts)
        print(f"  Loaded {len(additional_texts)} lines from training_data.txt")
    
    if not training_texts:
        print("ERROR: No training data found!")
        print("Please create data/training/training_data.txt with training examples.")
        return
    
    print(f"  Total training texts: {len(training_texts)}")
    
    # Prepare conversation pairs
    pairs = prepare_conversation_data(training_texts)
    pairs.extend(assistant_pairs)
    
    print(f"  Total conversation pairs: {len(pairs)}")
    
    # Step 2: Train tokenizer
    print("\n" + "=" * 60)
    print("Step 2: Training tokenizer")
    print("=" * 60)
    
    tokenizer = BPETokenizer(
        vocab_size=config['vocab_size'],
        special_tokens=['<pad>', '<unk>', '<bos>', '<eos>']
    )
    
    tokenizer.train(training_texts)
    tokenizer_path = models_dir / "tokenizer.json"
    tokenizer.save(str(tokenizer_path))
    print(f"  Tokenizer saved to {tokenizer_path}")
    print(f"  Vocabulary size: {len(tokenizer.vocab)}")
    
    # Step 3: Create data loaders
    print("\n" + "=" * 60)
    print("Step 3: Creating data loaders")
    print("=" * 60)
    
    # Split data (80% train, 20% val)
    split_idx = int(len(pairs) * 0.8)
    train_pairs = pairs[:split_idx]
    val_pairs = pairs[split_idx:]
    
    train_loader = create_data_loader(
        train_pairs, tokenizer,
        batch_size=config['batch_size'],
        max_len=config['max_len'],
        shuffle=True
    )
    
    val_loader = create_data_loader(
        val_pairs, tokenizer,
        batch_size=config['batch_size'],
        max_len=config['max_len'],
        shuffle=False
    ) if val_pairs else None
    
    print(f"  Training batches: {len(train_loader)}")
    if val_loader:
        print(f"  Validation batches: {len(val_loader)}")
    
    # Step 4: Initialize model
    print("\n" + "=" * 60)
    print("Step 4: Initializing model")
    print("=" * 60)
    
    vocab_size = len(tokenizer.vocab)
    model = TransformerModel(
        src_vocab_size=vocab_size,
        tgt_vocab_size=vocab_size,
        d_model=config['d_model'],
        num_encoder_layers=config['num_encoder_layers'],
        num_decoder_layers=config['num_decoder_layers'],
        num_heads=config['num_heads'],
        d_ff=config['d_ff'],
        max_len=config['max_len'],
        dropout=config['dropout']
    )
    
    param_count = model.count_parameters()
    print(f"  Model parameters: {param_count:,}")
    print(f"  Model size: ~{param_count * 4 / 1024 / 1024:.2f} MB (float32)")
    
    # Step 5: Train model
    print("\n" + "=" * 60)
    print("Step 5: Training model")
    print("=" * 60)
    
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        device=config['device'],
        learning_rate=config['learning_rate']
    )
    
    trainer.train(
        train_loader=train_loader,
        num_epochs=config['num_epochs'],
        val_loader=val_loader,
        checkpoint_dir=str(models_dir),
        save_every=5
    )
    
    # Save final model
    model_path = models_dir / "best_model.pt"
    model.save(str(model_path))
    print(f"\n  Final model saved to {model_path}")
    
    print("\n" + "=" * 60)
    print("Training completed!")
    print("=" * 60)
    print(f"\nTo use the model, start the AI service:")
    print(f"  cd ai-engine")
    print(f"  python -m api.server")


if __name__ == "__main__":
    main()

