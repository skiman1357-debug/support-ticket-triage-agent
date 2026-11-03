# Przygotowanie wdrożenia

## Teraz: sprawdzenie kontenera na GitHubie

1. Skopiuj zawartość paczki do głównego folderu projektu PythonProject5.
   Dockerfile musi znajdować się obok api.py. Zachowaj strukturę folderu .github.
   README.md jest nowym plikiem: jeżeli samodzielnie dodałeś już README,
   połącz jego treść z plikiem z paczki zamiast zastępować go bez sprawdzenia.
2. W terminalu projektu wykonaj:

```powershell
git add Dockerfile .dockerignore README.md DEPLOYMENT_PL.md .github/workflows/container-check.yml
git diff --cached --stat
git commit -m "Add CPU Docker deployment and container checks"
git push
```

3. Otwórz repozytorium na GitHubie, następnie Actions i Container check.
   Po pushu zadanie uruchomi się automatycznie. Można też uruchomić je ręcznie
   przez Run workflow. Jeśli Actions są wyłączone, włącz je dla repozytorium.
4. Poczekaj na zakończenie. Pierwsze budowanie pobiera biblioteki i model.
5. Przy błędzie otwórz czerwony etap i prześlij końcowy fragment logu zawierający
   pierwszy właściwy błąd. Nie zmieniaj samodzielnie wersji bibliotek.

Nie trzeba instalować Dockera na Windows ani podawać kluczy do testu CI.
Workflow nie wdraża aplikacji i nie kupuje hostingu. Zużywa zasoby GitHub Actions
zgodnie z zasadami Twojego konta.

## Po zielonym wyniku: Hugging Face

Przed płatnością sprawdź cenę i warunki widoczne na swoim koncie.
Utwórz Docker Space (Blank) na CPU Basic. Dla tego demo aplikacja musi być
dostępna dla serwera Streamlit bez dodatkowego logowania do Hugging Face;
publiczny Space spełnia ten warunek, a /triage nadal chroni własny klucz API.
Publiczny Space ujawnia także kod repozytorium.

W Settings ustaw Secrets XAI_API_KEY i TRIAGE_API_KEY oraz Variable XAI_MODEL.
Wartości wpisuj wyłącznie w panelu hostingu, nie przesyłaj ich na czacie.
Do Space prześlij Dockerfile, README.md, requirements-api.txt, osiem modułów
backendu wskazanych w Dockerfile, oba pliki testowe i data/knowledge_base.json.
Nie przesyłaj .env. Hugging Face sam zbuduje i uruchomi kontener.

Po uruchomieniu sprawdź /health. Oczekiwany wynik:

```json
{"status":"ok","knowledge_documents":6}
```

Następnie ustaw publiczny adres API i sekrety w Streamlit Cloud zgodnie z README.
Ostateczny test obejmuje poprawne zgłoszenie, źródła, przypadek bez wiedzy oraz
incydent bezpieczeństwa. Te próby wywołują xAI i mogą generować opłaty.

## Co zostało sprawdzone przy przygotowaniu

Odczytano kod i konfigurację z dostarczonej paczki. Potwierdzono w indeksie
PyTorch istnienie pakietu 2.15.0+cpu dla CPython 3.13 / Linux AMD64.
Pełne budowanie obrazu i testy integracyjne wymagają wyniku GitHub Actions.
Dotychczasowe 24 testy to wynik zgłoszony lokalnie przez autora, nie wynik
uruchomienia nowego kontenera.
