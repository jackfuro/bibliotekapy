import datetime
from datetime import date
import json
import os

# ----------------- WCZYTYWANIE I ZAPIS DANYCH -----------------

def wczytaj_ksiazki():
    if not os.path.exists("ksiazki.json"):
        return []
    with open("ksiazki.json", "r", encoding="utf-8") as f:
        return json.load(f)

def zapisz_ksiazki():
    with open("ksiazki.json", "w", encoding="utf-8") as f:
        json.dump(ksiazki, f, ensure_ascii=False, indent=4)

def wczytaj_historie():
    if not os.path.exists("historia.json"):
        return []
    with open("historia.json", "r", encoding="utf-8") as f:
        dane = json.load(f)
        for w in dane:
            w["data_wypozyczenia"] = datetime.date.fromisoformat(w["data_wypozyczenia"])
            w["data_zwrotu"] = datetime.date.fromisoformat(w["data_zwrotu"])
        return dane

def zapisz_historie():
    dane = []
    for h in historia:
        dane.append({
            "id_ksiazki": h["id_ksiazki"],
            "id_studenta": h["id_studenta"],
            "data_wypozyczenia": h["data_wypozyczenia"].isoformat(),
            "data_zwrotu": h["data_zwrotu"].isoformat()
        })
    with open("historia.json", "w", encoding="utf-8") as f:
        json.dump(dane, f, ensure_ascii=False, indent=4)

def wczytaj_studenci():
    if not os.path.exists("studenci.json"):
        return []
    with open("studenci.json", "r", encoding="utf-8") as f:
        return json.load(f)

def zapisz_studentow():
    with open("studenci.json", "w", encoding="utf-8") as f:
        json.dump(studenci, f, ensure_ascii=False, indent=4)

def wczytaj_wypozyczenia():
    if not os.path.exists("wypozyczenia.json"):
        return []
    with open("wypozyczenia.json", "r", encoding="utf-8") as f:
        dane = json.load(f)
        for w in dane:
            w["data_wypozyczenia"] = datetime.date.fromisoformat(w["data_wypozyczenia"])
            w["data_zwrotu"] = w["data_wypozyczenia"] + datetime.timedelta(days=90)
        return dane

def zapisz_wypozyczenia():
    dane = []
    for w in wypozyczenia:
        dane.append({
            "id_ksiazki": w["id_ksiazki"],
            "id_studenta": w["id_studenta"],
            "data_wypozyczenia": w["data_wypozyczenia"].isoformat(),
        })
    with open("wypozyczenia.json", "w", encoding="utf-8") as f:
        json.dump(dane, f, ensure_ascii=False, indent=4)

# ----------------- INICJALIZACJA -----------------

ksiazki = wczytaj_ksiazki()
studenci = wczytaj_studenci()
wypozyczenia = wczytaj_wypozyczenia()
historia = wczytaj_historie()

MAX_WYPOZYCZEN = 5
MAX_STUDENTOW = 15

# ----------------- FUNKCJE -----------------

def pokaz_ksiazki():
    print("\nLista książek:")
    print(f"{'ID':<3} {'Autor':<20} {'Tytuł':<25} {'Rok':<5} {'Strony':<7} {'Dostępne/Łącznie':<15}")
    for k in ksiazki:
        dostepne = k["egzemplarze"] - k["wypozyczone"]
        print(f"{k['id']:<3} {k['autor']:<20} {k['tytul']:<25} {k['rok']:<5} {k['strony']:<7} {dostepne}/{k['egzemplarze']:<15}")

def pokaz_studentow():
    print("\nLista studentów:")
    print(f"{'ID':<3} {'Imię i nazwisko':<25} {'Wypożyczone książki (ID)':<30}")
    for s in studenci:
        if s.get("ukryty"):
            continue
        wyp = ','.join(str(idk) for idk in s["wypozyczone_ksiazki"])
        print(f"{s['id']:<3} {s['imie']:<25} {wyp:<30}")

def pokaz_wypozyczenia():
    if not wypozyczenia:
        print("\nBrak aktywnych wypożyczeń.")
        return

    print("\nAktywne wypożyczenia:")
    print(f"{'ID książki':<12}{'Tytuł':<30}{'ID studenta':<14}{'Student':<25}{'Data wypożyczenia':<20}{'Termin zwrotu':<20}")

    for w in wypozyczenia:
        ks = next((k for k in ksiazki if k["id"] == w["id_ksiazki"]), None)
        st = next((s for s in studenci if s["id"] == w["id_studenta"]), None)
        if ks and st:
            data_wyp = w["data_wypozyczenia"].strftime("%Y-%m-%d")
            data_zwrotu = w["data_zwrotu"].strftime("%Y-%m-%d")
            print(f"{ks['id']:<12}{ks['tytul']:<30}{st['id']:<14}{st['imie']:<25}{data_wyp:<20}{data_zwrotu:<20}")

def pokaz_historie():
    if not historia:
        print("\nBrak historii wypożyczeń.")
        return
    print("\nHistoria wypożyczeń:")
    print(f"{'ID książki':<12}{'Tytuł':<30}{'ID studenta':<14}{'Student':<25}{'Data wypożyczenia':<20}{'Data zwrotu':<20}")
    for h in historia:
        ks = next((k for k in ksiazki if k["id"] == h["id_ksiazki"]), None)
        st = next((s for s in studenci if s["id"] == h["id_studenta"]), None)
        if ks and st:
            data_wyp = h["data_wypozyczenia"].strftime("%Y-%m-%d")
            data_zwrotu = h["data_zwrotu"].strftime("%Y-%m-%d")
            print(f"{ks['id']:<12}{ks['tytul']:<30}{st['id']:<14}{st['imie']:<25}{data_wyp:<20}{data_zwrotu:<20}")

def dodaj_studenta():
    if len(studenci) >= MAX_STUDENTOW:
        print("Osiągnięto maksymalną liczbę studentów.")
        return
    imie = input("Podaj imię i nazwisko studenta: ").strip()
    if not imie:
        print("Imię nie może być puste.")
        return
    nowy_id = max((s["id"] for s in studenci), default=0) + 1
    studenci.append({"id": nowy_id, "imie": imie, "wypozyczone_ksiazki": []})
    zapisz_studentow()
    print("Student dodany.")

def usun_studenta():
    pokaz_studentow()
    try:
        ids = int(input("Podaj ID studenta do ukrycia: "))
    except ValueError:
        print("Błędne ID.")
        return
    student = next((s for s in studenci if s["id"] == ids), None)
    if not student:
        print("Nie znaleziono studenta.")
        return
    if student["wypozyczone_ksiazki"]:
        print("Nie można ukryć studenta z aktywnymi wypożyczeniami.")
        return
    student["ukryty"] = True
    zapisz_studentow()
    print("Student został oznaczony jako ukryty.")

def dodaj_ksiazke():
    if len(ksiazki) >= 100:
        print("Osiągnięto maksymalną liczbę książek.")
        return
    autor = input("Autor: ")
    tytul = input("Tytuł: ")
    try:
        rok = int(input("Rok wydania: "))
        strony = int(input("Liczba stron: "))
        egzemplarze = int(input("Liczba egzemplarzy: "))
    except ValueError:
        print("Nieprawidłowe dane.")
        return
    nowy_id = max((k["id"] for k in ksiazki), default=0) + 1
    ksiazki.append({
        "id": nowy_id,
        "autor": autor,
        "tytul": tytul,
        "rok": rok,
        "strony": strony,
        "egzemplarze": egzemplarze,
        "wypozyczone": 0
    })
    zapisz_ksiazki()
    print("Książka dodana.")

def pokaz_ukrytych_studentow():
    print("\nUkryci studenci:")
    ukryci = [s for s in studenci if s.get("ukryty")]
    if not ukryci:
        print("Brak ukrytych studentów.")
        return
    print(f"{'ID':<3} {'Imię i nazwisko':<25}")
    for s in ukryci:
        print(f"{s['id']:<3} {s['imie']:<25}")

def przywroc_studenta():
    pokaz_ukrytych_studentow()
    try:
        ids = int(input("Podaj ID studenta do przywrócenia: "))
    except ValueError:
        print("Błędne ID.")
        return
    student = next((s for s in studenci if s.get("ukryty") and s["id"] == ids), None)
    if not student:
        print("Nie znaleziono ukrytego studenta.")
        return
    student.pop("ukryty", None)
    zapisz_studentow()
    print("Student został przywrócony.")

def wypozycz_ksiazke():
    pokaz_studentow()
    try:
        ids = int(input("ID studenta: "))
    except ValueError:
        print("Błędne ID.")
        return
    student = next((s for s in studenci if s["id"] == ids and not s.get("ukryty")), None)
    if not student:
        print("Nie znaleziono studenta lub jest ukryty.")
        return
    if len(student["wypozyczone_ksiazki"]) >= MAX_WYPOZYCZEN:
        print("Student osiągnął limit wypożyczeń.")
        return
    pokaz_ksiazki()
    try:
        idk = int(input("ID książki do wypożyczenia: "))
    except ValueError:
        print("Błędne ID.")
        return
    ksiazka = next((k for k in ksiazki if k["id"] == idk), None)
    if not ksiazka:
        print("Nie znaleziono książki.")
        return
    if ksiazka["wypozyczone"] >= ksiazka["egzemplarze"]:
        print("Brak dostępnych egzemplarzy.")
        return
    if idk in student["wypozyczone_ksiazki"]:
        print("Student ma już wypożyczoną tę książkę.")
        return
    ksiazka["wypozyczone"] += 1
    student["wypozyczone_ksiazki"].append(idk)
    data_wyp = date.today()
    wypozyczenia.append({
        "id_ksiazki": idk,
        "id_studenta": ids,
        "data_wypozyczenia": data_wyp,
        "data_zwrotu": data_wyp + datetime.timedelta(days=90)
    })
    zapisz_ksiazki()
    zapisz_studentow()
    zapisz_wypozyczenia()
    print("Książka wypożyczona.")

def raport_zwroty():
    print("\nRaport wypożyczeń (mniej niż 14 dni do terminu zwrotu):")
    print(f"{'ID książki':<10} {'Tytuł':<25} {'ID studenta':<12} {'Student':<25} {'Data wypożyczenia':<20} {'Termin zwrotu':<20}")
    for w in wypozyczenia:
        ks = next((k for k in ksiazki if k["id"] == w["id_ksiazki"]), None)
        st = next((s for s in studenci if s["id"] == w["id_studenta"]), None)
        if ks and st:
            days_remaining = (w["data_zwrotu"] - date.today()).days
            if days_remaining < 14:
                data_wyp = w["data_wypozyczenia"].strftime("%Y-%m-%d")
                data_zwr = w["data_zwrotu"].strftime("%Y-%m-%d")
                print(f"{ks['id']:<10} {ks['tytul']:<25} {st['id']:<12} {st['imie']:<25} {data_wyp:<20} {data_zwr:<20}")

def zwroc_ksiazke():
    pokaz_studentow()
    try:
        ids = int(input("ID studenta: "))
    except ValueError:
        print("Błędne ID.")
        return
    student = next((s for s in studenci if s["id"] == ids), None)
    if not student or not student["wypozyczone_ksiazki"]:
        print("Student nie ma wypożyczeń.")
        return
    print(f"Wypożyczone książki: {student['wypozyczone_ksiazki']}")
    try:
        idk = int(input("ID książki do zwrotu: "))
    except ValueError:
        print("Błędne ID.")
        return
    if idk not in student["wypozyczone_ksiazki"]:
        print("Nie wypożyczono tej książki.")
        return
    ksiazka = next((k for k in ksiazki if k["id"] == idk), None)
    wyp = next((w for w in wypozyczenia if w["id_ksiazki"] == idk and w["id_studenta"] == ids), None)
    if not wyp:
        print("Nie znaleziono wypożyczenia.")
        return
    # Aktualizacja danych
    ksiazka["wypozyczone"] -= 1
    student["wypozyczone_ksiazki"].remove(idk)
    wypozyczenia.remove(wyp)
    # Dodanie do historii
    historia.append({
        "id_ksiazki": idk,
        "id_studenta": ids,
        "data_wypozyczenia": wyp["data_wypozyczenia"],
        "data_zwrotu": date.today()
    })
    zapisz_ksiazki()
    zapisz_studentow()
    zapisz_wypozyczenia()
    zapisz_historie()
    print("Zwrócono książkę.")

# ----------------- MENU -----------------

def menu():
    while True:
        print("\nMENU:")
        print("1. Wyświetl książki")
        print("2. Wyświetl studentów")
        print("3. Wyświetl wypożyczenia")
        print("4. Wyświetl historię wypożyczeń")
        print("5. Dodaj studenta")
        print("6. Ukryj studenta")
        print("7. Dodaj książkę")
        print("8. Wypożycz książkę")
        print("9. Zwróć książkę")
        print("10. Kończące się wypożyczenia")
        print("11. Przywróć ukrytego studenta")
        print("0. Wyjście")
        wybor = input("Wybierz opcję: ")
        if wybor == "1":
            pokaz_ksiazki()
        elif wybor == "2":
            pokaz_studentow()
        elif wybor == "3":
            pokaz_wypozyczenia()
        elif wybor == "4":
            pokaz_historie()
        elif wybor == "5":
            dodaj_studenta()
        elif wybor == "6":
            usun_studenta()
        elif wybor == "7":
            dodaj_ksiazke()
        elif wybor == "8":
            wypozycz_ksiazke()
        elif wybor == "9":
            zwroc_ksiazke()
        elif wybor == "10":
            raport_zwroty()
        elif wybor == "11":
            przywroc_studenta()
        elif wybor == "0":
            print("Do widzenia!")
            break
        else:
            print("Niepoprawna opcja.")

if __name__ == "__main__":
    menu()

