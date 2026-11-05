"""
Interfaccia web del Business Game.
Questo file sostituisce la vecchia interfaccia Kivy di main.py.

Avvio locale:
    python main.py

Deploy su Render:
    Build Command: pip install -r requirements.txt
    Start Command: gunicorn main:app

IMPORTANTE:
- server.py contiene la logica del gioco e le API Flask.
- main.py importa la stessa app Flask e aggiunge l'interfaccia HTML.
- I due file devono trovarsi nella stessa cartella.
"""

import os
from flask import render_template_string

# Riutilizza le API e la logica già presenti in server.py.
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
p{color:var(--muted);line-height:1.5}
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
canvas{width:100%;height:230px;border:1px solid var(--line);border-radius:10px;background:white}
.hidden{display:none!important}
.badge{display:inline-block;border-radius:20px;padding:5px 9px;background:#edf2ff;color:#2446a0;font-size:12px;font-weight:700}
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
      <div class="section"><h3>Andamento dei mercati</h3><div class="grid"><div><h4>Mercato A</h4><canvas id="market-chart-a" width="600" height="230"></canvas></div><div><h4>Mercato B</h4><canvas id="market-chart-b" width="600" height="230"></canvas></div></div></div>
      <div class="section"><h3>Ultimo risultato di mercato</h3><div id="market-results"></div></div>
    </div>
    <div id="tab-report" class="view">
      <div class="section"><h3>Seleziona situazione</h3><select id="report-turn" onchange="aggiornaReport()"><option value="current">Situazione attuale</option></select></div>
      <div class="grid">
        <div class="section"><h3>Stato patrimoniale - Attivo</h3><div id="report-assets"></div></div>
        <div class="section"><h3>Stato patrimoniale - Passivo</h3><div id="report-liabilities"></div></div>
      </div>
      <div class="section"><h3>Conto economico</h3><div id="report-income"></div></div>
      <div class="section"><h3>Flussi di cassa</h3><div id="report-cashflow"></div></div>
      <div class="section"><h3>Indici</h3><div id="report-ratios"></div></div>
    </div>
    <div id="tab-guida" class="view">
      <div class="section"><h3>Come funziona il gioco</h3>
        <p><b>Marketing:</b> prezzo e promozione influenzano la competitività e la visibilità dei prodotti.</p>
        <p><b>Produzione:</b> scegli la quantità da produrre e gli investimenti per aumentare la capacità.</p>
        <p><b>Finanza:</b> puoi richiedere un finanziamento per sostenere le attività aziendali.</p>
        <p><b>Approvvigionamento:</b> acquista materie prime necessarie alla produzione.</p>
        <p><b>Risorse umane:</b> assumi o licenzia personale e definisci gli straordinari.</p>
        <p><b>Ricerca e sviluppo:</b> investi in ricerca interna o co-progettazione per migliorare i prodotti.</p>
        <p>Le scelte vengono elaborate dal server quando tutti i giocatori della stanza hanno confermato il turno.</p>
      </div>
    </div>
  </section>
</main>
<script>
const API = "";
let stato = {room_code:"", company_name:"", admin_password:"", player:null, room:null, personnel:0};
const $ = id => document.getElementById(id);
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
  aggiornaMercato();aggiornaReport();
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
  if(tab==="report")aggiornaReport();if(tab==="mercato")aggiornaMercato();
}
function tabella(obj,labels){
  const rows=Object.entries(labels).map(([k,l])=>`<tr><td>${esc(l)}</td><td>${fmt(obj?.[k])}</td></tr>`).join("");
  return `<div class="table-wrap"><table>${rows}</table></div>`;
}
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
  $("report-assets").innerHTML=tabella(bs,{fixed_investments:"Investimenti fissi",cash:"Cassa",raw_material_inventory:"Magazzino materie prime",finished_goods_inventory:"Magazzino prodotti finiti",current_investments:"Investimenti correnti"});
  $("report-liabilities").innerHTML=tabella(bs,{share_capital:"Capitale sociale",reserves:"Riserve",bank_debt_fixed:"Debiti bancari fissi",bank_debt_current:"Debiti bancari correnti"});
  $("report-income").innerHTML=tabella(inc,{sales_revenue:"Ricavi di vendita",variation_finished_goods:"Variazione prodotti finiti",purchase_raw_materials:"Acquisto materie prime",variation_raw_materials:"Variazione materie prime",value_added:"Valore aggiunto",personnel_cost:"Costo personale",ebitda:"Margine operativo lordo",depreciation:"Ammortamenti",operating_income:"Margine operativo netto",interest:"Interessi",profit:"Utile"});
  $("report-cashflow").innerHTML=tabella(cf,{inflows_from_customers:"Entrate da clienti",outflows_to_suppliers:"Uscite per fornitori",outflows_for_personnel:"Uscite per personale",cash_interest:"Interessi pagati",cash_promotion:"Promozione",cash_capacity:"Investimenti capacità",cash_research:"Ricerca",debt_acquisition:"Nuovi finanziamenti",debt_payment:"Rimborso debiti"});
  const totalAssets=Number(bs.fixed_investments||0)+Number(bs.cash||0)+Number(bs.raw_material_inventory||0)+Number(bs.finished_goods_inventory||0)+Number(bs.current_investments||0);
  const debt=Number(bs.bank_debt_fixed||0)+Number(bs.bank_debt_current||0);
  const roe=Number(inc.profit||0)/(Number(bs.share_capital||0)||Infinity);
  const roi=Number(inc.operating_income||0)/(totalAssets||Infinity);
  const rod=Number(inc.interest||0)/(debt||Infinity);
  $("report-ratios").innerHTML=tabella({roe,roi,rod,q:debt/(Number(bs.share_capital||0)||Infinity),s:Number(inc.profit||0)/(Number(inc.operating_income||0)||Infinity),leverage:roi-rod},{roe:"ROE",roi:"ROI",rod:"Costo indebitamento (ROD)",q:"Q",s:"S",leverage:"Leva"});
}
function aggiornaMercato(){
  const room=stato.room||{},settings=room.settings||{},history=room.market_results_by_turn||{};
  disegnaGrafico("market-chart-a",settings.market_values_a||[],"Mercato A");
  disegnaGrafico("market-chart-b",settings.market_values_b||[],"Mercato B");
  const keys=Object.keys(history).sort((a,b)=>Number(b)-Number(a));
  const last=keys.length?history[keys[0]]:room.market_results||{};
  $("market-results").innerHTML=last&&Object.keys(last).length?`<pre>${esc(JSON.stringify(last,null,2))}</pre>`:"I risultati saranno disponibili dopo la conferma di tutti i giocatori.";
}
function disegnaGrafico(id,values,title){
  const canvas=$(id),ctx=canvas.getContext("2d"),w=canvas.width,h=canvas.height;ctx.clearRect(0,0,w,h);
  ctx.fillStyle="#667085";ctx.font="14px Arial";ctx.fillText(title,14,20);
  if(!values.length){ctx.fillText("Dati non ancora disponibili",14,55);return;}
  const nums=values.map(Number),min=Math.min(...nums),max=Math.max(...nums),range=(max-min)||1;
  ctx.strokeStyle="#d9dfeb";ctx.lineWidth=1;
  for(let i=0;i<5;i++){let y=38+i*(h-70)/4;ctx.beginPath();ctx.moveTo(45,y);ctx.lineTo(w-15,y);ctx.stroke();}
  ctx.strokeStyle="#2457d6";ctx.lineWidth=3;ctx.beginPath();
  nums.forEach((v,i)=>{const x=45+i*(w-65)/Math.max(1,nums.length-1),y=h-32-(v-min)/range*(h-85);if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);});
  ctx.stroke();ctx.fillStyle="#172033";ctx.font="12px Arial";
  nums.forEach((v,i)=>{const x=45+i*(w-65)/Math.max(1,nums.length-1),y=h-32-(v-min)/range*(h-85);ctx.beginPath();ctx.arc(x,y,4,0,Math.PI*2);ctx.fill();ctx.fillText(String(i+1),x-3,h-12);});
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
