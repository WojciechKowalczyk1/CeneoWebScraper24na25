# CeneoWebScraper

**CeneoWebScraper** to aplikacja webowa do pobierania i analizy opinii oraz ocen produktów z serwisu Ceneo. Umożliwia szybki wgląd w dane dotyczące produktów, ułatwiając podejmowanie świadomych decyzji zakupowych.

---

## 🎯 Cel aplikacji

Głównym celem CeneoWebScraper jest umożliwienie użytkownikowi:

- pobierania opinii o produktach z platformy Ceneo na podstawie unikalnego ID produktu,
- analizowania ocen, wad i zalet produktów,
- filtrowania i sortowania danych według wybranych kryteriów,
- pobierania danych w formacie JSON,
- wizualizacji statystyk za pomocą wykresów.

---

## ⚙️ Opis działania aplikacji

1. Użytkownik wprowadza **ID produktu Ceneo**.
2. Aplikacja pobiera wszystkie dostępne **opinie, oceny, rekomendacje, wady i zalety**.
3. Opinie prezentowane są w czytelnej tabeli z możliwością:
   - filtrowania po treści, autorze, dacie, rekomendacji,
   - sortowania danych.
4. Możliwe jest:
   - **pobranie danych jako plik JSON**,
   - **wygenerowanie wykresów** (słupkowy i kołowy) przedstawiających rozkład ocen i rekomendacji.

---

## 🧰 Zastosowane biblioteki

| Biblioteka     | Zastosowanie |
|----------------|--------------|
| **Flask**      | Tworzenie aplikacji webowej i routing |
| **Requests**   | Pobieranie stron internetowych z serwisu Ceneo |
| **Bootstrap**  | Stylowanie i responsywny interfejs użytkownika |
| **Jinja2**     | Szablony HTML generowane dynamicznie |

---

## 🧪 Zastosowane podejścia

- **Web Scraping**: wykorzystanie BeautifulSoup do ekstrakcji danych ze stron Ceneo.
- **Responsywność UI**: projekt oparty na Bootstrapie działa poprawnie zarówno na desktopie, jak i urządzeniach mobilnych.
- **Sortowanie i filtrowanie**: użytkownik może analizować opinie według wielu kryteriów.
- **Wizualizacja danych**: generowanie wykresów na podstawie zebranych opinii.
- **Eksport danych**: możliwość pobrania opinii w formacie `.json` do dalszej analizy.

---

## Struktura opinii w serwisie Ceneo.pl
|Składowa|Zmienna|Selektor|
|--------|-------|--------|
|opinia|opinion|div.js_product-review:not(.user-post--highlight)|
|identyfikator opinii|opinion_id|["data-entry-id"]|
|autor|author|span.user-post__author-name|
|rekomendacja|recommendation|span.user-post__author-recomendation > em|
|liczba gwiazdek|stars|span.user-post__score-count|
|treść opinii|content|div.user-post__text|
|lista zalet|pros|div.review-feature__item--positive|
|lista wad|cons|div.review-feature__item--negative|
|ile osób uznało opinię za przydatną|useful|button.vote-yes["data-total-vote"]|
|ile osób uznało opinię za nieprzydatną|useless|button.vote-no["data-total-vote"]|
|data wystawienia opinii|post_date|span.user-post__published > time:nth-child(1)["datetime"]|
|data zakupu produktu|purchase_date|span.user-post__published > time:nth-child(2)["datetime"]|