"""
AI Model Service
Handles AI model loading and response generation
"""

import logging
from typing import Any, Optional, Union

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from ..config import settings

logger = logging.getLogger(__name__)


class AIModelService:
    """AI Model service for enhanced honeypot responses"""

    def __init__(self) -> None:
        self.model_name = settings.ai_model_name
        self.fallback_model = settings.ai_model_fallback
        self.device: Union[str, int] = settings.ai_model_device
        self.max_tokens = settings.ai_max_tokens
        self.temperature = settings.ai_temperature
        self.use_quantized = settings.ai_use_quantized
        self.model_loaded = False
        self.generator: Optional[Any] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self.current_model: Optional[Any] = None

    async def initialize_model(self) -> bool:
        """Initialize AI model with fallback support"""
        models_to_try = [self.model_name, self.fallback_model]

        for model_name in models_to_try:
            try:
                logger.info(f"Attempting to load AI model: {model_name}")

                # Check if CUDA is available
                if self.device == "auto":
                    self.device = 0 if torch.cuda.is_available() else -1

                # Load tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)

                # Add padding token if not present
                if (
                    self.tokenizer
                    and hasattr(self.tokenizer, "pad_token")
                    and self.tokenizer.pad_token is None
                ) and hasattr(self.tokenizer, "eos_token"):
                    self.tokenizer.pad_token = self.tokenizer.eos_token

                # Determine model loading parameters
                model_kwargs = {
                    "trust_remote_code": True,
                    "low_cpu_mem_usage": True,
                }

                # Add quantization if enabled and supported
                if self.use_quantized and torch.cuda.is_available():
                    model_kwargs["torch_dtype"] = torch.float16
                    model_kwargs["device_map"] = "auto"
                else:
                    model_kwargs["torch_dtype"] = torch.float32
                    model_kwargs["device_map"] = None

                # Load model
                model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)

                # Create text generation pipeline
                pipeline_kwargs = {
                    "model": model,
                    "tokenizer": self.tokenizer,
                    "device": self.device,
                    "max_length": 512,
                    "do_sample": True,
                    "temperature": self.temperature,
                    "pad_token_id": self.tokenizer.eos_token_id
                    if self.tokenizer and hasattr(self.tokenizer, "eos_token_id")
                    else None,
                }

                # Add quantization to pipeline if enabled
                if self.use_quantized and torch.cuda.is_available():
                    pipeline_kwargs["torch_dtype"] = torch.float16
                else:
                    pipeline_kwargs["torch_dtype"] = torch.float32

                self.generator = pipeline("text-generation", **pipeline_kwargs)

                self.model_loaded = True
                self.current_model = model_name
                logger.info(f"AI model loaded successfully: {model_name}")
                return True

            except Exception as e:
                logger.warning(f"Failed to load model {model_name}: {e}")
                continue

        # If all models failed
        logger.error("All AI models failed to load")
        self.model_loaded = False
        return False

    async def generate_response(self, context: str) -> str:
        """Generate AI response with fallback to simple responses"""
        if not self.model_loaded:
            logger.warning("AI model not available, using fallback responses")
            return self._get_fallback_response(context)

        try:
            # Create more specific prompts based on command type
            prompt = self._create_contextual_prompt(context)

            # Generate response with proper token handling
            if not self.generator:
                # Extract command from context for fallback
                command = context.split("\n")[-1].strip() if context else "unknown"
                return self._get_fallback_response(command)

            response = self.generator(
                prompt,
                max_new_tokens=30,  # Very short responses to match terminal output
                num_return_sequences=1,
                temperature=0.1,  # Very low temperature for consistent responses
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
                if self.tokenizer and hasattr(self.tokenizer, "eos_token_id")
                else None,
                truncation=True,  # Explicitly enable truncation
                return_full_text=False,  # Don't return the input prompt
            )

            # Extract generated text
            generated_text = response[0]["generated_text"]

            # Clean up response
            clean_response = self._clean_response(generated_text, context)

            # Validate response quality
            if not self._is_valid_response(clean_response):
                logger.warning("AI generated poor response, using fallback")
                return self._get_fallback_response(context)

            return clean_response

        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            logger.info("Falling back to simple responses")
            return self._get_fallback_response(context)

    def _create_contextual_prompt(self, command: str) -> str:
        """Create contextual prompts that guide the model to generate realistic terminal output"""
        command_lower = command.strip().lower()

        # Use few-shot prompting to teach the model the expected format
        if command_lower.startswith("ls"):
            return f"""You are a Linux terminal. Generate realistic output for the ls command.

Example:
$ ls
bin  etc  home  usr  var  Documents  Downloads

$ ls -la
total 8
drwxr-xr-x 2 admin admin 4096 Oct 19 00:00 .
drwxr-xr-x 3 root  root  4096 Oct 19 00:00 ..
-rw-r--r-- 1 admin admin  220 Oct 19 00:00 .bashrc

Now generate output for: {command}"""

        elif command == "cat /etc/passwd":
            return f"""You are a Linux terminal. Generate realistic /etc/passwd file content.

Example:
$ cat /etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
admin:x:1000:1000:admin:/home/admin:/bin/bash

Now generate output for: {command}"""

        elif command_lower == "who":
            return f"""You are a Linux terminal. Generate realistic who command output.

Example:
$ who
admin    pts/0        2025-10-19 00:58 (127.0.0.1)
root     pts/1        2025-10-19 00:55 (192.168.1.100)

Now generate output for: {command}"""

        elif command_lower == "pwd":
            return f"""You are a Linux terminal. Generate realistic pwd command output.

Example:
$ pwd
/home/admin

Now generate output for: {command}"""

        elif command_lower.startswith("cd"):
            return f"""You are a Linux terminal. Generate realistic cd command response.

Example:
$ cd /home
$ cd nonexistent
cd: nonexistent: No such file or directory

Now generate output for: {command}"""

        elif command_lower in ["help", "?"]:
            return f"""You are a Linux terminal. Generate realistic help output.

Example:
$ help
Available commands:
ls          - List directory contents
cat         - Display file contents
who         - Show logged in users
pwd         - Print working directory
cd          - Change directory
help        - Show this help
exit        - Exit session

Now generate output for: {command}"""

        elif command_lower in ["exit", "quit", "logout"]:
            return f"""You are a Linux terminal. Generate realistic logout message.

Example:
$ exit
Goodbye!

Now generate output for: {command}"""

        else:
            # Unknown command - generate realistic error
            return f"""You are a Linux terminal. Generate realistic error message for unknown command.

Example:
$ unknown_command
bash: unknown_command: command not found

Now generate output for: {command}"""

    def _clean_response(self, generated_text: str, command: str) -> str:
        """Clean up AI generated response to extract terminal output"""
        # Look for the command in the generated text and extract what comes after
        lines = generated_text.split("\n")

        # Find the line with the command (with $ prompt)
        for i, line in enumerate(lines):
            if command.strip() in line and "$" in line:
                # Return all lines after the command line
                output_lines = lines[i + 1 :]
                clean_response = "\n".join(output_lines).strip()

                # Remove any remaining prompt indicators
                clean_response = clean_response.replace("$", "").strip()

                # If we got a good response, return it
                if clean_response and len(clean_response) > 2:
                    return clean_response

        # Fallback: try to extract content after "Now generate output for:"
        if "Now generate output for:" in generated_text:
            parts = generated_text.split("Now generate output for:")
            if len(parts) > 1:
                clean_response = parts[1].strip()
                # Remove any remaining prompt indicators
                clean_response = clean_response.replace("$", "").strip()
                return clean_response

        # Another fallback: look for content after the command
        if command in generated_text:
            parts = generated_text.split(command)
            if len(parts) > 1:
                clean_response = parts[1].strip()
                clean_response = clean_response.replace("$", "").strip()
                return clean_response

        # Last resort: return the original text cleaned up
        clean_response = generated_text.strip()
        clean_response = clean_response.replace("$", "").strip()
        return clean_response

    def _is_valid_response(self, response: str) -> bool:
        """Check if response is valid and not garbled"""
        if not response or len(response) < 3:
            return False

        # Check for repetitive patterns (sign of model failure)
        words = response.split()
        if len(words) > 5:
            # Check if more than 50% of words are repeated
            unique_words = set(words)
            if len(unique_words) / len(words) < 0.5:
                return False

        # Check for nonsensical patterns
        return not any(
            pattern in response.lower()
            for pattern in [
                "command:",
                "response:",
                "generate",
                "linux terminal",
                "realistic",
                "output for",
                "command output",
            ]
        )

    def _get_fallback_response(self, command: str) -> str:
        """Get fallback response when AI fails"""
        command_lower = command.strip().lower()

        if command_lower.startswith("ls"):
            return """total 8
drwxr-xr-x 2 admin admin 4096 Oct 19 00:00 .
drwxr-xr-x 3 root  root  4096 Oct 19 00:00 ..
-rw-r--r-- 1 admin admin  220 Oct 19 00:00 .bashrc
-rw-r--r-- 1 admin admin  807 Oct 19 00:00 .profile
drwxr-xr-x 2 admin admin 4096 Oct 19 00:00 Documents
drwxr-xr-x 2 admin admin 4096 Oct 19 00:00 Downloads"""

        elif command == "cat /etc/passwd":
            return """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
admin:x:1000:1000:admin:/home/admin:/bin/bash"""

        elif command_lower == "who":
            return """admin    pts/0        2025-10-19 00:58 (127.0.0.1)
root     pts/1        2025-10-19 00:55 (192.168.1.100)"""

        elif command_lower == "pwd":
            return "/home/admin"

        elif command_lower.startswith("cd"):
            return ""  # cd commands typically don't produce output

        elif command_lower in ["help", "?"]:
            return """Available commands:
ls          - List directory contents
cat         - Display file contents
who         - Show logged in users
pwd         - Print working directory
cd          - Change directory
help        - Show this help
exit        - Exit session"""

        elif command_lower in ["exit", "quit", "logout"]:
            return "Goodbye!"

        else:
            return f"bash: {command}: command not found"

    def is_available(self) -> bool:
        """Check if AI model is available"""
        return self.model_loaded and self.generator is not None

    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            "current_model": self.current_model,
            "primary_model": self.model_name,
            "fallback_model": self.fallback_model,
            "device": self.device,
            "loaded": self.model_loaded,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "quantized": self.use_quantized,
        }
