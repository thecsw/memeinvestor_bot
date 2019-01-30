"""
This module will be responsible for
providing help information on commands
"""

help_dict = {
    'attivi': "Mostra una lista di tutti gli investimenti attivi.",
    'saldo': "Mostra il tuo saldo in MemeCoins.",
    'bancarotta': "Se hai meno di 100 MemeCoins, questo comando portera il tuo saldo a 100.",
    'crea': "Crea il tuo conto.",
    'creasocietà': "Crea una nuova società e ti imposta come CEO. Costo: 1,000,000 Memecoins.",
    'licenzia': "Rimuove i membri dalla società. Solo il CEO può licenziare un executive.",
    'società': "Mostra riguardo la tua società.",
    'aiuto': "Mostra un aiuto.",
    'invest': "Invests the specified number of Memecoins into the post. Depending on the amount of upvotes the post gets in the next 4 hours, you will either receive a return or lose il tuo investment.",
	'investi': "Investi l'ammontare specificato di MemeCoin in uno specifico post. A seconda dell'ammontare di upvotes del post, dopo 4 ore potrai ricevere o perdere il tuo investimento.",
    'invita': "Invita l'utente selezionato nella società` command.",
    'entrainsocietà': "Entra nella società da te selezionata. Se la società è privata, dovrai prima essere stato invitato.",
    'lasciasocietà': "Ti rimuove dalla tua società attuale.",
    'mercato': "Mostra delle statistiche sul mercato.",
    'promuovi': "Promuove un membro della società. Se il membro era un trader semplice, verrà promosso a Executive. Se era Executive, verrà promosso a CEO (scambiando posto col CEO attuale)",
    'impostaprivato': "Imposta una società come privata. Gli utenti potranno accedere solo usando il comando `!invita`.",
    'impostapubblico': "Imposta la società come pubblica. Tutti gli utenti possono accedere",
    'template': "Permette a OP di specificare il link del template che verrà inserito nel messaggio sticky del post.",
    'top': "Mostra i migliori investitori della società.",
    'upgrade': "Aumenta il livello della società, così da aumentare il numero di utenti che possono farne parte. Costa 4 milioni Memecoins per aumentare al livello 2, 16M per il livello 3, 64 per il livello 4 e così via.",
    'versione': "Mostra quando è stata installata la versione corrente del bot."
}
