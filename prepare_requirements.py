from importlib.metadata import version
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DEPENDENCIES = {
    "requirements.txt": [
        "streamlit",
        "httpx",
        "pydantic",
        "python-dotenv",
    ],
    "requirements-api.txt": [
        "fastapi",
        "uvicorn",
        "openai",
        "pydantic",
        "python-dotenv",
        "sentence-transformers",
        "torch",
        "transformers",
    ],
}


def main():
    for filename, packages in DEPENDENCIES.items():
        lines = [
            f"{package}=={version(package)}"
            for package in packages
        ]

        path = BASE_DIR / filename
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        print(f"\n=== {filename} ===")
        print("\n".join(lines))


if __name__ == "__main__":
    main()