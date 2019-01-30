import datetime
import time

import config
import utils

INVESTMENT_DURATION_VAR = utils.investment_duration_string(config.INVESTMENT_DURATION)

# This message will be sent if an account has been
# successfully created
CREATE_ORG = """
*Conto creato!*

Grazie %USERNAME% per aver creato un conto /r/BancaDelMeme!

Il tuo saldo iniziale è **%BALANCE% MemeCoins**.
"""

def modify_create(username, balance):
    return CREATE_ORG.\
        replace("%USERNAME%", str(username)).\
        replace("%BALANCE%", format(balance, ",d"))

# This message will be sent if a user tries to create an account but already
# has one.
CREATE_EXISTS_ORG = """
Non capisco se sei troppo entusiasta o stai cercando di truffarmi. Hai già un account!
"""

# This message will be sent when an investment
# was successful

INVEST_ORG = """
*%AMOUNT% MemeCoins investiti @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

Il tuo investimento è ora attivo. Valuterò il tuo profitto in %TIME% e aggiornerò questo stesso commento. Non facciamo che ci perdiamo di vista!

Il tuo saldo attuale è **%BALANCE% MemeCoins**.
""".replace("%TIME%", INVESTMENT_DURATION_VAR).\
    replace("%UPVOTES_WORD%", utils.upvote_string())

def modify_invest(amount, initial_upvotes, new_balance):
    return INVEST_ORG.\
        replace("%AMOUNT%", format(amount, ",d")).\
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")).\
        replace("%BALANCE%", format(new_balance, ",d"))

INVEST_WIN_ORG = """
*%AMOUNT% MemeCoins investite @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Il tuo investimento è maturato. È andato alla grande! Hai guadagnato %PROFIT% MemeCoins (%PERCENT%).

*%RETURNED% MemeCoins restituite @ %FINAL_UPVOTES% %UPVOTES_WORD%*

Il tuo nuovo saldo is **%BALANCE% MemeCoins**.
""".replace("%UPVOTES_WORD%", utils.upvote_string())

INVEST_LOSE_ORG = """
*%AMOUNT% MemeCoins investite @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Il tuo investimento è maturato. Non è andato bene! Hai perso %PROFIT% MemeCoins (%PERCENT%).

*%RETURNED% MemeCoins restituiti @ %FINAL_UPVOTES% %UPVOTES_WORD%*

Il tuo nuovo saldo is **%BALANCE% MemeCoins**.
""".replace("%UPVOTES_WORD%", utils.upvote_string())

INVEST_BREAK_EVEN_ORG = """
*%AMOUNT% MemeCoins investite @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Il tuo investimento è maturato. Sei andato in pari! Hai guadagnato %PROFIT% MemeCoins (%PERCENT%).

*%RETURNED% MemeCoins restituiti @ %FINAL_UPVOTES% %UPVOTES_WORD%*

Il tuo nuovo saldo is **%BALANCE% MemeCoins**.
""".replace("%UPVOTES_WORD%", utils.upvote_string())

def modify_invest_return(amount, initial_upvotes,
                         final_upvotes, returned,
                         profit, percent_str, new_balance):
    if profit > 0:
        original = INVEST_WIN_ORG
    elif profit < 0:
        original = INVEST_LOSE_ORG
        profit *= -1
    else:
        original = INVEST_BREAK_EVEN_ORG

    return original.\
        replace("%AMOUNT%", format(amount, ",d")).\
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")).\
        replace("%FINAL_UPVOTES%", format(final_upvotes, ",d")).\
        replace("%RETURNED%", format(returned, ",d")).\
        replace("%PROFIT%", format(profit, ",d")).\
        replace("%PERCENT%", format(percent_str)).\
        replace("%BALANCE%", format(int(new_balance), ",d"))

INVEST_CAPPED_ORG = """
*%AMOUNT% MemeCoins investite @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Il tuo investimento è maturato a %FINAL_UPVOTES% %UPVOTES_WORD%, con un profitto di %PROFIT% MemeCoins (%PERCENT%).

**Congratulazioni,** hai raggiunto il saldo massimo! Hai trionfato in questa sanguinosa competizione nel marketplace, e il tuo portafoglio è gonfissimo! Le future generazioni ti ricorderanno come titano degli investimenti.

*"Alessandro pianse, poiché non c'erano altri mondi da conquistare.."* (...ancora)

Il tuo saldo attuale è **%BALANCE% MemeCoins** (il saldo massimo).
""".replace("%UPVOTES_WORD%", utils.upvote_string())

def modify_invest_capped(amount, initial_upvotes,
                         final_upvotes, returned,
                         profit, percent_str, new_balance):
    return INVEST_CAPPED_ORG.\
        replace("%AMOUNT%", format(amount, ",d")).\
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")).\
        replace("%FINAL_UPVOTES%", format(final_upvotes, ",d")).\
        replace("%PROFIT%", format(profit, ",d")).\
        replace("%PERCENT%", str(percent_str)).\
        replace("%BALANCE%", format(new_balance, ",d"))

# If funds are insufficient to make an investment
# say that
INSUFF_ORG = """
Non hai abbastanza MemeCoins per fare questo investimento.

Il tuo saldo attuale è **%BALANCE% MemeCoins**.

Se hai meno di 100 MemeCoins e nessun investimento in corso, prova ad inviare `!broke`!
"""

def modify_insuff(balance_t):
    return INSUFF_ORG.\
        replace("%BALANCE%", format(balance_t, ",d"))

# Message if you are broke
BROKE_ORG = """
OOps, sei in bancarotta.

Il tuo saldo è stato resettato a 100 MemeCoins. Sta attento la prossima volta.

Sei andato in bancarotta %NUMBER% volte.
"""

def modify_broke(times):
    return BROKE_ORG.\
        replace("%NUMBER%", str(times))

# Message if you are broke and have investimenti attivi
BROKE_ACTIVE_ORG = """
Hai ancora %ACTIVE% investmento/i attivi.

Dovrai attendere che vengano completati.
"""

def modify_broke_active(active):
    return BROKE_ACTIVE_ORG.\
        replace("%ACTIVE%", str(active))

# Message if you are broke and have more than 100 MemeCoins
BROKE_MONEY_ORG = """
Non sei così povero! Hai ancora **%AMOUNT% MemeCoins**.
"""

def modify_broke_money(amount):
    return BROKE_MONEY_ORG.\
        replace("%AMOUNT%", format(amount, ",d"))

HELP_ORG = """
*Benvenuto su BancaDelMeme!*

Io sono un bot che vi aiuterà ad investire in *MEME* e farci una fortuna. Mica come le criptovalute.

Ecco una lista di tutti i comandi che funzionano con me:
Here is a list of commands that summon me:

### COMANDI GENERALI
- `!active`
- `!balance`
- `!broke`
- `!create`
- `!help`
- `!invest <amount>`
- `!market`
- `!top`
- `!version`
- `!template https://imgur.com/...` **(solo per OP, utile per linkare i template)**

### FIRM COMMANDS
- `!firm`
- `!createfirm <name>`
- `!joinfirm <name>`
- `!leavefirm`
- `!promote <username>` **(CEO and Exec Only)**
- `!fire <username>` **(CEO and Exec Only)**
- `!upgrade` **(CEO Only)**
- `!setprivate` **(CEO Only)**
- `!setpublic` **(CEO Only)**
- `!invite <username>` **(CEO and Exec Only)**

Per avere aiuto su un singolo comando, semplicemente scrivi `!help command`
"""

BALANCE_ORG = """
Attualmente, il tuo saldo è **%BALANCE% MemeCoins**.
"""

def modify_balance(balance):
    return BALANCE_ORG.\
        replace("%BALANCE%", format(balance, ",d"))

ACTIVE_ORG = """
Hai %NUMBER% investimenti attivi:

%INVESTMENTS_LIST%
"""

def modify_active(active_investments):
    if not active_investments:
        return "Non hai alcun investimento attivo al momento."

    investments_strings = []
    i = 1
    for inv in active_investments:
        seconds_remaining = inv.time + config.INVESTMENT_DURATION - time.time()
        if seconds_remaining > 0:
            td = datetime.timedelta(seconds=seconds_remaining)
            remaining_string = str(td).split(".")[0] + " remaining"
        else:
            remaining_string = "in elaborazione"
        post_url = f"https://www.reddit.com/r/BancaDelMemecomments/{inv.post}"
        inv_string = f"[#{i}]({post_url}): {inv.amount} M¢ @ {inv.upvotes} %UPVOTES_WORD% ({remaining_string})"\
            .replace("%UPVOTES_WORD%", utils.upvote_string())
        investments_strings.append(inv_string)
        i += 1
    investments_list = "\n\n".join(investments_strings)

    return ACTIVE_ORG.\
        replace("%NUMBER%", str(len(active_investments))).\
        replace("%INVESTMENTS_LIST%", investments_list)

MIN_INVEST_ORG = """
L'investimento minimo consentito è di 100 MemeCoins.
"""

MARKET_ORG = """
Il mercato, in questo momento, ha **%NUMBER%** investimenti attivi.

Tutti gli investitori possiedono **%MONEY% MemeCoins**.

Ci sono %HODL% MemeCoins** in circolazione su investimenti al momento.
"""

def modify_market(inves, cap, invs_cap):
    return MARKET_ORG.\
        replace("%NUMBER%", format(int(inves), ",d")).\
        replace("%MONEY%", format(int(cap), ",d")).\
        replace("%HODL%", format(int(invs_cap), ",d"))

# Message used for !top command
TOP_ORG = """
Gli investitori con il valore netto più alto (saldo + investimenti attivi): 

%TOP_STRING%
"""

def modify_top(leaders):
    top_string = ""
    for leader in leaders:
        top_string = f"{top_string}\n\n{leader.name}: {int(leader.networth)} MemeCoins"

    top_response = TOP_ORG
    top_response = top_response.replace("%TOP_STRING%", top_string)
    return top_response

DELETED_COMMENT_ORG = """
Dov'è finito?

Comunque, l'investimento è andato perduto.
"""

TEMPLATE_HINT_ORG = """
---

Psst, %NAME%, puoi scrivere `!template https://imgur.com/...` per pubblicare il template del tuo post! Alla fine è uno degli scopi di BancaDelMeme! ;)
"""

INVEST_PLACE_HERE_NO_FEE = """
**GLI INVESTIMENTI VANNO QUI - SOLO LE RISPOSTE DIRETTE A QUESTO MESSAGGIO VERRANNO ELABORATE**

Per prevenire spam e altri catastrofi naturali, rispondo solamente a risposte dirette in questo messaggio. Altri comandi verranno ignorati e potrebbero addirittura venire penalizzati. Teniamo la nostra piazza affari bella pulita!

---

- Visita [BancaDelMeme](/r/BancaDelMeme) per aiuto, statistiche di piazza affari, e profili degli investitori. (Il sito potrebbe arrivare in futuro)

- Visit /r/MemeInvestor_bot per domande o suggerimenti riguardo la versione originale di questo bot in uso su /r/meme_economy o supportali tramite il loro patreon: [patreon](https://www.patreon.com/memeinvestor_bot)

- Nuovo utente? Ti senti perso e confuso? Rispondi `!help` a questo messaggio, o visita la pagina [Wiki](https://www.reddit.com/r/BancaDelMeme/wiki/index) per una spiegazione più dettagliata.
"""

def invest_no_fee(name):
    return INVEST_PLACE_HERE_NO_FEE + TEMPLATE_HINT_ORG.\
        replace("%NAME%", name)

INVEST_PLACE_HERE = """
**GLI INVESTIMENTI VANNO QUI - SOLO LE RISPOSTE DIRETTE A QUESTO MESSAGGIO VERRANNO ELABORATE**

Per prevenire spam e altri catastrofi naturali, rispondo solamente a risposte dirette in questo messaggio. Altri comandi verranno ignorati e potrebbero addirittura venire penalizzati. Teniamo la nostra piazza affari bella pulita!

L'autore di questo post ha pagato **%MEMECOIN% MemeCoins** per postare.

---

- Visita [BancaDelMeme](/r/BancaDelMeme) per aiuto, statistiche di piazza affari, e profili degli investitori. (Il sito potrebbe arrivare in futuro)

- Visit /r/MemeInvestor_bot per domande o suggerimenti riguardo la versione originale di questo bot in uso su /r/meme_economy o supportali tramite il loro patreon: [patreon](https://www.patreon.com/memeinvestor_bot)

- Nuovo utente? Ti senti perso e confuso? Rispondi `!help` a questo messaggio, o visita la pagina [Wiki](https://www.reddit.com/r/BancaDelMeme/wiki/index) per una spiegazione più dettagliata.
""" + TEMPLATE_HINT_ORG

def modify_invest_place_here(amount, name):
    return INVEST_PLACE_HERE.\
        replace("%MEMECOIN%", format(int(amount), ",d")) + TEMPLATE_HINT_ORG.\
        replace("%NAME%", name)

INSIDE_TRADING_ORG = """
Non puoi investire nei tuoi stessi meme! Non è consentito fare insider trading!
"""

def modify_grant_success(grantee, badge):
    return f"Badge assegnato con successo `{badge}` a {grantee}!"

def modify_grant_failure(failure_message):
    return f"Oops, Non ho potuto assegnare il badge ({failure_message})"

NO_ACCOUNT_POST_ORG = """
Hai bisogno di creare un account per postare un meme. Per favore, rispondi ad uno dei miei commenti con `!create`.

Per avere più informazioni, scrivi `!help`
"""

PAY_TO_POST_ORG = """
Date le ultime regolamentazioni di mercato, per postare un meme dovrai pagare una tassa del 6% con un minimo di 250 MemeCoins.

Se non puoi permettertelo, il tuo post verrà cancellato. Nulla di personale, barbùn. Sono le regole di piazza affari.

Fatti risentire quando avrai più soldi, rimanda il meme con un nuovo post.

Il tuo saldo attuale è **%MEMECOINS% MemeCoins**.
"""

def modify_pay_to_post(balance):
    return PAY_TO_POST_ORG.\
        replace("%MEMECOINS%", str(balance))

MAINTENANCE_ORG = """
**Il bot è in manutenzione per ragioni tecniche.**

**Dovrebbe tornare online a breve. (Qualche ora)**

**Ci scusiamo per ogni disagio causato.**
"""

firm_none_org = """
Non ti trovi in una società.

Puoi crearne una con il comando **!createfirm <NOME SOCIETA>**, oppure richiedere di accedere ad una esistente con il comando **!joinfirm <NOME SOCIETA ESISTENTE>**.
"""

firm_org = """
SOCIETÀ: **%FIRM_NAME%**

BILANCIO SOCIETÀ: **%BALANCE%** Memecoins

LIVELLO SOCIETÀ: **%LEVEL%**

Il tuo Rank: **%RANK%**

----

## MEMBRI:

*CEO:*
%CEO%

*Executives:*
%EXECS%

*Trader semplici:*
%TRADERS%

----

Puoi lasciare questa società con il comando **!leavefirm**.
"""

rank_strs = {
    "ceo": "CEO",
    "exec": "Executive",
    "": "Trader semplice"
}

def modify_firm(rank, firm, ceo, execs, traders):
    rank_str = rank_strs[rank]
    return firm_org.\
        replace("%RANK%", rank_str).\
        replace("%FIRM_NAME%", firm.name).\
        replace("%CEO%", ceo).\
        replace("%EXECS%", execs).\
        replace("%TRADERS%", traders).\
        replace("%BALANCE%", str(firm.balance)).\
        replace("%LEVEL%", str(firm.rank + 1))

createfirm_exists_failure_org = """
Sei già all'interno di questa società: **%FIRM_NAME%**

Per favore, esci usando il comando *!leavefirm*, prima di accedere in una nuova società.
"""

createfirm_cost_failure_org = """
Creare una società costa 1,000,000 Memecoins, e tu sei un poveraccio. Vai a fare della grana, e fatti rivedere solo quando ne avrai abbastanza.
"""

def modify_createfirm_exists_failure(firm_name):
    return createfirm_exists_failure_org.\
        replace("%FIRM_NAME%", firm_name)

createfirm_format_failure_org = """
I nomi delle società devono avere tra 4 e 32 caratteri. Sono consentiti solo caratteri alfanumerici, spazi, trattini medi e bassi (- e _)
"""

createfirm_nametaken_failure_org = """
Il nome scelto per la società è già in uso. Se non stai tentando di organizzare una truffa finanziaria, per favore riprova.
"""

createfirm_org = """
La nuova società è stata creata correttamente, sto chiamando il notaio.

Tu sei il CEO della società e hai il potere di
"""

nofirm_failure_org = leavefirm_none_failure_org = """
Non sei in una società.
"""
no_firm_failure_org = leavefirm_none_failure_org

leavefirm_ceo_failure_org = """
Al momento sei il CEO della tua società, quindi non ti è permesso andartene. Non fare lo schettino della finanza.

Se davvero vuoi andartene, dovrai prima rinunciare al tuo ruolo. Per farlo dovrai promuovere un executive al ruolo di CEO col comando **!promote <username>**.
"""

leavefirm_org = """
Sei uscito dalla società.
"""

not_ceo_org = """
Solo il CEO può farlo.
"""

not_ceo_or_exec_org = """
Solo il CEO e gli executives possono farlo.
"""

promote_failure_org = """
Non sono riuscito a promuovere l'utente, assicurati che sia corretto (o che non sia un prestanome).
"""

promote_full_org = """
Non ho potuto promuovere questo impiegato, poiché la società è alla sua capacità massima. 
**Numero di execs:** %EXECS%
**Livello società:** %LEVEL%

Il CEO della società può aumentare il livello col comando `!upgrade`.
"""

def modify_promote_full(firm):
    return promote_full_org.\
        replace("%EXECS%", str(firm.execs)).\
        replace("%LEVEL%", str(firm.rank + 1))

def modify_promote(user):
    rank_str = rank_strs[user.firm_role]
    return promote_org.\
        replace("%NAME%", user.name).\
        replace("%RANK%", rank_str)

promote_org = """
Promosso con successo! **/u/%NAME%** ora è **%RANK%**.
"""

def modify_fire(user):
    return fire_org.\
        replace("%NAME%", user.name)

fire_org = """
Vattene via, barbone, ci hai fatto perdere un sacco di soldi!
**/u/%NAME%** licenziato dalla società.
"""

fire_failure_org = """
Non sono riuscito a cacciare l'utente, assicurati di aver scritto il nome correttamente, o che non abbia intestato a prestanomi il suo conto.
"""

joinfirm_exists_failure_org = """
Non puoi unirti ad una società perché sei già all'interno di un'altra.  
Utilizza il comando *!leavefirm* per lasciare la società prima di unirti ad una nuova.
"""

joinfirm_private_failure_org = """
Impossibile unirsi a questa società perché è privata e non sei stato invitato alla festa.

Il CEO o gli Executives devono prima invitarti col comando `!invite <username>`.
"""

joinfirm_failure_org = """
Non riesco a trovare la società che hai inserito. Che cazzo di truffa stai organizzando? Scrivi meglio il nome e riprova
"""

joinfirm_full_org = """
Non puoi unirti alla società poiché ha raggiunto il numero massimo di membri.
**Numero di impiegati:** %MEMBERS%
**Livello società:** %LEVEL%

Il CEO della società può aumentare il livello col comando `!upgrade`
"""

def modify_joinfirm_full(firm):
    return joinfirm_full_org.\
        replace("%MEMBERS%", str(firm.size)).\
        replace("%LEVEL%", str(firm.rank + 1))

joinfirm_org = """
Adesso sei un trader semplice della società **%NAME%**. Se vuoi uscire dalla società scrivi *!leavefirm*.
"""

def modify_joinfirm(firm):
    return joinfirm_org.\
        replace("%NAME%", firm.name)

FIRM_TAX_ORG = """

--

%AMOUNT% MemeCoins sono stati inviati alla società - %NAME%.
"""

def modify_firm_tax(tax_amount, firm_name):
    return FIRM_TAX_ORG.\
        replace("%AMOUNT%", str(tax_amount)).\
        replace("%NAME%", firm_name)

TEMPLATE_NOT_OP = """
Spiacente, ma non sei OP
"""

TEMPLATE_ALREADY_DONE = """
Spiacente, ma hai già inviato il link template.
"""

TEMPLATE_NOT_STICKY = """
Spiacente, ma devi rispondere *direttamente* al messaggio stickato del bot.
"""

TEMPLATE_OP = """
---

OP %NAME% ha postato *[IL LINK AL TEMPLATE](%LINK%)*, Evviva!
"""

def modify_template_op(link, name):
    return TEMPLATE_OP.\
        replace("%LINK%", link).\
        replace("%NAME%", name)
invite_not_private_failure_org = """
Non hai bisogno di invitare qualcuno poiché la tua società non è privata.

Gli investitori possono unirsi col comando `!joinfirm <firm_name>`.

Se sei il CEO e vuoi impostare la società come privata, usa il comando `!setprivate`.
"""

invite_no_user_failure_org = """
Impossibile invitare l'utente, assicurati di aver scritto il nome correttamente.
"""

invite_in_firm_failure_org = """
Questo utente fa già parte di un'altra società. Assicurati che esca prima di invitarlo nuovamente.
"""

invite_org = """
Hai invitato /u/%NAME% nella società.

Possono accettare questa richiesta usando il comando `!joinfirm %FIRM%`.
"""

def modify_invite(invitee, firm):
    return invite_org.\
        replace("%NAME%", invitee.name).\
        replace("%FIRM%", firm.name)

setprivate_org = """
La società è ora privata. I nuovi investitori potranno accedere solo se tu o uno degli Executives invia loro un invito col comando `!invite <user>`.

Se vuoi annullare tutto e tornare con una società pubblica, scrivi `!setpublic`.
"""

setpublic_org = """
La tua società è ora pubblica. I nuovi investitori potranno accedere senza essere invitati utilizzando il comando `!joinfirm <firm_name>`.

Se vuoi annullare tutto e tornare con una società privata, scrivi `!setprivate`.

"""
upgrade_insufficient_funds_org = """
La società non ha abbastanza fondi per aumentare il proprio livello.


**Saldo società:** %BALANCE%
**Costo per passare al livello %LEVEL%:** %COST%
"""

def modify_upgrade_insufficient_funds_org(firm, cost):
    return upgrade_insufficient_funds_org.\
        replace("%BALANCE%", str(firm.balance)).\
        replace("%LEVEL%", str(firm.rank + 2)).\
        replace("%COST%", str(cost))

upgrade_org = """
Hai migliorato con successo il livello della società:  **Livello %LEVEL%**!

La società adesso supporta un massimo di **%MAX_MEMBERS% impiegati**, incluso un massimo di **%MAX_EXECS% executives**.
"""

def modify_upgrade(firm, max_members, max_execs):
    return upgrade_org.\
        replace("%LEVEL%", str(firm.rank + 1)).\
        replace("%MAX_MEMBERS%", str(max_members)).\
        replace("%MAX_EXECS%", str(max_execs))
DEPLOY_VERSION = """
La versione corrente del bot è stata installata il `%DATE%`
"""

def modify_deploy_version(date):
    return DEPLOY_VERSION.\
        replace("%DATE%", date)

TAX_TOO_HIGH = """
La tassa è troppo alta. Dovrebbe essere tra il 5% e il 75%.
"""

TAX_TOO_LOW = """
La tassa è troppo bassa. Dovrebbe essere tra il 5% e il 75%.
"""

TAX_SUCCESS = """
La nuova tassa è stata impostata con successo
"""

TEMPLATE_SUCCESS = """
Template postato con successo! Grazie per aver reso /r/BancaDelMeme un posto migliore!
"""
