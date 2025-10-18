#!/usr/bin/env python3
"""
Quantized Model Testing Script
Test different AI models for terminal command responses
"""

import asyncio
import time
from typing import Dict

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


# Models to test (ordered by preference)
MODELS_TO_TEST = [
    {
        "name": "microsoft/DialoGPT-small",
        "description": "Conversational model - good for terminal responses",
        "size": "Small",
        "recommended": True,
    },
    {
        "name": "microsoft/DialoGPT-medium",
        "description": "Larger conversational model - better quality",
        "size": "Medium",
        "recommended": True,
    },
    {
        "name": "distilgpt2",
        "description": "Lightweight GPT-2 - fast and efficient",
        "size": "Small",
        "recommended": True,
    },
    {
        "name": "gpt2",
        "description": "Original GPT-2 - reliable baseline",
        "size": "Small",
        "recommended": False,
    },
    {
        "name": "EleutherAI/gpt-neo-125M",
        "description": "GPT-Neo small - good alternative",
        "size": "Small",
        "recommended": False,
    },
]

# Test commands
TEST_COMMANDS = ["ls", "cat /etc/passwd", "who", "pwd", "help", "unknown_command"]


async def test_model(model_info: Dict, test_command: str = "ls") -> Dict:
    """Test a specific model with a command"""
    model_name = model_info["name"]

    print(f"\n{'=' * 60}")
    print(f"Testing Model: {model_name}")
    print(f"Description: {model_info['description']}")
    print(f"Size: {model_info['size']}")
    print(f"{'=' * 60}")

    try:
        start_time = time.time()

        # Load model
        print(f"Loading {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Add padding token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Determine device and dtype
        device = 0 if torch.cuda.is_available() else -1
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=dtype,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
        )

        # Create pipeline
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            torch_dtype=dtype,
            device=device,
            max_length=512,
            do_sample=True,
            temperature=0.6,
            pad_token_id=tokenizer.eos_token_id,
        )

        load_time = time.time() - start_time

        # Test with different commands
        results = {}
        for command in TEST_COMMANDS:
            try:
                # Create simple prompt
                prompt = f"Linux terminal output for '{command}':\n"

                # Generate response
                response = generator(
                    prompt,
                    max_new_tokens=50,
                    num_return_sequences=1,
                    temperature=0.3,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    truncation=True,
                    return_full_text=False,
                )

                generated_text = response[0]["generated_text"]

                # Clean response
                if ":" in generated_text:
                    clean_response = generated_text.split(":", 1)[-1].strip()
                else:
                    clean_response = generated_text.strip()

                results[command] = {
                    "response": clean_response,
                    "success": True,
                    "quality": len(clean_response) > 3
                    and not any(
                        pattern in clean_response.lower()
                        for pattern in [
                            "command:",
                            "response:",
                            "generate",
                            "linux terminal",
                        ]
                    ),
                }

            except Exception as e:
                results[command] = {
                    "response": f"Error: {e!s}",
                    "success": False,
                    "quality": False,
                }

        # Calculate metrics
        successful_commands = sum(1 for r in results.values() if r["success"])
        quality_responses = sum(1 for r in results.values() if r["quality"])

        return {
            "model_name": model_name,
            "description": model_info["description"],
            "size": model_info["size"],
            "recommended": model_info["recommended"],
            "load_time": load_time,
            "success_rate": successful_commands / len(TEST_COMMANDS),
            "quality_rate": quality_responses / len(TEST_COMMANDS),
            "results": results,
            "device": "CUDA" if torch.cuda.is_available() else "CPU",
            "dtype": str(dtype),
        }

    except Exception as e:
        return {
            "model_name": model_name,
            "description": model_info["description"],
            "size": model_info["size"],
            "recommended": model_info["recommended"],
            "load_time": 0,
            "success_rate": 0,
            "quality_rate": 0,
            "results": {},
            "error": str(e),
            "device": "CUDA" if torch.cuda.is_available() else "CPU",
        }


async def main():
    """Main testing function"""
    print("🤖 Quantized Model Testing for SSH Honeypot")
    print("=" * 60)
    print(f"Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    print(f"PyTorch Version: {torch.__version__}")
    print("=" * 60)

    all_results = []

    for model_info in MODELS_TO_TEST:
        result = await test_model(model_info)
        all_results.append(result)

        # Print summary
        if "error" in result:
            print(f"❌ FAILED: {result['error']}")
        else:
            print("✅ SUCCESS")
            print(f"   Load Time: {result['load_time']:.2f}s")
            print(f"   Success Rate: {result['success_rate']:.1%}")
            print(f"   Quality Rate: {result['quality_rate']:.1%}")

            # Show sample response
            if result["results"]:
                sample_cmd = list(result["results"].keys())[0]
                sample_resp = result["results"][sample_cmd]["response"]
                print(f"   Sample ({sample_cmd}): {sample_resp[:50]}...")

    # Print recommendations
    print(f"\n{'=' * 60}")
    print("📊 RECOMMENDATIONS")
    print(f"{'=' * 60}")

    # Sort by quality rate
    successful_models = [r for r in all_results if "error" not in r]
    successful_models.sort(key=lambda x: x["quality_rate"], reverse=True)

    if successful_models:
        best_model = successful_models[0]
        print(f"🥇 BEST MODEL: {best_model['model_name']}")
        print(f"   Quality Rate: {best_model['quality_rate']:.1%}")
        print(f"   Load Time: {best_model['load_time']:.2f}s")
        print(f"   Description: {best_model['description']}")

        print("\n📝 CONFIGURATION:")
        print(f"AI_MODEL_NAME={best_model['model_name']}")
        print("AI_MODEL_FALLBACK=distilgpt2")
        print("AI_USE_QUANTIZED=true")

        print("\n🔧 ALTERNATIVE MODELS:")
        for i, model in enumerate(successful_models[1:3], 1):
            print(
                f"{i + 1}. {model['model_name']} ({model['quality_rate']:.1%} quality)"
            )
    else:
        print("❌ No models loaded successfully!")
        print("💡 Try installing transformers: pip install transformers torch")


if __name__ == "__main__":
    asyncio.run(main())
