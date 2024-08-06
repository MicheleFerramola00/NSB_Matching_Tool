import re
from groq import Groq

# API Key (assicurati di proteggerla adeguatamente)
api_key = "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"

# Crea un'istanza del client Groq
client = Groq(api_key=api_key)


# Funzione per leggere le righe dal file, rimuovere righe vuote e aggiungere solo righe pertinenti a una lista
def leggi_righe(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        righe = file.readlines()
    righe_pertinenti = []
    for riga in righe:
        if riga.strip() != "":
            righe_pertinenti.append(riga.strip())
    return righe_pertinenti


# Funzione principale per processare le righe e creare una lista di soggetti
def processa_soggetti(file_path):
    righe = leggi_righe(file_path)
    soggetti = []
    soggetto_corrente = []
    descrizione = ""

    for riga in righe:
        if "A -" in riga:
            parts = riga.split("A -", 1)
        elif "B -" in riga:
            parts = riga.split("B -", 1)
        elif "C -" in riga:
            parts = riga.split("C -", 1)
        elif "D -" in riga:
            parts = riga.split("D -", 1)
        elif "E -" in riga:
            parts = riga.split("E -", 1)
        else:
            if descrizione:
                descrizione += " " + riga
            else:
                descrizione = riga
            continue

        if soggetto_corrente:
            soggetto_corrente.append(descrizione.strip())
            soggetti.append(soggetto_corrente)

        nome = parts[0][:-1].strip()  # Rimuove l'ultimo carattere della stringa e spazi
        descrizione = parts[1].strip()  # Inizia una nuova descrizione
        soggetto_corrente = [nome]

    # Aggiungi l'ultimo soggetto
    if soggetto_corrente:
        soggetto_corrente.append(descrizione.strip())
        soggetti.append(soggetto_corrente)

    return soggetti


# Funzione per fare una richiesta al chatbot
def interroga_chatbot(messages):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.1-70b-versatile"
        # https://console.groq.com/docs/models
    )
    return chat_completion.choices[0].message.content


# Funzione per creare il messaggio per il modello
def crea_messaggio(progetto, organizzazioni, parte_domanda_utente):
    introduzione = (
        "I dati dei progetti che ti nominerò avranno questa struttura: "
        "Project Name, Need Type, Need Status, Preferred Way To Solve Need, Themes, Description.\n\n"
        "I dati delle organizzazioni che ti nominerò avranno questa struttura: "
        "Organization Name, Need Type, Need Status, Preferred Way To Solve Need, Themes, Description.\n\n"
        "Ricorda che per eseguire il compito che ti sto per impartire dovrai tenere conto di tutti questi dati e del loro significato.\n\n"
    )

    descrizione_progetto = f"{progetto[0]}: {progetto[1]}"
    descrizioni_organizzazioni = "\n\n".join(
        [f"{organizzazione[0]}: {organizzazione[1]}" for organizzazione in organizzazioni])

    return {
        "role": "user",
        "content": (
            f"{introduzione}"
            f"Ecco la descrizione del progetto:\n\n{descrizione_progetto}\n\n"
            f"Ecco le descrizioni delle organizzazioni:\n\n{descrizioni_organizzazioni}\n\n"
            f"{parte_domanda_utente}"
        )
    }


# Funzione principale per eseguire l'operazione desiderata
def esegui_operazione(operazione):
    progetti = processa_soggetti('Projects_needs.txt')
    organizzazioni = processa_soggetti('Organization_needs.txt')

    if operazione == "partenariati":
        parte_domanda_utente = input(
            "Inserisci la parte della domanda da porre al modello. "
            "Ricorda di specificare che cosa vuoi fare, quanti partenariati possibili vuoi per ogni progetto "
            "e quante aziende minime per partenariato:\n "
        )
        for progetto in progetti:
            messaggio = crea_messaggio(progetto, organizzazioni, parte_domanda_utente)
            risposta = interroga_chatbot([messaggio])
            print(f"Risposta per il progetto '{progetto[0]}':\n{risposta}\n")

    elif operazione == "sinergie":
        # Mostra i nomi di tutti i progetti
        print("Progetti disponibili:")
        for idx, progetto in enumerate(progetti, start=1):
            print(f"{idx}. {progetto[0]}")

        # Chiedi all'utente di scegliere un progetto
        indice_progetto = int(
            input("Di quale progetto vuoi cercare sinergie? Inserisci il numero corrispondente: ")) - 1
        progetto_selezionato = progetti[indice_progetto]

        # Chiedi all'utente di inserire la domanda per il modello in merito alle sinergie
        domanda_sinergie = input("Inserisci la domanda da sottoporre al modello in merito alle sinergie: ")

        # Creare il messaggio per le sinergie
        descrizioni_progetti = "\n\n".join([f"{progetto[0]}: {progetto[1]}" for progetto in progetti])
        messaggio = {
            "role": "user",
            "content": (
                f"I dati dei progetti che ti nominerò avranno questa struttura: "
                "Project Name, Need Type, Need Status, Preferred Way To Solve Need, Themes, Description.\n\n"
                "Ricorda che per eseguire il compito che ti sto per impartire dovrai tenere conto di tutti questi dati e del loro significato.\n\n"
                f"Ecco le descrizioni dei progetti:\n\n{descrizioni_progetti}\n\n"
                f"{domanda_sinergie}"
            )
        }

        # Ottieni e stampa le sinergie per il progetto selezionato
        risposta = interroga_chatbot([messaggio])
        print(f"Risposta del chatbot:\n{risposta}")

    elif operazione == "match":
        # Mostra i nomi di tutte le organizzazioni
        print("Organizzazioni disponibili:")
        for idx, organizzazione in enumerate(organizzazioni, start=1):
            print(f"{idx}. {organizzazione[0]}")

        # Chiedi all'utente di scegliere un'organizzazione
        indice_organizzazione = int(
            input("Di quale organizzazione vuoi cercare match? Inserisci il numero corrispondente: ")) - 1
        organizzazione_selezionata = organizzazioni[indice_organizzazione]

        # Chiedi all'utente di inserire la domanda per il modello in merito al matching
        domanda_matching = input("Inserisci la domanda da sottoporre al modello in merito al matching: ")

        # Creare il messaggio per il matching
        descrizioni_organizzazioni = "\n\n".join(
            [f"{organizzazione[0]}: {organizzazione[1]}" for organizzazione in organizzazioni])
        messaggio = {
            "role": "user",
            "content": (
                f"I dati delle organizzazioni che ti nominerò avranno questa struttura: "
                "Organization Name, Need Type, Need Status, Preferred Way To Solve Need, Themes, Description.\n\n"
                "Ricorda che per eseguire il compito che ti sto per impartire dovrai tenere conto di tutti questi dati e del loro significato.\n\n"
                f"Ecco le descrizioni delle organizzazioni:\n\n{descrizioni_organizzazioni}\n\n"
                f"{domanda_matching}"
            )
        }

        # Ottieni e stampa i match per l'organizzazione selezionata
        risposta = interroga_chatbot([messaggio])
        print(f"Risposta del chatbot:\n{risposta}")

    elif operazione == "partenariato":
        # Mostra i nomi di tutti i progetti
        print("Progetti disponibili:")
        for idx, progetto in enumerate(progetti, start=1):
            print(f"{idx}. {progetto[0]}")

        # Chiedi all'utente di scegliere un progetto
        indice_progetto = int(
            input("Per quale progetto vuoi creare un partenariato? Inserisci il numero corrispondente: ")) - 1
        progetto_selezionato = progetti[indice_progetto]

        # Chiedi all'utente di inserire la domanda per il modello in merito al partenariato
        domanda_partenariato = input("Inserisci la domanda da sottoporre al modello in merito al partenariato: ")

        # Creare il messaggio per il partenariato
        messaggio = crea_messaggio(progetto_selezionato, organizzazioni, domanda_partenariato)

        # Ottieni e stampa i partenariati per il progetto selezionato
        risposta = interroga_chatbot([messaggio])
        print(f"Risposta del chatbot:\n{risposta}")

    else:
        print("Operazione non valida. Per favore, scegli tra 'partenariati', 'match', 'sinergie' o 'partenariato'.")


# Chiedi all'utente quale operazione desidera eseguire
operazione = input("Che operazione desideri eseguire? (partenariati/match/sinergie/partenariato): ").strip().lower()
esegui_operazione(operazione)
