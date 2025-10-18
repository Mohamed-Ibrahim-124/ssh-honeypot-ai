#!/usr/bin/env python3
"""
Model Comparison Script
Test different AI models for honeypot responses
"""

import asyncio

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Models to test
MODELS_TO_TEST = [
    "microsoft/DialoGPT-small",  # Current
    "microsoft/CodeGPT-small-py",  # Code-focused
    "microsoft/DialoGPT-medium",  # Larger dialogue model
    "EleutherAI/gpt-neo-125M",  # GPT-style
]


async def test_model(model_name: str, test_command: str = "ls -la"):
    """Test a specific model with a command"""
    print(f"\n{'=' * 50}")
    print(f"Testing Model: {model_name}")
    print(f"{'=' * 50}")

    try:
        # Load model
        print(f"Loading {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Add padding token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
        )

        # Create pipeline
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device=0 if torch.cuda.is_available() else -1,
            max_length=512,
            do_sample=True,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id,
        )

        # Test prompt
        prompt = f"""You are a Linux SSH terminal. Respond to commands naturally.
Available commands: ls, cat /etc/passwd, who, pwd, cd
Current directory: /home/admin

User command: {test_command}
Response:"""

        # Generate response
        print(f"Generating response for: {test_command}")
        response = generator(
            prompt,
            max_length=len(prompt.split()) + 50,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

        # Extract and clean response
        generated_text = response[0]["generated_text"]
        if "Response:" in generated_text:
            clean_response = generated_text.split("Response:")[-1].strip()
        else:
            clean_response = generated_text.split(test_command)[-1].strip()

        print(f"Response: {clean_response}")

        # Clean up memory
        del model
        del tokenizer
        del generator
        torch.cuda.empty_cache() if torch.cuda.is_available() else None

    except Exception as e:
        print(f"Error testing {model_name}: {e}")


async def main():
    """Main test function"""
    print("AI Model Comparison for SSH Honeypot")
    print("This will test different models to see which gives better responses")

    test_commands = ["ls -la", "cat /etc/passwd", "who", "pwd"]

    for command in test_commands:
        print(f"\n{'#' * 60}")
        print(f"Testing Command: {command}")
        print(f"{'#' * 60}")

        for model in MODELS_TO_TEST:
            await test_model(model, command)

        # Ask user if they want to continue
        try:
            continue_test = input(
                "\nPress Enter to test next command, or 'q' to quit: "
            )
            if continue_test.lower() == "q":
                break
        except KeyboardInterrupt:
            break

    print("\nModel comparison complete!")


if __name__ == "__main__":
    asyncio.run(main())
