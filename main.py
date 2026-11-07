"""
Interfaccia web del Business Game.
Questo file sostituisce la vecchia interfaccia Kivy e integra la logica avanzata
delle schermate Guida, Mercato (con grafici interattivi Dark Premium) e dei Report
di Bilancio e Rendiconto di Cassa basati sui prospetti ufficiali della simulazione.

Avvio locale:
    python main.py

Deploy su Render:
    Build Command: pip install -r requirements.txt
    Start Command: gunicorn main:app
"""

import os
from flask import render_template_string
from server import app

PAGINA = r"""
<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Business Game</title>
<style>
:root {
  --bg:#f3f5f9; --panel:#fff; --ink:#172033; --muted:#667085;
  --primary:#2457d6; --primary-dark:#1743b2; --line:#e4e8f0;
  --good:#137a45; --bad:#b42318; --soft:#eef3ff;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,Segoe UI,Arial,sans-serif}
header{background:#14213d;color:white;padding:18px 22px;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
header h1{font-size:21px;margin:0}
header small{color:#cbd5e1}
main{max-width:1200px;margin:22px auto;padding:0 16px 40px}
.panel,.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 3px 12px #16213b0a}
.panel{max-width:760px;margin:24px auto}
h2{margin:0 0 15px;font-size:21px}
h3{margin:0 0 12px;font-size:16px}
h4{margin:10px 0 6px;font-size:14px;color:var(--ink)}
p{color:var(--muted);line-height:1.5;margin:0 0 10px}
label{display:block;font-size:13px;font-weight:650;margin:10px 0 5px}
input,select{width:100%;padding:10px 11px;border:1px solid #cfd6e2;border-radius:8px;background:white;color:var(--ink);font:inherit}
input:focus,select:focus{outline:2px solid #b8caff;border-color:var(--primary)}
button{border:0;border-radius:9px;padding:10px 15px;background:var(--primary);color:white;font-weight:650;cursor:pointer}
button:hover{background:var(--primary-dark)}
button.secondary{background:#e9eefb;color:#213b78}
button.danger{background:#a83232}
button:disabled{opacity:.5;cursor:not-allowed}
.actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:16px}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:16px 0}
.metric{background:#f7f9fc;border:1px solid var(--line);border-radius:10px;padding:13px}
.metric b{display:block;font-size:19px;margin-top:5px}
.muted{color:var(--muted);font-size:13px}
nav{display:flex;gap:7px;flex-wrap:wrap;margin:16px 0}
nav button{background:#e7ebf3;color:#344054}
nav button.active{background:var(--primary);color:white}
.view{display:none}.view.active{display:block}
.section{margin:14px 0;padding:16px;border:1px solid var(--line);border-radius:12px;background:white}
.section h3{margin-bottom:12px}
.field-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.product-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.product{background:#f8faff;border:1px solid var(--line);padding:13px;border-radius:10px}
.product h4{margin:0 0 8px}
.notice{padding:11px 13px;border-radius:9px;background:var(--soft);color:#25417f;margin:12px 0}
.message{margin-top:12px;font-weight:600}
.message.error{color:var(--bad)}.message.success{color:var(--good)}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{padding:9px;border-bottom:1px solid var(--line);text-align:left}
th{background:#f6f8fb}
.table-wrap{overflow:auto}
pre{white-space:pre-wrap;word-break:break-word;font:14px/1.55 inherit;margin:0}
canvas{width:100%;height:230px;border:1px solid #334155;border-radius:12px;background:#0f172a;cursor:crosshair;box-shadow:0 4px 15px rgba(0,0,0,0.15)}
.hidden{display:none!important}
.badge{display:inline-block;border-radius:20px;padding:5px 9px;background:#edf2ff;color:#2446a0;font-size:12px;font-weight:700}
.guide-text{font-size:14px;line-height:1.6;color:var(--ink);white-space:pre-wrap}
.admin-bar-box{background:#f8fafc;border:1px solid var(--line);border-radius:10px;padding:12px;margin-bottom:14px;font-size:13px;line-height:1.6}
@media(max-width:760px){.grid,.grid3,.cards,.product-grid,.field-grid{grid-template-columns:1fr}header{padding:15px}main{margin-top:12px}.panel{margin:12px auto;padding:15px}}
</style>
</head>
<body>
<header>
  <div><h1>Business Game</h1><small>Simulazione competitiva tra aziende</small></div>
  <div id="header-user" class="muted"></div>
</header>
<main>
  <section id="access-view" class="panel">
    <h2>Benvenuto</h2>
    <p>Scegli se creare una stanza come amministratore oppure entrare in una partita esistente come azienda.</p>
    <div class="grid">
      <div class="card">
        <h3>Amministratore</h3>
        <label for="admin-password">Password admin</label>
        <input id="admin-password" type="password" autocomplete="current-password" placeholder="Password">
        <div class="actions"><button onclick="creaStanza()">Crea stanza</button></div>
      </div>
      <div class="card">
        <h3>Giocatore</h3>
        <label for="join-company">Nome azienda</label>
        <input id="join-company" placeholder="Es. Alfa S.p.A.">
        <label for="join-code">Codice stanza</label>
        <input id="join-code" placeholder="Codice comunicato dall'admin" maxlength="6">
        <div class="actions"><button onclick="entraStanza()">Entra nella partita</button></div>
      </div>
    </div>
    <div id="access-message" class="message"></div>
  </section>

  <section id="admin-view" class="hidden">
    <div class="panel" style="max-width:none">
      <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap">
        <div><h2>Area amministratore</h2><span class="badge">Stanza <span id="admin-room-code">---</span></span></div>
        <button class="secondary" onclick="tornaAccesso()">Esci</button>
      </div>
      <p>Imposta i parametri iniziali e salva. I giocatori potranno entrare nella stanza dopo il salvataggio.</p>
      <form id="settings-form">
        <div class="section"><h3>Parametri iniziali delle aziende</h3><div class="field-grid">
          <div><label>Capitale iniziale</label><input name="initial_capital" type="number" step="any" value="100000"></div>
          <div><label>Magazzino materie prime iniziale</label><input name="initial_raw_material_inventory" type="number" step="any" value="500"></div>
          <div><label>Capacità iniziale</label><input name="initial_capacity" type="number" step="any" value="100"></div>
          <div><label>Personale iniziale</label><input name="initial_personnel" type="number" step="1" value="5"></div>
        </div></div>
        <div class="section"><h3>Dimensione dei mercati</h3><div class="field-grid">
          <div><label>Mercato iniziale A</label><input name="market_initial_a" type="number" step="any" value="150"></div>
          <div><label>Mercato finale A</label><input name="market_final_a" type="number" step="any" value="300"></div>
          <div><label>Mercato iniziale B</label><input name="market_initial_b" type="number" step="any" value="150"></div>
          <div><label>Mercato finale B</label><input name="market_final_b" type="number" step="any" value="400"></div>
        </div></div>
        <div class="section"><h3>Pesi delle variabili di mercato (la somma deve essere 100%)</h3>
          <h4>Mercato A</h4><div class="field-grid">
            <div><label>Prezzo A (%)</label><input name="a_price" type="number" value="50"></div>
            <div><label>Visibilità A (%)</label><input name="a_visibility" type="number" value="20"></div>
            <div><label>Ricerca A (%)</label><input name="a_research" type="number" value="30"></div>
          </div>
          <h4>Mercato B</h4><div class="field-grid">
            <div><label>Prezzo B (%)</label><input name="b_price" type="number" value="50"></div>
            <div><label>Visibilità B (%)</label><input name="b_visibility" type="number" value="30"></div>
            <div><label>Ricerca B (%)</label><input name="b_research" type="number" value="20"></div>
          </div>
        </div>
        <div class="section"><h3>Parametri economici e produttivi</h3><div class="field-grid">
          <div><label>Interessi (%)</label><input name="interests" type="number" step="any" value="6"></div>
          <div><label>Costo acquisto materie prime</label><input name="purchase_cost" type="number" step="any" value="10"></div>
          <div><label>Produzione oraria Prodotto A</label><input name="production_time_a" type="number" value="1"></div>
          <div><label>Produzione oraria Prodotto B</label><input name="production_time_b" type="number" value="2"></div>
          <div><label>Rapporto investimento/visibilità A</label><input name="investment_visibility_ratio_a" type="number" step="any" value="10"></div>
          <div><label>Rapporto investimento/visibilità B</label><input name="investment_visibility_ratio_b" type="number" step="any" value="20"></div>
          <div><label>Ricerca interna/ricerca A</label><input name="innovation_internal_research_ratio_a" type="number" step="any" value="10"></div>
          <div><label>Co-progettazione/ricerca A</label><input name="innovation_coproj_research_ratio_a" type="number" step="any" value="20"></div>
          <div><label>Ricerca interna/ricerca B</label><input name="innovation_internal_research_ratio_b" type="number" step="any" value="20"></div>
          <div><label>Co-progettazione/ricerca B</label><input name="innovation_coproj_research_ratio_b" type="number" step="any" value="30"></div>
          <div><label>Rapporto investimento/capacità</label><input name="investment_capacity_ratio" type="number" step="any" value="10"></div>
        </div></div>
        <div class="actions"><button type="submit">Salva parametri stanza</button><button type="button" class="secondary" onclick="aggiornaAdmin()">Aggiorna giocatori</button></div>
      </form>
      <div id="admin-message" class="message"></div>
      <div class="section"><h3>Giocatori nella stanza</h3><div id="players-list" class="muted">Nessun giocatore.</div></div>
      <div class="section"><h3>Condivisione</h3><p>Comunica ai partecipanti questo codice:</p><h2 id="share-code">---</h2></div>
    </div>
  </section>

  <section id="game-view" class="hidden">
    <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap">
      <div><h2 id="game-title">Azienda</h2><div class="muted">Stanza: <b id="game-room"></b> · Turno: <b id="game-turn"></b></div></div>
      <button class="secondary" onclick="tornaAccesso()">Esci</button>
    </div>
    <nav>
      <button class="active" data-tab="home" onclick="mostraTab('home')">Home</button>
      <button data-tab="leve" onclick="mostraTab('leve')">Leve</button>
      <button data-tab="mercato" onclick="mostraTab('mercato')">Mercato</button>
      <button data-tab="report" onclick="mostraTab('report')">Report</button>
      <button data-tab="guida" onclick="mostraTab('guida')">Guida</button>
    </nav>

    <div id="tab-home" class="view active">
      <div class="cards" id="company-metrics"></div>
      <div class="grid">
        <div class="card"><h3>Prodotto A</h3><div id="product-a"></div></div>
        <div class="card"><h3>Prodotto B</h3><div id="product-b"></div></div>
      </div>
      <div class="section"><h3>Classifica</h3><div id="ranking"></div></div>
    </div>

    <div id="tab-leve" class="view">
      <div class="notice">Inserisci le decisioni del turno e premi “Conferma scelte”. Una volta confermate, le scelte non possono essere modificate.</div>
      <form id="decisions-form">
        <div class="section"><h3>Marketing</h3><div class="product-grid">
          <div class="product"><h4>Prodotto A</h4><label>Promozione</label><input name="Marketing_Prodotto A_Promozione" type="number" min="0" step="any" value="0"><label>Prezzo</label><input name="Marketing_Prodotto A_Prezzo" type="number" min="0" step="any" value="0"></div>
          <div class="product"><h4>Prodotto B</h4><label>Promozione</label><input name="Marketing_Prodotto B_Promozione" type="number" min="0" step="any" value="0"><label>Prezzo</label><input name="Marketing_Prodotto B_Prezzo" type="number" min="0" step="any" value="0"></div>
        </div></div>
        <div class="section"><h3>Produzione</h3><div class="field-grid">
          <div><label>Investimento capacità</label><input name="Produzione_Investimento capacità" type="number" min="0" step="any" value="0"></div>
          <div><label>Quantità prodotto A</label><input name="Produzione_Quantità prodotto A" type="number" min="0" step="1" value="0"></div>
          <div><label>Quantità prodotto B</label><input name="Produzione_Quantità prodotto B" type="number" min="0" step="1" value="0"></div>
        </div></div>
        <div class="section"><h3>Finanza</h3><label>Richiesta di finanziamento</label><input name="Finanza_Richiesta di finanziamento" type="number" min="0" step="any" value="0"></div>
        <div class="section"><h3>Approvvigionamento</h3><label>Quantità materie prime da acquistare</label><input name="Approvvigionamento_Quantità" type="number" min="0" step="any" value="0"></div>
        <div class="section"><h3>Risorse umane</h3><div class="field-grid">
          <div><label>Personale attuale (modifica con i pulsanti)</label><div class="actions"><button type="button" class="secondary" onclick="modificaPersonale(1)">Assumi</button><button type="button" class="secondary" onclick="modificaPersonale(-1)">Licenzia</button></div><b id="personnel-value">0</b></div>
          <div><label>Straordinari</label><input name="Risorse umane_Straordinari" type="number" min="0" step="any" value="0"></div>
        </div></div>
        <div class="section"><h3>Ricerca e sviluppo</h3><div class="product-grid">
          <div class="product"><h4>Prodotto A</h4><label>Investimento ricerca prodotto</label><input name="Ricerca e sviluppo_Prodotto A_Ricerca prodotto" type="number" min="0" step="any" value="0"><label>Modalità</label><select name="Ricerca e sviluppo_Prodotto A_Ricerca prodotto_modalita"><option>Interna</option><option>Co-progettazione</option></select></div>
          <div class="product"><h4>Prodotto B</h4><label>Investimento ricerca prodotto</label><input name="Ricerca e sviluppo_Prodotto B_Ricerca prodotto" type="number" min="0" step="any" value="0"><label>Modalità</label><select name="Ricerca e sviluppo_Prodotto B_Ricerca prodotto_modalita"><option>Interna</option><option>Co-progettazione</option></select></div>
        </div></div>
        <div class="actions"><button id="submit-decisions" type="submit">Conferma scelte</button></div>
      </form>
      <div id="game-message" class="message"></div>
    </div>

    <div id="tab-mercato" class="view">
      <div class="section">
        <h3 style="text-align:center;margin-bottom:6px">STIMA DOMANDA TURNO <span id="market-current-turn">1</span></h3>
        <p style="text-align:center;font-size:16px;font-weight:bold;color:var(--primary)" id="market-estimate-label">Mercato A: - | Mercato B: -</p>
      </div>

      <div class="section">
        <h3>Andamento della Domanda di Mercato</h3>
        <div class="grid">
          <div><h4>Domanda mercato A</h4><canvas id="chart-demand-a" width="550" height="230"></canvas></div>
          <div><h4>Domanda mercato B</h4><canvas id="chart-demand-b" width="550" height="230"></canvas></div>
        </div>
      </div>

      <div class="section">
        <h3>Medie di Mercato - Prodotto A</h3>
        <div class="grid3">
          <div><h4>Prezzo medio A</h4><canvas id="chart-price-a" width="360" height="200"></canvas></div>
          <div><h4>Visibilità media A</h4><canvas id="chart-visibility-a" width="360" height="200"></canvas></div>
          <div><h4>Ricerca media A</h4><canvas id="chart-research-a" width="360" height="200"></canvas></div>
        </div>
      </div>

      <div class="section">
        <h3>Medie di Mercato - Prodotto B</h3>
        <div class="grid3">
          <div><h4>Prezzo medio B</h4><canvas id="chart-price-b" width="360" height="200"></canvas></div>
          <div><h4>Visibilità media B</h4><canvas id="chart-visibility-b" width="360" height="200"></canvas></div>
          <div><h4>Ricerca media B</h4><canvas id="chart-research-b" width="360" height="200"></canvas></div>
        </div>
      </div>
    </div>

    <div id="tab-report" class="view">
      <div class="section"><h3>Seleziona situazione</h3><select id="report-turn" onchange="aggiornaReport()"><option value="current">Situazione attuale</option></select></div>
      <div class="grid">
        <div class="section"><h3>Stato patrimoniale - Attivo</h3><div id="report-assets"></div></div>
        <div class="section"><h3>Stato patrimoniale - Passivo e Patrimonio Netto</h3><div id="report-liabilities"></div></div>
      </div>
      <div class="section"><h3>Conto economico</h3><div id="report-income"></div></div>
      <div class="section"><h3>Flussi di cassa (Rendiconto di Cassa)</h3><div id="report-cashflow"></div></div>
      <div class="section"><h3>Indici</h3><div id="report-ratios"></div></div>
    </div>

    <div id="tab-guida" class="view">
      <div class="admin-bar-box">
        <div id="guide-admin-row1"><b>Mercato A:</b> Prezzo: -% | Visibilità: -% | Ricerca: -% &nbsp;&nbsp; <b>Mercato B:</b> Prezzo: -% | Visibilità: -% | Ricerca: -%</div>
        <div id="guide-admin-row2"><b>Interessi:</b> -% &nbsp;|&nbsp; <b>Costo acquisto:</b> - &nbsp;|&nbsp; <b>Rapporto inv./capacità:</b> -</div>
        <div id="guide-admin-row3"><b>Rapporti A:</b> Visibilità: - | Ricerca interna: - | Co-progettazione: - &nbsp;&nbsp; <b>Rapporti B:</b> Visibilità: - | Ricerca interna: - | Co-progettazione: -</div>
      </div>

      <div class="section">
        <h3>Guida Completa al Business Game</h3>
        <div class="guide-text">SPIEGAZIONE DEI PARAMETRI ADMIN

PERCENTUALI DI MERCATO
Le percentuali di mercato indicano quanto incidono prezzo, visibilità e ricerca nella competizione tra aziende.

Prezzo:
Indica quanto il prezzo pesa nella scelta del mercato. Nel calcolo del mercato un prezzo più alto riduce la competitività del prodotto.

Visibilità:
Indica quanto la promozione influenza la capacità dell'azienda di vendere. Più il prodotto è visibile, più aumenta la sua forza competitiva.

Ricerca:
Indica quanto l'investimento in ricerca influenza la qualità competitiva del prodotto sul mercato.

INTERESSI
Il valore degli interessi indica il costo del finanziamento richiesto. Quando un'azienda chiede un finanziamento, nei turni successivi pagherà una quota del debito e gli interessi calcolati su quel finanziamento.

COSTO DI ACQUISTO
Il costo di acquisto rappresenta il costo unitario delle materie prime. Viene usato per calcolare il valore del magazzino materie prime, il costo degli acquisti e parte del valore dei prodotti finiti.

RAPPORTO INVESTIMENTO/CAPACITÀ
Questo rapporto indica quanto investimento serve per aumentare la capacità produttiva dell'azienda. Più il rapporto è alto, più è costoso aumentare la capacità.

RAPPORTO INVESTIMENTO/VISIBILITÀ
Questo rapporto indica quanto investimento in promozione serve per aumentare la visibilità del prodotto. È separato per Prodotto A e Prodotto B.

RAPPORTO RICERCA INTERNA
Indica quanto investimento in ricerca interna serve per aumentare il livello di ricerca del prodotto. Anche questo parametro è distinto tra Prodotto A e Prodotto B.

RAPPORTO CO-PROGETTAZIONE
Indica quanto investimento in co-progettazione serve per aumentare il livello di ricerca del prodotto. Può essere diverso dalla ricerca interna e permette di simulare una modalità alternativa di innovazione.


LEVE DI MARKETING

Le leve di marketing determinano la competitività commerciale dei prodotti.

Prezzo:
Il prezzo rappresenta il valore di vendita del prodotto. Un prezzo alto aumenta il ricavo unitario, ma può ridurre la competitività del prodotto sul mercato. Un prezzo basso può aiutare a vendere di più, ma riduce il margine su ogni unità venduta.

Promozione:
La promozione rappresenta l'investimento usato per aumentare la visibilità del prodotto. Maggiore è la promozione, maggiore sarà l'aumento della visibilità, secondo il rapporto investimento/visibilità impostato dall'admin. La promozione aumenta gli investimenti nello Stato Patrimoniale e viene ammortizzata nei turni successivi.


LEVE DI PRODUZIONE

Le leve di produzione permettono di decidere quante unità produrre e quanto aumentare la capacità produttiva dell'azienda.

Investimento capacità:
Serve ad aumentare la capacità produttiva. L'aumento ottenuto dipende dal rapporto investimento/capacità impostato dall'admin. Anche questo valore aumenta gli investimenti nello Stato Patrimoniale e viene ammortizzato nei turni successivi.

Quantità prodotto A:
Indica quante unità del Prodotto A vengono prodotte nel turno corrente. Questa quantità aumenta il magazzino prodotti disponibili prima del calcolo del mercato.

Quantità prodotto B:
Indica quante unità del Prodotto B vengono prodotte nel turno corrente. Come per il prodotto A, questa quantità aumenta il magazzino prodotti disponibili prima del calcolo del mercato.

La produzione consuma materie prime e deve rispettare i vincoli di capacità produttiva e ore di lavoro disponibili. Se produci troppo poco, potresti non riuscire a soddisfare la domanda; se produci troppo, aumenterà il magazzino prodotti finiti.


LEVE DI FINANZA

Le leve di finanza consentono all'azienda di reperire le risorse economiche necessarie per sostenere gli investimenti e la gestione aziendale.

Richiesta di finanziamento:
Permette di richiedere un prestito bancario. L'importo richiesto viene immediatamente aggiunto alla liquidità (cassa) dell'azienda e aumenta i debiti verso banche nello Stato Patrimoniale.

A partire dai turni successivi il finanziamento viene rimborsato gradualmente secondo il piano di ammortamento del gioco. Ad ogni rimborso vengono pagati sia una quota del capitale ricevuto sia gli interessi calcolati utilizzando il tasso impostato dall'amministratore. I pagamenti riducono la liquidità dell'azienda e vengono registrati nei Flussi di Cassa e nel Conto Economico.

Una richiesta di finanziamento elevata aumenta le risorse disponibili nel breve periodo, ma comporta maggiori costi finanziari nei turni successivi.


LEVE DI APPROVVIGIONAMENTO

Le leve di approvvigionamento permettono di decidere come acquistare le materie prime necessarie alla produzione.

Quantità:
Rappresenta il numero di materie prime acquistate presso ciascun fornitore. La somma delle quantità acquistate determina il totale delle materie prime che entreranno nel magazzino dell'azienda.

Le materie prime acquistate aumentano il valore del Magazzino Materie Prime nello Stato Patrimoniale e saranno utilizzate per la produzione dei prodotti A e B nei turni successivi. Un acquisto insufficiente può limitare la produzione, mentre un acquisto eccessivo aumenta il capitale immobilizzato nel magazzino.


LEVE DI RISORSE UMANE

Le leve di Risorse Umane consentono di gestire il personale e l'organizzazione del lavoro dell'azienda. Una corretta gestione delle risorse umane permette di sfruttare al meglio la capacità produttiva e di adattare l'azienda alle esigenze del mercato.

Personale:
Attraverso i pulsanti 'Assumi' e 'Licenzia' è possibile aumentare o ridurre il numero di dipendenti dell'azienda. Un numero maggiore di dipendenti può consentire una migliore organizzazione della produzione, ma comporta un aumento del costo del personale che verrà registrato nel Conto Economico e nei Flussi di Cassa.

Straordinari:
Consentono di aumentare le ore a disposizione senza assumere personale, ma ad un costo orario maggiore.


LEVE DI RICERCA E SVILUPPO

Le leve di Ricerca e Sviluppo consentono di migliorare il livello di innovazione dei prodotti A e B, aumentando la loro competitività sul mercato.

Modalità di ricerca:
Per ciascun prodotto è possibile scegliere tra Ricerca Interna e Co-progettazione. Le due modalità utilizzano rapporti di conversione diversi definiti dall'amministratore del gioco.

Ricerca Interna:
L'azienda sviluppa autonomamente il prodotto. L'efficacia dell'investimento dipende dal rapporto 'Ricerca interna' impostato dall'amministratore. Il valore del rapporto verrà poi aggiunto a ricerca del prodotto al turno t+2 dove t è il turnoattuale.

Co-progettazione:
L'azienda sviluppa il prodotto insieme a partner esterni. Anche in questo caso l'incremento del livello di ricerca dipende dal rapporto 'Co-progettazione' definito dall'amministratore.

Investimento in ricerca:
L'importo inserito rappresenta l'investimento destinato allo sviluppo del prodotto. Maggiore è l'investimento, maggiore sarà l'aumento del livello di ricerca del prodotto in funzione del rapporto scelto.

Gli investimenti in Ricerca e Sviluppo vengono registrati nello Stato Patrimoniale come investimenti pluriennali e vengono ammortizzati nei turni successivi. Un livello di ricerca più elevato aumenta la competitività del prodotto quando il mercato attribuisce importanza alla variabile Ricerca.


COME USARE QUESTI PARAMETRI
Il giocatore dovrebbe leggere questi valori prima di compilare le leve. Se, ad esempio, la visibilità pesa molto nel mercato e il rapporto investimento/visibilità è basso, investire in promozione può essere una scelta conveniente. Se invece il prezzo pesa molto, sarà importante controllare attentamente il prezzo di vendita.


STATO PATRIMONIALE

Lo Stato Patrimoniale rappresenta la situazione economica e finanziaria dell'azienda alla fine di ogni turno. È suddiviso in Attivo e Passivo e mostra come sono impiegate le risorse dell'azienda e come sono state finanziate.

ATTIVO FISSO
Investimenti: Questa voce rappresenta il valore degli investimenti pluriennali ancora non ammortizzati. Comprende gli investimenti effettuati in promozione, capacità produttiva e ricerca e sviluppo. Ad ogni turno una quota degli investimenti viene trasferita negli investimenti correnti e registrata come ammortamento nel Conto Economico.

ATTIVO CORRENTE
Cassa: La cassa rappresenta la liquidità disponibile dell'azienda. Aumenta grazie agli incassi delle vendite e ai finanziamenti ottenuti, mentre diminuisce per effetto degli acquisti, degli investimenti, del pagamento dei debiti, degli interessi e di tutte le altre uscite monetarie.
Magazzino materie prime: Rappresenta il valore economico delle materie prime disponibili. Aumenta con gli acquisti effettuati dai fornitori e diminuisce quando le materie prime vengono utilizzate nella produzione dei prodotti.
Magazzino prodotti finiti: Indica il valore economico dei prodotti già realizzati ma non ancora venduti. Aumenta quando la produzione supera le vendite e diminuisce quando i prodotti vengono acquistati dal mercato.
Investimenti correnti: Contengono la quota degli investimenti pluriennali che sta per essere ammortizzata.

TOTALE ATTIVO: Il totale dell'attivo è dato dalla somma di tutte le attività presenti nello Stato Patrimoniale.

PASSIVO E PATRIMONIO NETTO
Capitale sociale: Rappresenta il patrimonio netto dell'azienda. Nel turno iniziale è pari al capitale iniziale deciso dall'amministratore più il valore iniziale del magazzino materie prime più l'utile accumulato.
Debiti verso banche: Rappresentano la parte a medio-lungo termine dei finanziamenti ottenuti.
Debiti correnti: Rappresentano la quota di finanziamenti che dovrà essere rimborsata nel breve periodo.


CONTO ECONOMICO

Il Conto Economico rappresenta il risultato della gestione aziendale durante un turno di gioco.
VALORE DELLA PRODUZIONE: Ricavi di vendita (Prodotti A e B venduti x prezzi) e Variazione prodotti finiti (Valore magazzino PF finale - iniziale).
COSTI ESTERNI: Acquisto materie prime (Quantità acquistata x costo unitario) e Variazione materie prime (Valore magazzino MP iniziale - finale).
VALORE AGGIUNTO: Valore della Produzione - Costi Esterni.
COSTO DEL PERSONALE: Dipendenti x costo unitario + straordinari x costo orario.
MARGINE OPERATIVO LORDO (MOL / EBITDA): Valore Aggiunto - Costo del personale.
MARGINE OPERATIVO NETTO (MON / EBIT): MOL - Ammortamenti (Quota d'esercizio degli investimenti pluriennali).
UTILE D'ESERCIZIO: MON - Interessi (Costi finanziari sui finanziamenti bancari).


FLUSSO DI CASSA (RENDICONTO DI CASSA)

FLUSSO DI CASSA OPERATIVO
Entrate da clienti: Incassi derivanti dalla vendita dei prodotti A e B.
Uscite per fornitori: Uscite per acquisto materie prime.
Uscite per personale: Uscite per retribuzioni e straordinari dipendenti.
Interessi: Pagamento interessi relativi ai finanziamenti.

FLUSSO DI CASSA DA INVESTIMENTI
Promozione: Uscita per investimento in visibilità prodotti.
Capacità produttiva: Uscita per investimento in aumento capacità.
Ricerca e sviluppo: Uscita per investimento in sviluppo prodotti A e B.

FLUSSO DI CASSA DA FINANZIAMENTO
Acquisizione debiti: Entrate da nuovi finanziamenti bancari ottenuti.
Pagamento debiti: Rimborso quota capitale finanziamenti precedenti.

CASSA FINALE: Cassa Iniziale + Totale Entrate - Totale Uscite.


INDICI ECONOMICO-FINANZIARI

ROE (Return On Equity): Utile / Capitale Sociale. Misura la redditività del capitale investito dai soci.
ROI (Return On Investment): Margine Operativo Netto / Totale Attivo. Misura l'efficienza degli investimenti.
ROD (Costo dell'indebitamento): Interessi / Debiti Totali.
Indice Q: Debiti Totali / Capitale Sociale. Grado di indebitamento.
Indice S: Utile / Margine Operativo Netto. Incidenza della gestione finanziaria.
Leva Finanziaria: ROI - ROD.


CLASSIFICA DEI GIOCATORI

La classifica viene aggiornata al termine di ogni turno in base al punteggio:
Punteggio = 0.7 × Quota di Mercato + 0.3 × ROE

Quota di Mercato = ((Venduto A / Domanda A) + (Venduto B / Domanda B)) / 2</div>
      </div>
    </div>
  </section>
</main>

<script>
const API = "";
let stato = {room_code:"", company_name:"", admin_password:"", player:null, room:null, personnel:0};
const $ = id => document.getElementById(id);
const canvasState = {};

async function api(url, method="GET", body=null) {
  const opt={method,headers:{"Content-Type":"application/json"}};
  if(body!==null) opt.body=JSON.stringify(body);
  const res=await fetch(API+url,opt);
  let data={}; try{data=await res.json()}catch(e){}
  if(!res.ok || data.success===false) throw new Error(data.message || `Errore HTTP ${res.status}`);
  return data;
}

function msg(id,text,error=false){const el=$(id);el.textContent=text;el.className="message "+(error?"error":"success");}
function show(id){["access-view","admin-view","game-view"].forEach(x=>$(x).classList.add("hidden"));$(id).classList.remove("hidden");}
function salvaSessione(){sessionStorage.setItem("business-game-session",JSON.stringify(stato));}
function caricaSessione(){try{const x=JSON.parse(sessionStorage.getItem("business-game-session")||"null");if(x)stato=x;}catch(e){}}
function tornaAccesso(){sessionStorage.removeItem("business-game-session");stato={room_code:"",company_name:"",admin_password:"",player:null,room:null,personnel:0};show("access-view");$("header-user").textContent="";}

async function creaStanza(){
  try{
    const password=$("admin-password").value.trim(); if(!password) throw new Error("Inserisci la password admin.");
    const d=await api("/create_room","POST",{password});
    stato={room_code:d.room_code,admin_password:password,company_name:"",player:null,room:null,personnel:0};
    salvaSessione(); $("admin-room-code").textContent=d.room_code; $("share-code").textContent=d.room_code;
    show("admin-view"); $("header-user").textContent="Amministratore · "+d.room_code;
    msg("admin-message","Stanza creata. Imposta e salva i parametri.");
  }catch(e){msg("access-message",e.message,true);}
}

function formObject(form){return Object.fromEntries(new FormData(form).entries());}

async function salvaImpostazioni(ev){
  ev.preventDefault();
  try{
    const f=formObject($("settings-form"));
    const n=k=>Number(f[k]||0);
    const payload={
      initial_capital:n("initial_capital"),initial_raw_material_inventory:n("initial_raw_material_inventory"),
      initial_capacity:n("initial_capacity"),initial_personnel:n("initial_personnel"),
      market_initial_a:f.market_initial_a,market_initial_b:f.market_initial_b,market_final_a:f.market_final_a,market_final_b:f.market_final_b,
      market_variable_percentages_a:[n("a_price"),n("a_visibility"),n("a_research")],
      market_variable_percentages_b:[n("b_price"),n("b_visibility"),n("b_research")],
      interests:n("interests"),purchase_cost:n("purchase_cost"),production_time_a:n("production_time_a"),production_time_b:n("production_time_b"),
      investment_visibility_ratio_a:n("investment_visibility_ratio_a"),investment_visibility_ratio_b:n("investment_visibility_ratio_b"),
      innovation_internal_research_ratio_a:n("innovation_internal_research_ratio_a"),innovation_coproj_research_ratio_a:n("innovation_coproj_research_ratio_a"),
      innovation_internal_research_ratio_b:n("innovation_internal_research_ratio_b"),innovation_coproj_research_ratio_b:n("innovation_coproj_research_ratio_b"),
      investment_capacity_ratio:n("investment_capacity_ratio"),room_code:stato.room_code,password:stato.admin_password
    };
    const d=await api("/update_room_settings","POST",payload);
    msg("admin-message",d.message); await aggiornaAdmin();
  }catch(e){msg("admin-message",e.message,true);}
}

async function aggiornaAdmin(){
  try{
    const d=await api("/room/"+encodeURIComponent(stato.room_code));
    stato.room=d.room; salvaSessione();
    const players=d.room.players||[];
    $("players-list").innerHTML=players.length?players.map(p=>`<div class="metric"><b>${esc(p.company_name)}</b><div class="muted">Turno ${p.current_turn} · ${p.choices_confirmed?"Scelte confermate":"In attesa"}</div></div>`).join(""):"Nessun giocatore è ancora entrato.";
  }catch(e){msg("admin-message",e.message,true);}
}

async function entraStanza(){
  try{
    const company_name=$("join-company").value.trim(),room_code=$("join-code").value.trim().toUpperCase();
    if(!company_name||!room_code)throw new Error("Inserisci nome azienda e codice stanza.");
    const d=await api("/join_room","POST",{company_name,room_code});
    stato={room_code,company_name,player:d.player,room:null,personnel:Number(d.player.company?.personnel||0)};
    await aggiornaStato();
    salvaSessione();show("game-view");$("header-user").textContent=company_name+" · "+room_code;
    $("game-title").textContent=company_name;$("game-room").textContent=room_code;
    mostraTab("home");renderGioco();
  }catch(e){msg("access-message",e.message,true);}
}

async function aggiornaStato(){
  const d=await api("/room/"+encodeURIComponent(stato.room_code));
  stato.room=d.room;
  const p=(d.room.players||[]).find(x=>x.company_name.toLowerCase()===stato.company_name.toLowerCase());
  if(p)stato.player=p;
  if(stato.player)stato.personnel=Number(stato.player.company?.personnel||stato.personnel||0);
  salvaSessione();
}

function esc(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function fmt(v){const x=Number(v||0);return Number.isFinite(x)?x.toLocaleString("it-IT",{maximumFractionDigits:2}):"0";}
function metric(label,value){return `<div class="metric"><span class="muted">${esc(label)}</span><b>${esc(fmt(value))}</b></div>`;}
function renderProdotto(p,sale){return `<p>Prezzo: <b>${fmt(p.price)}</b></p><p>Visibilità: ${fmt(p.visibility)}</p><p>Ricerca: ${fmt(p.research)}</p><p>Quantità in magazzino: ${fmt(p.quantity)}</p><p>Produzione oraria: ${fmt(p.production_per_hour)}</p><p>Venduto nell'ultimo turno: ${fmt(sale)}</p>`;}

function renderGioco(){
  const p=stato.player||{},c=p.company||{},pr=p.products||{},sales=p.sales||{A:0,B:0};
  $("game-turn").textContent=`${p.current_turn||1}/${(stato.room?.max_turns||8)}`;
  $("company-metrics").innerHTML=metric("Capitale",c.capital)+metric("Magazzino materie prime",c.raw_material_inventory)+metric("Capacità",c.capacity)+metric("Personale",c.personnel)+metric("Investimenti",c.fixed_investments)+metric("Stato partita",p.game_finished?"Terminata":p.choices_confirmed?"Scelte confermate":"In corso");
  $("product-a").innerHTML=renderProdotto(pr.A||{},sales.A);$("product-b").innerHTML=renderProdotto(pr.B||{},sales.B);
  $("personnel-value").textContent=stato.personnel;
  const ranking=stato.room?.current_ranking||[];
  $("ranking").innerHTML=ranking.length?`<div class="table-wrap"><table><tr><th>Pos.</th><th>Azienda</th><th>Punteggio</th><th>Quota mercato</th><th>ROE</th></tr>${ranking.map(x=>`<tr><td>${esc(x.posizione)}</td><td>${esc(x.azienda)}</td><td>${fmt(x.punteggio)}</td><td>${fmt(x.quota_mercato)}</td><td>${fmt(x.roe)}</td></tr>`).join("")}</table></div>`:"La classifica sarà disponibile dopo l'elaborazione del mercato.";
  const disabled=p.choices_confirmed||p.game_finished||(p.current_turn||1)>(stato.room?.max_turns||8);
  $("submit-decisions").disabled=disabled;
  $("decisions-form").querySelectorAll("input,select,button").forEach(el=>{if(el.type!=="button")el.disabled=disabled;});
  aggiornaMercato();aggiornaReport();aggiornaGuida();
}

function modificaPersonale(delta){stato.personnel=Math.max(0,Number(stato.personnel||0)+delta);$("personnel-value").textContent=stato.personnel;}

async function inviaDecisioni(ev){
  ev.preventDefault();
  try{
    const p=stato.player||{};
    const decisions=formObject($("decisions-form"));
    decisions["Risorse umane_Personale attuale"]=String(stato.personnel);
    const d=await api("/submit_choices","POST",{room_code:stato.room_code,company_name:stato.company_name,decisions});
    if(d.company)stato.player.company=d.company;
    if(d.products)stato.player.products=d.products;
    if(d.costs)stato.player.costs=d.costs;
    if(d.sales)stato.player.sales=d.sales;
    if(d.history)stato.player.history=d.history;
    stato.player.current_turn=d.current_turn??stato.player.current_turn;
    stato.player.choices_confirmed=d.choices_confirmed??true;
    stato.player.game_finished=d.game_finished??false;
    msg("game-message",d.message);
    await aggiornaStato();renderGioco();mostraTab("home");
  }catch(e){msg("game-message",e.message,true);}
}

function mostraTab(tab){
  document.querySelectorAll(".view").forEach(x=>x.classList.remove("active"));
  document.querySelectorAll("nav button").forEach(x=>x.classList.toggle("active",x.dataset.tab===tab));
  $("tab-"+tab).classList.add("active");
  if(tab==="report")aggiornaReport();
  if(tab==="mercato")aggiornaMercato();
  if(tab==="guida")aggiornaGuida();
}

function tabella(obj,labels){
  const rows=Object.entries(labels).map(([k,l])=>`<tr><td>${esc(l)}</td><td>${fmt(obj?.[k])}</td></tr>`).join("");
  return `<div class="table-wrap"><table>${rows}</table></div>`;
}

// =================================================================
// REPORT (Aggiornato secondo il file PDF Prospetti di Bilancio)
// =================================================================
function aggiornaReport(){
  const p=stato.player||{},history=p.history||{},sel=$("report-turn").value||"current";
  let company=p.company||{},turn=p.current_turn||1;
  if(sel!=="current"&&history[sel]){company=history[sel].azienda||{report:history[sel].report};turn=Number(sel);}
  const r=company.report||{},bs=r.balance_sheet||{},inc=r.income_statement||{},cf=r.cash_flow||{};
  const turns=Object.keys(history).sort((a,b)=>Number(a)-Number(b));
  const select=$("report-turn"),old=select.value;
  const opts=['<option value="current">Situazione attuale</option>',...turns.map(t=>`<option value="${esc(t)}">Turno ${esc(t)}</option>`)];
  if(select.options.length!==opts.length)select.innerHTML=opts.join("");
  if([...select.options].some(o=>o.value===old))select.value=old;

  // STATO PATRIMONIALE - ATTIVO
  $("report-assets").innerHTML=tabella(bs,{
    fixed_investments: "ATTIVO FISSO: Investimenti (promozione, capacità, R&S)",
    cash: "ATTIVO CORRENTE: Cassa (liquidità disponibile)",
    raw_material_inventory: "Magazzino materie prime",
    finished_goods_inventory: "Magazzino prodotti finiti",
    current_investments: "Investimenti correnti (quota in ammortamento)"
  });

  // STATO PATRIMONIALE - PASSIVO E PATRIMONIO NETTO
  $("report-liabilities").innerHTML=tabella(bs,{
    share_capital: "PATRIMONIO NETTO: Capitale sociale (capitale iniziale + magazzino MP iniziale + utile accumulato)",
    reserves: "Riserve accumulate",
    bank_debt_fixed: "DEBITI: Debiti verso banche (medio-lungo termine)",
    bank_debt_current: "Debiti correnti (breve termine)"
  });

  // CONTO ECONOMICO
  $("report-income").innerHTML=tabella(inc,{
    sales_revenue: "VALORE DELLA PRODUZIONE: Ricavi di vendita (Prodotti A e B venduti x prezzi)",
    variation_finished_goods: "Variazione prodotti finiti (Valore magazzino PF finale - iniziale)",
    purchase_raw_materials: "COSTI ESTERNI: Acquisto materie prime (Quantità acquistata x costo unitario)",
    variation_raw_materials: "Variazione materie prime (Valore magazzino MP finale - iniziale)",
    value_added: "VALORE AGGIUNTO (Valore della Produzione - Costi Esterni)",
    personnel_cost: "Costo del personale (Dipendenti x costo unitario + straordinari x costo orario)",
    ebitda: "MARGINE OPERATIVO LORDO - MOL (Valore Aggiunto - Costo del personale)",
    depreciation: "Ammortamenti (Quota d'esercizio degli investimenti pluriennali)",
    operating_income: "MARGINE OPERATIVO NETTO - MON (MOL - Ammortamenti)",
    interest: "Interessi (Costi finanziari sui finanziamenti bancari)",
    profit: "UTILE D'ESERCIZIO (MON - Interessi)"
  });

  // FLUSSI DI CASSA (RENDICONTO DI CASSA)
  $("report-cashflow").innerHTML=tabella(cf,{
    inflows_from_customers: "FLUSSO DI CASSA OPERATIVO: Entrate da clienti (+ Incassi vendita prodotti A e B)",
    outflows_to_suppliers: "Uscite per fornitori (- Acquisto materie prime)",
    outflows_for_personnel: "Uscite per personale (- Retribuzioni e straordinari)",
    cash_interest: "Interessi (- Pagamento interessi finanziamenti)",
    cash_promotion: "FLUSSO DI CASSA DA INVESTIMENTI: Promozione (- Investimento in visibilità)",
    cash_capacity: "Capacità produttiva (- Investimento in aumento capacità)",
    cash_research: "Ricerca e sviluppo (- Investimento in sviluppo prodotti A e B)",
    debt_acquisition: "FLUSSO DI CASSA DA FINANZIAMENTO: Acquisizione debiti (+ Nuovi finanziamenti)",
    debt_payment: "Pagamento debiti (- Rimborso quota capitale finanziamenti precedenti)"
  });

  // INDICI
  const totalAssets=Number(bs.fixed_investments||0)+Number(bs.cash||0)+Number(bs.raw_material_inventory||0)+Number(bs.finished_goods_inventory||0)+Number(bs.current_investments||0);
  const debt=Number(bs.bank_debt_fixed||0)+Number(bs.bank_debt_current||0);
  const roe=Number(inc.profit||0)/(Number(bs.share_capital||0)||Infinity);
  const roi=Number(inc.operating_income||0)/(totalAssets||Infinity);
  const rod=Number(inc.interest||0)/(debt||Infinity);
  $("report-ratios").innerHTML=tabella({roe,roi,rod,q:debt/(Number(bs.share_capital||0)||Infinity),s:Number(inc.profit||0)/(Number(inc.operating_income||0)||Infinity),leverage:roi-rod},{roe:"ROE (Return On Equity)",roi:"ROI (Return On Investment)",rod:"Costo indebitamento (ROD)",q:"Indice Q (Grado di indebitamento)",s:"Indice S (Incidenza gestione finanziaria)",leverage:"Leva Finanziaria (ROI - ROD)"});
}

// =================================================================
// MERCATO (Restyling Dark Premium + Hover Interattivo)
// =================================================================
function stimaLineare(ini, fin, turno, maxTurns) {
  ini = Number(ini||0); fin = Number(fin||0);
  if (maxTurns <= 1) return Math.round(ini);
  const inc = (fin - ini) / (maxTurns - 1);
  return Math.round(ini + inc * (turno - 1));
}

function calcolaMedia(arr) {
  if (!arr || !arr.length) return 0;
  const valid = arr.map(Number).filter(x => !isNaN(x));
  if (!valid.length) return 0;
  return Math.round((valid.reduce((a,b)=>a+b,0)/valid.length)*100)/100;
}

function aggiornaMercato() {
  const room = stato.room || {}, settings = room.settings || {}, players = room.players || [];
  const currentTurn = stato.player?.current_turn || 1;
  const maxTurns = room.max_turns || 8;

  $("market-current-turn").textContent = currentTurn;
  const stimaA = stimaLineare(settings.market_initial_a, settings.market_final_a, currentTurn, maxTurns);
  const stimaB = stimaLineare(settings.market_initial_b, settings.market_final_b, currentTurn, maxTurns);
  $("market-estimate-label").textContent = `Mercato A: ${stimaA} | Mercato B: ${stimaB}`;

  const pastTurns = Array.from({length: Math.max(0, currentTurn - 1)}, (_, i) => i + 1);
  const marketValA = settings.market_values_a || [];
  const marketValB = settings.market_values_b || [];

  const demandA = pastTurns.map(t => Number(marketValA[t-1] || 0));
  const demandB = pastTurns.map(t => Number(marketValB[t-1] || 0));

  disegnaGraficoAvanzato("chart-demand-a", pastTurns, demandA, "Domanda A", "#3b82f6");
  disegnaGraficoAvanzato("chart-demand-b", pastTurns, demandB, "Domanda B", "#3b82f6");

  const avgPriceA = [], avgVisA = [], avgResA = [];
  const avgPriceB = [], avgVisB = [], avgResB = [];

  pastTurns.forEach(t => {
    const pA = [], vA = [], rA = [];
    const pB = [], vB = [], rB = [];
    players.forEach(p => {
      const turnData = p.history?.[String(t)]?.prodotti || {};
      if (turnData.A) { pA.push(turnData.A.price); vA.push(turnData.A.visibility); rA.push(turnData.A.research); }
      if (turnData.B) { pB.push(turnData.B.price); vB.push(turnData.B.visibility); rB.push(turnData.B.research); }
    });
    avgPriceA.push(calcolaMedia(pA)); avgVisA.push(calcolaMedia(vA)); avgResA.push(calcolaMedia(rA));
    avgPriceB.push(calcolaMedia(pB)); avgVisB.push(calcolaMedia(vB)); avgResB.push(calcolaMedia(rB));
  });

  disegnaGraficoAvanzato("chart-price-a", pastTurns, avgPriceA, "Prezzo medio A", "#ef4444");
  disegnaGraficoAvanzato("chart-visibility-a", pastTurns, avgVisA, "Visibilità media A", "#10b981");
  disegnaGraficoAvanzato("chart-research-a", pastTurns, avgResA, "Ricerca media A", "#8b5cf6");

  disegnaGraficoAvanzato("chart-price-b", pastTurns, avgPriceB, "Prezzo medio B", "#ef4444");
  disegnaGraficoAvanzato("chart-visibility-b", pastTurns, avgVisB, "Visibilità media B", "#10b981");
  disegnaGraficoAvanzato("chart-research-b", pastTurns, avgResB, "Ricerca media B", "#8b5cf6");
}

function disegnaGraficoAvanzato(canvasId, xVals, yVals, label, colorHex) {
  const canvas = $(canvasId); if (!canvas) return;
  const ctx = canvas.getContext("2d"), w = canvas.width, h = canvas.height;

  canvasState[canvasId] = { xVals, yVals, label, colorHex };

  if (!canvas.dataset.hasListener) {
    canvas.addEventListener("mousemove", (ev) => {
      const rect = canvas.getBoundingClientRect();
      const mouseX = (ev.clientX - rect.left) * (canvas.width / rect.width);
      const mouseY = (ev.clientY - rect.top) * (canvas.height / rect.height);
      const st = canvasState[canvasId];
      if (st) renderCanvasContent(canvas, st.xVals, st.yVals, st.label, st.colorHex, mouseX, mouseY);
    });

    canvas.addEventListener("mouseleave", () => {
      const st = canvasState[canvasId];
      if (st) renderCanvasContent(canvas, st.xVals, st.yVals, st.label, st.colorHex, -1, -1);
    });

    canvas.dataset.hasListener = "true";
  }

  renderCanvasContent(canvas, xVals, yVals, label, colorHex, -1, -1);
}

function renderCanvasContent(canvas, xVals, yVals, label, colorHex, mouseX, mouseY) {
  const ctx = canvas.getContext("2d"), w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  // Sfondo Sfumato Dark
  const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
  bgGrad.addColorStop(0, "#1e293b");
  bgGrad.addColorStop(1, "#0f172a");
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, w, h);

  if (!xVals.length || !yVals.length) {
    ctx.fillStyle = "#94a3b8"; ctx.font = "13px Inter, sans-serif";
    ctx.fillText("Nessun dato ancora disponibile", 20, h / 2);
    return;
  }

  const marginL = 52, marginR = 25, marginT = 32, marginB = 38;
  const cW = w - marginL - marginR, cH = h - marginT - marginB;

  const minX = Math.min(...xVals), maxX = Math.max(...xVals);
  let minY = Math.min(...yVals), maxY = Math.max(...yVals);

  if (minY === maxY) { minY -= 10; maxY += 10; }
  const marginY = (maxY - minY) * 0.2;
  minY -= marginY; maxY += marginY;

  const mapX = x => marginL + ((x - (minX === maxX ? minX - 1 : minX)) / ((maxX === minX ? maxX + 1 : maxX) - (minX === maxX ? minX - 1 : minX))) * cW;
  const mapY = y => marginT + cH - ((y - minY) / (maxY - minY)) * cH;

  // Griglia Orizzontale Tratteggiata
  ctx.strokeStyle = "#334155"; ctx.lineWidth = 1; ctx.setLineDash([4, 4]);
  ctx.fillStyle = "#94a3b8"; ctx.font = "11px Inter, sans-serif";
  for (let i = 0; i <= 4; i++) {
    const valY = minY + (maxY - minY) * (i / 4);
    const posY = mapY(valY);
    ctx.beginPath(); ctx.moveTo(marginL, posY); ctx.lineTo(marginL + cW, posY); ctx.stroke();
    ctx.fillText(valY.toFixed(1), 10, posY + 4);
  }
  ctx.setLineDash([]);

  // Punti di Coordinata Calcolati
  const points = xVals.map((x, i) => ({
    x, y: yVals[i],
    px: mapX(x), py: mapY(yVals[i])
  }));

  // Sfumatura di riempimento sotto la linea
  const areaGrad = ctx.createLinearGradient(0, marginT, 0, marginT + cH);
  areaGrad.addColorStop(0, colorHex + "33");
  areaGrad.addColorStop(1, colorHex + "00");
  ctx.fillStyle = areaGrad;
  ctx.beginPath();
  ctx.moveTo(points[0].px, marginT + cH);
  points.forEach(p => ctx.lineTo(p.px, p.py));
  ctx.lineTo(points[points.length - 1].px, marginT + cH);
  ctx.closePath();
  ctx.fill();

  // Curva Principale con Effetto Glow
  ctx.shadowColor = colorHex;
  ctx.shadowBlur = 10;
  ctx.strokeStyle = colorHex;
  ctx.lineWidth = 3;
  ctx.beginPath();
  points.forEach((p, i) => {
    if (i === 0) ctx.moveTo(p.px, p.py); else ctx.lineTo(p.px, p.py);
  });
  ctx.stroke();
  ctx.shadowBlur = 0;

  let activePoint = null;

  // Render dei Punti e delle Etichette Permanenti (Valori Y & X)
  points.forEach((p) => {
    const dist = Math.hypot(mouseX - p.px, mouseY - p.py);
    if (dist < 12) activePoint = p;

    // Asse X (Turno)
    ctx.fillStyle = "#cbd5e1"; ctx.font = "bold 11px Inter, sans-serif";
    ctx.fillText(`T${p.x}`, p.px - 8, h - 12);

    // Etichetta Valore Y sopra il punto
    ctx.fillStyle = "#ffffff"; ctx.font = "bold 11px Inter, sans-serif";
    const textY = p.y.toFixed(1);
    const textW = ctx.measureText(textY).width;
    ctx.fillText(textY, p.px - textW / 2, p.py - 12);

    // Cerchio del Punto
    ctx.beginPath();
    ctx.arc(p.px, p.py, 5, 0, Math.PI * 2);
    ctx.fillStyle = colorHex;
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#ffffff";
    ctx.stroke();
  });

  // Tooltip al Passaggio del Mouse (Hover Interattivo)
  if (activePoint) {
    ctx.beginPath();
    ctx.arc(activePoint.px, activePoint.py, 8, 0, Math.PI * 2);
    ctx.fillStyle = colorHex;
    ctx.fill();
    ctx.lineWidth = 3;
    ctx.strokeStyle = "#ffffff";
    ctx.stroke();

    const tipText = `Turno ${activePoint.x}: ${activePoint.y}`;
    ctx.font = "bold 12px Inter, sans-serif";
    const tipW = ctx.measureText(tipText).width + 16;
    let tipX = activePoint.px - tipW / 2;
    let tipY = activePoint.py - 42;

    if (tipX < 5) tipX = 5;
    if (tipX + tipW > w - 5) tipX = w - tipW - 5;
    if (tipY < 5) tipY = activePoint.py + 15;

    ctx.fillStyle = "#0f172a";
    ctx.shadowColor = "rgba(0,0,0,0.5)";
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.roundRect(tipX, tipY, tipW, 26, 6);
    ctx.fill();
    ctx.strokeStyle = colorHex;
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.shadowBlur = 0;

    ctx.fillStyle = "#ffffff";
    ctx.fillText(tipText, tipX + 8, tipY + 17);
  }
}

// =================================================================
// GUIDA
// =================================================================
function aggiornaGuida() {
  const room = stato.room || {}, s = room.settings || {};
  const pa = s.market_variable_percentages_a || [0,0,0];
  const pb = s.market_variable_percentages_b || [0,0,0];

  $("guide-admin-row1").innerHTML = `<b>MERCATO A</b> Prezzo: ${pa[0]||0}% | Visibilità: ${pa[1]||0}% | Ricerca: ${pa[2]||0}% &nbsp;&nbsp;&nbsp;&nbsp; <b>MERCATO B</b> Prezzo: ${pb[0]||0}% | Visibilità: ${pb[1]||0}% | Ricerca: ${pb[2]||0}%`;
  $("guide-admin-row2").innerHTML = `<b>Interessi:</b> ${s.interests||0}% &nbsp;|&nbsp; <b>Costo acquisto:</b> ${s.purchase_cost||0} &nbsp;|&nbsp; <b>Rapporto inv./capacità:</b> ${s.investment_capacity_ratio||0}`;
  $("guide-admin-row3").innerHTML = `<b>RAPPORTI A</b> Visibilità: ${s.investment_visibility_ratio_a||0} | Ricerca interna: ${s.innovation_internal_research_ratio_a||0} | Co-progettazione: ${s.innovation_coproj_research_ratio_a||0} &nbsp;&nbsp;&nbsp;&nbsp; <b>RAPPORTI B</b> Visibilità: ${s.investment_visibility_ratio_b||0} | Ricerca interna: ${s.innovation_internal_research_ratio_b||0} | Co-progettazione: ${s.innovation_coproj_research_ratio_b||0}`;
}

async function ripristina(){
  caricaSessione();
  if(stato.room_code&&stato.admin_password&&!stato.company_name){
    $("admin-room-code").textContent=stato.room_code;$("share-code").textContent=stato.room_code;show("admin-view");$("header-user").textContent="Amministratore · "+stato.room_code;await aggiornaAdmin();
  }else if(stato.room_code&&stato.company_name){
    try{await aggiornaStato();show("game-view");$("game-title").textContent=stato.company_name;$("game-room").textContent=stato.room_code;$("header-user").textContent=stato.company_name+" · "+stato.room_code;renderGioco();}
    catch(e){tornaAccesso();msg("access-message","Sessione non più disponibile: "+e.message,true);}
  }else show("access-view");
}

$("settings-form").addEventListener("submit",salvaImpostazioni);
$("decisions-form").addEventListener("submit",inviaDecisioni);
setInterval(()=>{if(!document.getElementById("admin-view").classList.contains("hidden"))aggiornaAdmin();},5000);
setInterval(async()=>{if(!document.getElementById("game-view").classList.contains("hidden")){try{await aggiornaStato();renderGioco();}catch(e){}}},8000);
ripristina();
</script>
</body>
</html>
"""

@app.get("/")
def pagina_principale():
    return render_template_string(PAGINA)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
    )