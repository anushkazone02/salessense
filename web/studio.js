"use strict";
const $ = id => document.getElementById(id);
const esc = value => String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]);
const num = n => Number(n).toLocaleString("en-US");

const options = values => values.map(v=>`<option>${esc(v)}</option>`).join("");
const pages = {
  overview:["Overview","Retail intelligence","Sales overview","Explore grocery demand by city and product family in Ecuador."],
  analytics:["Sales analytics","Spark computation","Sales analytics","Compare trading patterns using aggregates computed with Apache Spark."],
  models:["Model comparison","Machine learning","Model comparison","Four Spark regressors evaluated against the same validation store-family-days."],
  predict:["Demand forecast","Inference studio","Demand forecast","Choose a city, store and product family to estimate tomorrow’s unit sales."],
  batch:["Batch scoring","Inference studio","Batch scoring","Run multiple store-family plans through the same saved Spark pipeline."],
  method:["Methodology","Project notes","Methodology","How the dataset, training pipeline and dashboard fit together."]
};
const icons={grid:"M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z",chart:"M3 3v18h18 M7 16l4-6 4 2 5-7",layers:"M3 7l9-4 9 4-9 4z M3 12l9 4 9-4 M3 17l9 4 9-4",pulse:"M2 12h5l3-8 4 16 3-8h5",table:"M3 4h18v16H3z M3 9h18 M3 14h18 M9 9v11",book:"M4 3h13l3 3v15H4z M8 9h8 M8 13h8 M8 17h6"};
document.querySelectorAll("nav a").forEach(a=>a.insertAdjacentHTML("afterbegin",`<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"><path d="${icons[a.dataset.icon]}"/></svg>`));
let cfg, overview, models, analytics, metric="revenue", revision=0;
function note(text="", error=false){$("message").hidden=!text;$("message").textContent=text;$("message").className=error?"error":"";}
async function request(url,init){
  const r=await fetch(url,init);
  if(!r.ok){let detail;try{detail=(await r.json()).detail;}catch{}throw Error(typeof detail==="string"?detail:Array.isArray(detail)?detail.map(d=>d.loc.slice(-1)+": "+d.msg).join("; "):"Request failed. Check the local API terminal and try again.");}
  return r;
}
function table(headers,rows,first=false){
  return '<div class="tablewrap"><table><thead><tr>'+headers.map(x=>`<th scope="col">${esc(x)}</th>`).join("")+"</tr></thead><tbody>"+
    rows.map((r,i)=>`<tr class="${first&&i===0?"winnerRow":""}">${r.map(x=>`<td>${esc(x)}</td>`).join("")}</tr>`).join("")+"</tbody></table></div>";
}
function cards(target,items){$(target).innerHTML=items.map(([label,value,hint])=>`<div class="kpi"><div class="eyebrow">${esc(label)}</div><strong>${esc(value)}</strong><small>${esc(hint)}</small></div>`).join("");}
function plot(id,traces,layout={}){
  return Plotly.react(id,traces,{autosize:true,height:258,margin:{l:55,r:14,t:15,b:32},font:{family:"Segoe UI, Arial",size:11,color:"#476254"},
    paper_bgcolor:"transparent",plot_bgcolor:"transparent",showlegend:false,hovermode:"closest",
    colorway:["#216a52","#b17737","#658aab"],xaxis:{showgrid:false,automargin:true},yaxis:{gridcolor:"#e8ece4",automargin:true},...layout},
    {responsive:true,displayModeBar:false,scrollZoom:false}).then(()=>Plotly.Plots.resize($(id)));
}
function drawTrend(){
  const avg=metric==="average";
  document.querySelectorAll("[data-metric]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.metric===metric)));
  plot("trend",[{type:"scatter",mode:"lines+markers",x:overview.months.map(x=>x.month),
    y:overview.months.map(x=>avg?(x.records?x.units/x.records:null):x.units),fill:"tozeroy",fillcolor:"rgba(80,145,96,.13)",
    line:{color:"#247254",width:2.7},marker:{size:4},hovertemplate:"%{x|%b %Y}<br>%{y:,.0f}<extra></extra>"}],
    {hovermode:"x unified",yaxis:{gridcolor:"#e8ece4",rangemode:"tozero"}});
}
async function showOverview(token){
  const query=new URLSearchParams(new FormData($("filters")));
  const d=await(await request("/api/overview?"+query)).json();if(token!==revision)return;
  overview=d;$("export").href="/api/overview.csv?"+query;$("dashboardBody").hidden=!d.days;
  if(!d.days){note("No store-family records match these filters.");return;}
  cards("totals",[["UNITS SOLD",num(Math.round(d.units)),"Selected history · rounded"],["PRODUCT FAMILIES",num(d.families),"Grocery and household ranges"],["STORES",num(d.stores),"Across selected cities"],["OBSERVATIONS",num(d.days),"Store × family × day"]]);
  drawTrend();
  $("regions").innerHTML=d.groups.slice(0,5).map(g=>{const share=d.units?100*g.units/d.units:0;return `<div class="region"><div><b>${esc(g.name)}</b><span>${share.toFixed(1)}%</span></div><div class="track"><i style="width:${share}%"></i></div></div>`;}).join("");
  $("categories").innerHTML=table(["Product family","Units sold","Store-family-days","Days with promotions"],d.groups.map(g=>[g.name,num(Math.round(g.units)),num(g.records),num(g.promoted)]));
}
const decimal=n=>Number(n).toLocaleString("en-US",{maximumFractionDigits:2,minimumFractionDigits:2});
function showModels(m){
  $("leader").innerHTML=`<div class="banner"><div><div class="eyebrow">ONE-DAY FORECAST MODEL</div><strong>${esc(m.winner)}</strong></div><span>Validation RMSE · ${decimal(m.candidates[0].rmse)}</span></div>`;
  $("ranking").innerHTML=table(["Spark regressor","RMSE ↓","MAE ↓","R²","Fit time"],m.candidates.map(x=>[x.model,decimal(x.rmse),decimal(x.mae),x.r2.toFixed(3),x.fit_seconds.toFixed(1)+" s"]),true)+
    `<p class="muted">${num(m.train_rows)} training observations · ${num(m.validation_rows)} validation store-family-days. Errors are in daily sales units.</p>`;
  cards("testmetrics",[["TEST RMSE",decimal(m.test.rmse),"July–15 August 2017"],["TEST MAE",decimal(m.test.mae),"Average error in units"],["TEST R²",m.test.r2.toFixed(3),"Explained variation"],["TEST WAPE",(100*m.test.wape).toFixed(1)+"%","Total absolute error / total units"]]);
  $("bench").innerHTML=table(["Test comparison","RMSE ↓","MAE ↓","Matched observations"],[[m.winner,m.matched_winner],["Same family and store last week",m.baseline]].map(([n,x])=>[n,decimal(x.rmse),decimal(x.mae),num(x.rows)]),true);
  const actual=m.sample.map(x=>x.sales),pred=m.sample.map(x=>x.pred),max=Math.max(...actual,...pred);
  plot("fitplot",[{x:actual,y:pred,mode:"markers",marker:{size:5,opacity:.55}},{x:[0,max],y:[0,max],mode:"lines",line:{dash:"dot"}}],{xaxis:{title:{text:"Actual units sold"}},yaxis:{title:{text:"Forecast"}}});
  plot("residuals",[{x:m.sample.map(x=>x.sales-x.pred),type:"histogram",nbinsx:35}],{xaxis:{title:{text:"Actual minus forecast"}}});
}
function showAnalytics(a){
  const names=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
  const plots=[
    ["cities","Cities with the most unit sales",a.cities.slice(0,8),"city","units",v=>v],
    ["families","Leading product families",a.families.slice(0,8),"family","units",v=>v],
    ["weekdays","Average daily units by weekday",[...a.weekdays].sort((x,y)=>x.weekday-y.weekday),"weekday","average",v=>names[v]],
    ["promotion","Average units with a promotion",a.promotion,"promoted","average",v=>v?"Items promoted":"None promoted"]];
  $("analyticsBody").innerHTML='<p class="muted">Spark aggregates from the complete labeled history. Averages are per store-family-day. Promotion groups show observed differences.</p><div class="grid halves">'+plots.map(([id,title])=>`<article><div class="eyebrow">GROCERY DEMAND</div><h2>${title}</h2><div id="chart-${id}"></div></article>`).join("")+"</div>";
  for(const [id,,rows,field,value,label] of plots)plot("chart-"+id,[{type:"bar",x:rows.map(x=>label(x[field])),y:rows.map(x=>x[value]),hovertemplate:"%{x}<br>%{y:,.1f} units<extra></extra>"}],{margin:{l:58,r:12,t:12,b:82}});
}
function cities(){return [...new Set(cfg.stores.map(s=>s.city))].sort();}
function fillForm(){
  $("inputs").innerHTML=`<label>City<select id="planCity">${options(cities())}</select></label><label>Store<select name="store_nbr"></select></label>
    <label>Product family<select name="family">${options(cfg.families)}</select></label><label>Forecast date<input type="date" name="date" min="${cfg.forecast_first}" max="${cfg.next}" value="${cfg.next}" required></label>
    <label>Items on promotion<input name="onpromotion" type="number" min="0" max="2147483647" step="1" required><small id="planHint"></small></label>`;
  const fields=$("single").elements, city=$("planCity"), hint=$("planHint");let version=0;
  city.value="Quito";fields.family.value="DAIRY";
  async function promotion(){
    const token=++version;
    fields.onpromotion.value="";hint.textContent="Loading recorded plan…";
    const q=new URLSearchParams({store_nbr:fields.store_nbr.value,family:fields.family.value,day:fields.date.value});
    try{const p=await(await request("/api/promotion?"+q)).json();if(token!==version)return;
      fields.onpromotion.value=p.onpromotion??"";hint.textContent=p.onpromotion===null?"Enter a planned count.":"Recorded promotion plan · editable";
      $("estimate").textContent="—";
      $("estimateNote").textContent=p.prior_week?`Recorded on ${p.prior_week.date}: ${decimal(p.prior_week.sales)} units of ${fields.family.value.toLowerCase()} at ${city.value}, Store ${fields.store_nbr.value}. Submit your plan to forecast the next week’s matching weekday.`:"No matching prior-week record. Submit the plan for an estimate.";
    }catch{if(token===version)hint.textContent="Enter a planned count.";}
  }
  function stores(){
    fields.store_nbr.innerHTML=cfg.stores.filter(s=>s.city===city.value).map(s=>`<option value="${s.store_nbr}">${esc(s.city)} · Store ${s.store_nbr} (${esc(s.state)})</option>`).join("");
    promotion();
  }
  city.onchange=stores; fields.store_nbr.onchange=fields.family.onchange=fields.date.onchange=promotion;
  stores();document.querySelectorAll(".model-chip").forEach(el=>el.textContent="Serving · "+cfg.winner);
}
async function route(){
  const token=++revision, hash=location.hash.slice(1),key=Object.hasOwn(pages,hash)?hash:"overview";
  const [label,kicker,title,sub]=pages[key];
  $("crumb").textContent=label;$("kicker").textContent=kicker.toUpperCase();$("title").textContent=title;$("subtitle").textContent=sub;document.title=label+" | SalesSense";
  Object.keys(pages).forEach(p=>$(p).hidden=p!==key);$("export").hidden=key!=="overview";
  document.querySelectorAll("nav a").forEach(a=>a.hash==="#"+key?a.setAttribute("aria-current","page"):a.removeAttribute("aria-current"));note();
  try{
    if(key==="overview")await showOverview(token);
    if(key==="models"){models??=await (await request("/api/models")).json();if(token===revision)showModels(models);}
    if(key==="analytics"){if(!analytics)note("Loading full-history Spark aggregates…");analytics??=await (await request("/api/analytics")).json();if(token===revision){note();showAnalytics(analytics);}}
  }catch(e){if(token===revision)note(e.message,true);}
}
$("single").onsubmit=async e=>{
  e.preventDefault();const form=e.currentTarget,submit=form.querySelector("button"),data=Object.fromEntries(new FormData(form));submit.disabled=true;$("estimate").textContent="…";$("estimateNote").textContent="Scoring with Spark. The first request loads the fitted pipeline.";
  for(const key of ["store_nbr","onpromotion"])data[key]=Number(data[key]);
  try{const result=await (await request("/api/predict",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)})).json();$("estimate").textContent=decimal(result.units);$("estimateNote").textContent="Forecast units for the submitted product family and store.";}
  catch(err){$("estimate").textContent="—";$("estimateNote").textContent=err.message;}finally{submit.disabled=false;}
};
$("batchForm").onsubmit=async e=>{
  e.preventDefault();const form=e.currentTarget,submit=form.querySelector("button");submit.disabled=true;$("batchNote").textContent="Scoring uploaded rows with Spark…";
  try{const r=await request("/api/predict/batch",{method:"POST",body:new FormData(form)}),url=URL.createObjectURL(await r.blob()),a=document.createElement("a");a.href=url;a.download="sales-predictions.csv";a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);$("batchNote").textContent="Scoring complete. Your predictions CSV is ready in your downloads.";}
  catch(err){$("batchNote").textContent=err.message;}finally{submit.disabled=false;}
};
async function start(){
  cfg=await (await request("/api/config")).json();fillForm();
  const f=$("filters"),fields=f.elements;
  fields.city.insertAdjacentHTML("beforeend",options(cities()));fields.family.insertAdjacentHTML("beforeend",options(cfg.families));
  for(const name of ["start","end"]){fields[name].min=cfg.first;fields[name].max=cfg.last;fields[name].defaultValue=name==="start"?cfg.first:cfg.last;}
  f.onsubmit=e=>{e.preventDefault();route();};f.onreset=()=>setTimeout(route,0);
  document.querySelectorAll("[data-metric]").forEach(b=>b.onclick=()=>{metric=b.dataset.metric;drawTrend();});
  window.addEventListener("hashchange",()=>{window.scrollTo(0,0);route();});await route();
}
start().catch(e=>note(e.message,true));
