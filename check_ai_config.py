import os
from pathlib import Path

from dotenv import load_dotenv


def main():
    env_path = Path(__file__).resolve().parent / ".env"

    if not env_path.is_file():
        raise FileNotFoundError(
            f"Nie znaleziono pliku konfiguracji: {env_path}"
        )

    load_dotenv(env_path, override=False)

    api_key = os.getenv("XAI_API_KEY", "").strip()
    model = os.getenv("XAI_MODEL", "").strip()

    if not api_key or api_key == "tu_wklej_swoj_klucz":
        raise ValueError("Uzupełnij XAI_API_KEY w pliku .env.")

    if not model:
        raise ValueError("Uzupełnij XAI_MODEL w pliku .env.")

    print("Klucz API: wczytany")
    print(f"Model: {model}")
    print("Konfiguracja gotowa. Nie wykonano zapytania do API.")


if __name__ == "__main__":
    main()