"""Ollama setup wizard for gitcommit-ai."""
import platform
import subprocess
import sys


class OllamaSetup:
    """Interactive Ollama setup wizard."""

    RECOMMENDED_MODEL = "qwen2.5:7b"
    MODEL_SIZE = "4.7GB"

    @staticmethod
    def detect_os() -> str:
        """Detect operating system.

        Returns:
            OS type: 'macos', 'linux', 'windows', or 'unknown'.
        """
        os_type = platform.system()
        if os_type == "Darwin":
            return "macos"
        elif os_type == "Linux":
            return "linux"
        elif os_type == "Windows":
            return "windows"
        else:
            return "unknown"

    @staticmethod
    def is_ollama_installed() -> bool:
        """Check if Ollama is already installed."""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def is_model_downloaded(model: str) -> bool:
        """Check if a model is already downloaded."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True,
            )
            return model in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def pull_model(model: str) -> bool:
        """Download Ollama model.

        Args:
            model: Model name to download.

        Returns:
            True if successful, False otherwise.
        """
        print(f"\n📥 Downloading {model}... (this may take a few minutes)")
        try:
            result = subprocess.run(
                ["ollama", "pull", model],
                check=True,
            )
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to download model: {e}", file=sys.stderr)
            return False
        except FileNotFoundError:
            print("❌ Ollama command not found. Please install Ollama first.", file=sys.stderr)
            return False

    @staticmethod
    def show_install_instructions(os_type: str) -> None:
        """Show installation instructions for the detected OS."""
        print("\n📦 Ollama Installation Instructions\n")

        if os_type == "macos":
            print("macOS:")
            print("  brew install ollama")
            print("\nAfter installation, run:")
            print("  ollama serve  # Start Ollama service")
        elif os_type == "linux":
            print("Linux:")
            print("  curl https://ollama.ai/install.sh | sh")
            print("\nAfter installation, the service starts automatically.")
        elif os_type == "windows":
            print("Windows:")
            print("  Download installer from: https://ollama.ai")
            print("\nAfter installation, Ollama runs as a service.")
        else:
            print("Visit: https://ollama.ai for installation instructions")

        print("\n💡 After installing, run this command again: gitcommit-ai setup-ollama")

    @staticmethod
    def confirm_download(model: str, size: str) -> bool:
        """Ask user to confirm model download.

        Args:
            model: Model name.
            size: Model size (e.g., "4.7GB").

        Returns:
            True if user confirms, False otherwise.
        """
        print(f"\n📊 Model: {model}")
        print(f"📦 Size: {size}")
        response = input("\nDownload this model? [Y/n]: ").strip().lower()
        return response in ("", "y", "yes")

    @classmethod
    def run(cls) -> int:
        """Run the setup wizard.

        Returns:
            Exit code (0 for success, non-zero for failure).
        """
        print("🚀 GitCommit AI - Ollama Setup Wizard")
        print("=" * 50)

        # Detect OS
        os_type = cls.detect_os()
        print(f"\n✓ Detected OS: {os_type}")

        # Check if Ollama is installed
        if not cls.is_ollama_installed():
            print("\n❌ Ollama is not installed")
            cls.show_install_instructions(os_type)
            return 1

        print("✓ Ollama is installed")

        # Check if recommended model is downloaded
        if cls.is_model_downloaded(cls.RECOMMENDED_MODEL):
            print(f"✓ Model {cls.RECOMMENDED_MODEL} is already downloaded")
            print("\n🎉 Setup complete! You can now use:")
            print("    gitcommit-ai generate")
            return 0

        print(f"\n⚠️  Recommended model not found: {cls.RECOMMENDED_MODEL}")

        # Ask to download
        if not cls.confirm_download(cls.RECOMMENDED_MODEL, cls.MODEL_SIZE):
            print("\n⏭  Skipped model download")
            print("💡 You can download it later with:")
            print(f"    ollama pull {cls.RECOMMENDED_MODEL}")
            return 0

        # Download model
        if cls.pull_model(cls.RECOMMENDED_MODEL):
            print(f"\n✅ Successfully downloaded {cls.RECOMMENDED_MODEL}")
            print("\n🎉 Setup complete! You can now use:")
            print("    gitcommit-ai generate")
            return 0
        else:
            return 1
