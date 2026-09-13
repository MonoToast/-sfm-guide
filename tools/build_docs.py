from pathlib import Path
import re,html,json,hashlib,zipfile
from markdown_it import MarkdownIt
root=Path(__file__).resolve().parents[1]
examples={
'01-first-transfer':('My first transfer','''EVERY 20 TICKS DO
    INPUT FROM source
    OUTPUT TO destination
END'''),
'02-priority-and-overflow':('Workshop first, warehouse second','''EVERY 20 TICKS DO
    INPUT minecraft:iron_ingot FROM incoming
    OUTPUT RETAIN 64 minecraft:iron_ingot TO workshop
    OUTPUT minecraft:iron_ingot TO warehouse
END'''),
'03-reserve-and-restock':('Keep coal in every generator','''-- Configure generator item-input faces if unsided access is unavailable.
EVERY 20 TICKS DO
    INPUT RETAIN 64 minecraft:coal FROM coal_stock
    OUTPUT RETAIN 16 minecraft:coal TO EACH generators
END'''),
'04-furnace-line':('Raw iron furnace line','''-- For vanilla furnaces; all furnaces share the label furnaces.
EVERY 20 TICKS DO
    INPUT minecraft:raw_iron FROM ores
    OUTPUT RETAIN 8 minecraft:raw_iron TO EACH furnaces TOP SIDE
    FORGET

    INPUT minecraft:coal FROM fuel
    OUTPUT RETAIN 8 minecraft:coal TO EACH furnaces BOTTOM SIDE
    FORGET

    INPUT minecraft:iron_ingot FROM furnaces BOTTOM SIDE
    OUTPUT TO finished
END'''),
'05-fluid-top-up':('One bucket of water per tank','''-- 1000 mB = one bucket; configure fluid sides if required.
EVERY 20 TICKS DO
    INPUT fluid:minecraft:water FROM water_source
    OUTPUT RETAIN 1000 fluid:minecraft:water TO EACH water_tanks
END'''),
'06-fe-distribution':('Capped FE delivery','''-- FE-only trigger; source/destination capabilities still limit throughput.
-- Each machine may receive up to 10000 FE per trigger execution.
EVERY TICK DO
    INPUT fe:: FROM battery
    OUTPUT 10000 fe:: TO EACH machines
END'''),
'07-chemical-transfer':('Mekanism oxygen line','''-- Example faces: source outputs chemical to EAST, users accept from WEST.
-- Change these directions or machine settings to match your build.
EVERY 20 TICKS DO
    INPUT chemical:mekanism:oxygen FROM oxygen_source EAST SIDE
    OUTPUT RETAIN 1000 chemical:mekanism:oxygen TO EACH oxygen_users WEST SIDE
END'''),
'08-tag-sorter':('Ingots before other storage','''-- Verify that c:ingots contains the intended items in this installation.
-- If ingot_storage is full, its remaining ingots can reach other_storage.
EVERY 20 TICKS DO
    INPUT FROM incoming
    OUTPUT WITH #c:ingots TO ingot_storage
    OUTPUT TO other_storage
END'''),
'09-lever-enabled':('Lever-enabled transfer','''-- The manager itself must receive the lever signal.
EVERY 20 TICKS DO
    IF REDSTONE GT 0 THEN
        INPUT FROM source
        OUTPUT TO destination
    END
END'''),
'10-pulse-batch':('Cobblestone batch button','''-- Each redstone pulse received by the manager allows up to 16 items.
EVERY REDSTONE PULSE DO
    INPUT 16 minecraft:cobblestone FROM source
    OUTPUT TO destination
END'''),
'11-round-robin':('Alternating station supply','''EVERY 20 TICKS DO
    INPUT minecraft:stone FROM warehouse
    OUTPUT 16 minecraft:stone TO stations ROUND ROBIN BY BLOCK
END'''),
'12-slot-routing':('Chest row routing','''-- Zero-based chest-handler indices; verify indices for other containers.
EVERY 20 TICKS DO
    INPUT FROM cabinet SLOTS 0-8
    OUTPUT TO sorting_chest SLOTS 9-17
END'''),
'13-conditional-restocking':('Keep supplies within a chosen range','''EVERY 20 TICKS DO
    IF supplies HAS LT 32 minecraft:iron_ingot THEN
        INPUT minecraft:iron_ingot FROM warehouse
        OUTPUT RETAIN 64 minecraft:iron_ingot TO supplies
    ELSE IF supplies HAS GT 128 minecraft:iron_ingot THEN
        INPUT RETAIN 128 minecraft:iron_ingot FROM supplies
        OUTPUT TO warehouse
    ELSE
        -- No work needed in this range.
    END
END'''),
'14-independent-jobs':('Two independent routes','''EVERY 20 TICKS DO
    INPUT FROM mined_items
    OUTPUT TO ore_storage
    FORGET

    INPUT FROM harvested_crops
    OUTPUT TO food_storage
END'''),
'15-resource-and-block-each':('Maintain iron and gold at every workbench','''-- workbenches means ordinary supply chests, not crafting-table blocks.
EVERY 20 TICKS DO
    INPUT minecraft:iron_ingot OR minecraft:gold_ingot FROM warehouse
    OUTPUT RETAIN 16 EACH minecraft:iron_ingot OR minecraft:gold_ingot TO EACH workbenches
END'''),
'16-empty-slot-insertion':('Only empty destination slots','''EVERY 20 TICKS DO
    INPUT FROM drops
    OUTPUT TO EMPTY SLOTS IN storage
END'''),
}
for slug,(title,code) in examples.items():
 (root/'examples'/(slug+'.sfml')).write_text(f'NAME "{title}"\n\n{code}\n',encoding='utf-8')
md=MarkdownIt('commonmark',{'html':False}).enable('table')
text=(root/'GUIDE.md').read_text()
tokens=md.parse(text)
headings=[];used={}
for i,t in enumerate(tokens):
 if t.type=='heading_open':
  label=tokens[i+1].content
  slug=re.sub(r'[^a-z0-9]+','-',label.lower()).strip('-')
  n=used.get(slug,0);used[slug]=n+1
  if n:slug+=f'-{n}'
  t.attrSet('id',slug)
  if t.tag=='h2':headings.append((slug,label))
rendered=md.renderer.render(tokens,md.options,{})
parts=re.split(r'(?=<h2\b)',rendered)
content='<div class="intro">'+parts[0]+'</div>'
for part,(slug,title) in zip(parts[1:],headings):
 content+='<section class="chapter" data-title="'+html.escape(title,quote=True)+'">'+part+'</section>'
toc=''.join(f'<a href="#{s}">{html.escape(t)}</a>' for s,t in headings)
css='''
:root{color-scheme:light;--bg:#f7f8fa;--paper:#fff;--ink:#1c2938;--muted:#546579;--line:#dce3eb;--accent:#146954;--soft:#e8f4ef;--code:#142332;--codetext:#edf4fa;--side:285px}
:root.dark{color-scheme:dark;--bg:#111b24;--paper:#16232e;--ink:#e8eef5;--muted:#adbed0;--line:#344555;--accent:#80d5b4;--soft:#203a36;--code:#0b141d;--codetext:#e7f3ff}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:22px}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.72 system-ui,-apple-system,Segoe UI,sans-serif}a{color:var(--accent);text-underline-offset:3px}a:hover{text-decoration-thickness:2px}button,input{font:inherit}button{cursor:pointer;border:1px solid var(--line);border-radius:7px;padding:6px 11px;background:var(--paper);color:var(--ink)}button:hover{background:var(--soft)}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid var(--accent);outline-offset:3px}[hidden]{display:none!important}
aside{position:fixed;inset:0 auto 0 0;width:var(--side);padding:25px 20px 20px;background:var(--paper);border-right:1px solid var(--line);display:flex;flex-direction:column;gap:16px}.brand{display:flex;gap:12px;align-items:center;color:var(--ink);text-decoration:none;font-weight:750;line-height:1.3}.logo{display:grid;place-items:center;width:44px;height:44px;flex:0 0 44px;background:var(--accent);color:var(--paper);border-radius:10px;font-size:13px;letter-spacing:.4px}.version{display:block;font-size:12px;font-weight:500;color:var(--muted);margin-top:4px}.searchbox label{display:block;font-size:12px;font-weight:700;margin-bottom:5px}.searchbox input{width:100%;padding:9px 10px;border:1px solid var(--line);border-radius:7px;background:var(--bg);color:var(--ink);font-size:14px}.searchhint{font-size:11px;color:var(--muted);margin-top:5px}nav{overflow:auto;flex:1}nav a{display:block;font-size:13px;line-height:1.45;padding:7px 9px;border-radius:6px;color:var(--muted);text-decoration:none}nav a:hover,nav a.active{color:var(--accent);background:var(--soft)}.tools{display:flex;gap:7px;flex-wrap:wrap}.tools button,.tools a{font-size:12px}.download{font-size:12px;color:var(--muted);margin:0}.download a{margin-right:10px}
main{margin-left:var(--side);padding:40px clamp(22px,4vw,70px) 70px;max-width:1450px}.eyebrow{font-size:12px;font-weight:750;letter-spacing:1.5px;text-transform:uppercase;color:var(--accent);margin:0 0 9px}.status{background:var(--soft);border:1px solid var(--line);padding:12px 17px;border-radius:9px;margin:0 0 22px;font-size:14px;display:flex;align-items:center;gap:14px;justify-content:space-between}h1{font-size:clamp(30px,3.2vw,45px);line-height:1.14;letter-spacing:-1.5px;margin:0 0 17px;max-width:800px}h2{font-size:26px;line-height:1.3;letter-spacing:-.5px;margin:0 0 23px;padding-bottom:13px;border-bottom:1px solid var(--line)}h3{font-size:19px;line-height:1.4;margin:30px 0 12px}p{margin:0 0 17px}li{margin:5px 0}strong{font-weight:700}.intro{max-width:930px;margin-bottom:34px}.intro>p:first-of-type{color:var(--muted)}.chapter{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:28px 30px;margin:25px 0;min-width:0;box-shadow:0 2px 6px #00000003}.chapter>*:last-child{margin-bottom:0}.chapter:target{border-color:var(--accent)}
code{font:13px/1.55 Consolas,'Cascadia Code',ui-monospace,monospace;background:var(--soft);color:var(--ink);padding:2px 4px;border-radius:4px;overflow-wrap:anywhere}pre{position:relative;background:var(--code);color:var(--codetext);border-radius:9px;margin:20px 0;padding:43px 19px 19px;overflow:auto;tab-size:4}pre code{font-size:13px;background:none;color:inherit;padding:0;white-space:pre;overflow-wrap:normal}.copy{position:absolute;right:10px;top:9px;font-size:11px;line-height:1.2;background:#ffffff12;color:#d7e8f5;border:1px solid #ffffff30;padding:5px 9px}.copy:hover{background:#ffffff25}.codekind{position:absolute;top:11px;left:18px;font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#9eb4c8}.kw{color:#82d9b9;font-weight:600}.num{color:#f4c475}.comment{color:#9fb1c4}.str{color:#b6cef5}.table-scroll{overflow-x:auto;margin:19px 0}table{width:100%;border-collapse:collapse;font-size:14px;line-height:1.55}th{text-align:left;background:var(--soft);font-size:12px;font-weight:750}td,th{padding:11px 13px;border-bottom:1px solid var(--line);vertical-align:top}td:first-child{min-width:145px}td code,th code{font-size:12px}tr:last-child td{border-bottom:0}blockquote{border-left:3px solid var(--accent);margin:20px 0;padding:8px 18px;background:var(--soft)}footer{font-size:12px;color:var(--muted);margin-top:30px}.mobile-toggle{display:none}.lab{border:1px solid var(--line);border-radius:9px;background:var(--soft);padding:18px;margin:20px 0}.lab h3{margin-top:0}.lab-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.lab label{font-size:12px;display:block;font-weight:650}.lab input{width:100%;padding:7px;border:1px solid var(--line);border-radius:5px;background:var(--paper);color:var(--ink);margin-top:5px}.lab output{font-size:18px;display:block;margin-top:13px;font-weight:700}.lab p{font-size:13px;margin-top:8px}.lab code{font-size:12px}
@media(min-width:1500px){main{margin-right:auto}}@media(max-width:1050px){:root{--side:245px}aside{padding:20px 13px}.chapter{padding:23px 21px}.lab-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:740px){aside{position:relative;width:100%;height:auto;border-right:0;border-bottom:1px solid var(--line);gap:12px;padding:18px}nav{max-height:240px;display:none}aside.open nav{display:block}.mobile-toggle{display:block}.tools{align-items:center}main{margin:0;padding:24px 13px 45px}.chapter{padding:21px 16px;border-radius:8px}h1{font-size:32px}h2{font-size:23px}body{font-size:15px}.brand{font-size:16px}.searchhint{display:none}.download{display:none}pre code{font-size:12px}}
@media print{:root{color-scheme:light;--paper:#fff;--bg:#fff;--ink:#000;--muted:#333;--line:#ccc;--soft:#f1f1f1;--accent:#155d4d}aside,.eyebrow,.status,.copy,.lab,footer button{display:none!important}main{margin:0;padding:0;max-width:none}.chapter{display:block!important;border:0;border-radius:0;box-shadow:none;padding:0;margin:30px 0;break-before:auto}h2,h3{break-after:avoid}pre{white-space:pre-wrap;break-inside:avoid;padding:16px;background:#f5f5f5;color:#111;border:1px solid #ddd}pre code{white-space:pre-wrap;color:#111;font-size:10px}.codekind{display:none}.kw,.num,.str,.comment{color:#111}table{font-size:10px}td,th{padding:6px}tr{break-inside:avoid}.table-scroll{overflow:visible}a{color:#155d4d;text-decoration:none}h1{font-size:30px}h2{font-size:23px}body{font-size:11px}.intro{max-width:none}}
'''
js=r'''
const qs=s=>document.querySelector(s), all=s=>[...document.querySelectorAll(s)];
const chapters=all('.chapter'), navlinks=all('nav a');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const words='NAME EVERY DO END INPUT FROM OUTPUT TO RETAIN EACH EXCEPT FORGET EMPTY SLOTS SLOT IN WITH WITHOUT TAG IF THEN ELSE HAS OVERALL SOME ONE LONE TRUE FALSE NOT AND OR GT LT EQ GE LE ROUND ROBIN BY LABEL BLOCK SIDE TOP BOTTOM NORTH EAST SOUTH WEST FRONT BACK LEFT RIGHT NULL TICK TICKS SECOND SECONDS GLOBAL G PLUS REDSTONE PULSE'.split(' '), keywords=new Set(words);
all('pre').forEach(pre=>{
 const code=pre.querySelector('code'), original=code.textContent, isProgram=code.classList.contains('language-sfml');
 if(isProgram){let out='',end=0;const tokens=/--[^\r\n]*|"(?:\\.|[^"\\])*"|\b[A-Za-z_]+\b|\b[0-9]+\b/g;let m;while((m=tokens.exec(original))){out+=esc(original.slice(end,m.index));let v=m[0],cls=v.startsWith('--')?'comment':v.startsWith('"')?'str':keywords.has(v.toUpperCase())?'kw':/^\d+$/.test(v)?'num':'';out+=cls?'<span class="'+cls+'">'+esc(v)+'</span>':esc(v);end=tokens.lastIndex}out+=esc(original.slice(end));code.innerHTML=out}
 const kind=document.createElement('span');kind.className='codekind';kind.textContent=isProgram?'SFML · complete program':'Reference notation';pre.prepend(kind);
 const btn=document.createElement('button');btn.className='copy';btn.type='button';btn.textContent='Copy';btn.setAttribute('aria-label',isProgram?'Copy SFML program':'Copy reference notation');
 btn.addEventListener('click',async()=>{try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(original)}else{const t=document.createElement('textarea');t.value=original;t.style.position='fixed';t.style.left='-9999px';document.body.append(t);t.select();if(!document.execCommand('copy'))throw new Error('Copy unavailable');t.remove()}btn.textContent='Copied';setTimeout(()=>btn.textContent='Copy',1500)}catch(e){btn.textContent='Select and copy';const sel=window.getSelection(),range=document.createRange();range.selectNodeContents(code);sel.removeAllRanges();sel.addRange(range)}});pre.append(btn)
});
all('table').forEach(t=>{let wrap=document.createElement('div');wrap.className='table-scroll';t.parentNode.insertBefore(wrap,t);wrap.append(t)});
const entries=chapters.map((node,i)=>({node,link:navlinks[i],text:node.textContent.toLowerCase()}));
function filter(){const terms=qs('#search').value.toLowerCase().trim().split(/\s+/).filter(Boolean);let count=0;entries.forEach(e=>{const show=terms.every(t=>e.text.includes(t));e.node.hidden=!show;e.link.hidden=!show;if(show)count++});qs('#status').hidden=!terms.length;qs('#result').textContent=count+' of '+entries.length+' chapters match';qs('.intro').hidden=terms.length>0}
qs('#search').addEventListener('input',filter);qs('#clear').addEventListener('click',()=>{qs('#search').value='';filter();qs('#search').focus()});
function revealHash(){const id=decodeURIComponent(location.hash.slice(1)),target=document.getElementById(id);if(target&&target.closest('.chapter')?.hidden){qs('#search').value='';filter();target.scrollIntoView()}}
window.addEventListener('hashchange',revealHash);revealHash();
qs('#theme').addEventListener('click',()=>{const dark=document.documentElement.classList.toggle('dark');qs('#theme').textContent=dark?'Light theme':'Dark theme';try{localStorage.setItem('sfml-docs-theme',dark?'dark':'light')}catch(e){}});
try{if(localStorage.getItem('sfml-docs-theme')==='dark'){document.documentElement.classList.add('dark');qs('#theme').textContent='Light theme'}}catch(e){}
qs('#print').addEventListener('click',()=>window.print());qs('#navtoggle').addEventListener('click',()=>{let open=qs('aside').classList.toggle('open');qs('#navtoggle').setAttribute('aria-expanded',String(open))});
window.addEventListener('keydown',e=>{if(e.key==='/'&&!['INPUT','TEXTAREA'].includes(document.activeElement.tagName)){e.preventDefault();qs('#search').focus()}if(e.key==='Escape'&&document.activeElement===qs('#search')){qs('#search').value='';filter();qs('#search').blur()}});
if('IntersectionObserver'in window){const obs=new IntersectionObserver(list=>{list.forEach(x=>{if(x.isIntersecting){navlinks.forEach(a=>a.classList.toggle('active',a.hash==='#'+x.target.id))}})},{rootMargin:'0px 0px -75% 0px'});all('.chapter h2').forEach(h=>obs.observe(h))}
// An illustrative arithmetic model: one resource, one source, one destination.
const retentionChapter=chapters.find(s=>s.dataset.title.startsWith('7.'));
const lab=document.createElement('div');lab.className='lab';lab.innerHTML='<h3>Try an OUTPUT RETAIN calculation</h3><p>One item type and one destination; assumes sufficient capacity and no other transfer limits.</p><div class="lab-grid"><label>Available from source<input id="lab-source" type="number" min="0" step="1" value="100"></label><label>Already at destination<input id="lab-stock" type="number" min="0" step="1" value="50"></label><label>Quantity limit<input id="lab-limit" type="number" min="0" step="1" value="16"></label><label>RETAIN target<input id="lab-target" type="number" min="0" step="1" value="64"></label></div><output id="lab-output" aria-live="polite"></output><p id="lab-rule"></p><p>This is an explanatory calculator, not the SFM runtime.</p>';
retentionChapter.querySelector('h3').before(lab);
function calc(){const val=id=>Math.max(0,Math.floor(Number(qs('#lab-'+id).value)||0));const source=val('source'),stock=val('stock'),limit=val('limit'),target=val('target'),moved=Math.min(source,limit,Math.max(0,target-stock));qs('#lab-output').textContent=moved+' items may move → '+(stock+moved)+' at destination';qs('#lab-rule').textContent='OUTPUT '+limit+' RETAIN '+target+' minecraft:iron_ingot TO supply'}
all('.lab input').forEach(i=>i.addEventListener('input',calc));calc();
// Expose only read-only counts so offline UI checks can confirm enhancement completed.
document.body.dataset.ready='true';document.body.dataset.chapters=String(chapters.length);
'''
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="SFML programming manual for Super Factory Manager 4.34. Keywords, examples, resource routing, and troubleshooting."><title>Super Factory Manager · SFML programming guide</title><style>'''+css+'''</style></head><body><aside aria-label="Documentation navigation"><a class="brand" href="#"><span class="logo" aria-hidden="true">SFML</span><span>Super Factory Manager<span class="version">Programming guide · SFM 4.34</span></span></a><div class="searchbox"><label for="search">Find a keyword or topic</label><input id="search" type="search" placeholder="Try RETAIN, slots, Mekanism…" autocomplete="off"><div class="searchhint">Press / to search · Esc to clear</div></div><button class="mobile-toggle" id="navtoggle" aria-expanded="false" aria-controls="toc">Contents</button><nav id="toc" aria-label="Chapters">'''+toc+'''</nav><div class="tools"><button id="theme">Dark theme</button><button id="print">Print / PDF</button></div><p class="download"><a href="GUIDE.md" download>Markdown</a><a href="Super-Factory-Manager-Guide.pdf" download>PDF</a><a href="examples.zip" download>Examples</a></p></aside><main><p class="eyebrow">Super Factory Manager 4.34 · Automation reference</p><div class="status" id="status" hidden><span id="result" role="status" aria-live="polite"></span><button id="clear">Clear search</button></div>'''+content+'''<footer>AI-generated independent guide · SFM 4.34. Prepared September 13, 2026. Works offline; no external scripts, fonts, or analytics. <a href="README.md">Package information</a> · <a href="VALIDATION.md">Validation details</a></footer></main><script>'''+js+'''</script></body></html>'''
(root/'index.html').write_text(page,encoding='utf-8')
with zipfile.ZipFile(root/'examples.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted((root/'examples').glob('*.sfml')):z.write(f,'examples/'+f.name)
(root/'README.md').write_text('# Super Factory Manager 4.34 programming guide\n\nA modpack-independent reference for SFML: keyword meanings, transfer rules, practical examples, and troubleshooting.\n\n**AI disclosure:** This guide was generated by AI using SFM 4.34 source code and official examples. It is an independent guide, not official SFM documentation. See [VALIDATION.md](VALIDATION.md) for checks and limitations.\n\nOpen [index.html](index.html) locally in a browser, or browse [GUIDE.md](GUIDE.md) on GitHub. The browser edition works offline and includes chapter search, copy buttons, a light/dark theme, an interactive OUTPUT RETAIN calculator, and a print layout.\n\n## Contents\n\n- [GUIDE.md](GUIDE.md): complete manual, 20 chapters.\n- [PDF edition](Super-Factory-Manager-Guide.pdf): printable manual.\n- [examples/](examples/): 16 complete programs with setup notes.\n- [examples.zip](examples.zip): all example programs in one download.\n- [VALIDATION.md](VALIDATION.md): source version, checks, and test boundaries.\n\n## Version scope\n\nThe guide covers **SFM 4.34** and is checked against **SFM 4.34.0 for Minecraft 1.21.1 / NeoForge**. Optional integrations and other Minecraft ports can differ; version-specific details are identified in the text.\n\nUpstream source tag: `4.34.0-1.21.1`; commit `f5366c79c823ff52712130e69dd9c8166c70bd14`.\n\n## GitHub Pages\n\nIn this repository, select **Settings → Pages → Deploy from a branch → main → /(root) → Save**. The `.nojekyll` file keeps the already-built HTML and downloads unchanged.\n\nAfter Pages is enabled and deployment completes, the site address for this repository is:\nhttps://monotoast.github.io/-sfm-guide/\n\n## Editing and rebuilding\n\nEdit `GUIDE.md` for the manual and the example definitions in `tools/build_docs.py` for the downloadable scripts. With Python 3 installed:\n\n```sh\npython -m pip install -r tools/requirements.txt\npython tools/build_docs.py\n```\n\nThe build regenerates `index.html`, `examples/`, and `examples.zip`. To refresh the PDF, open the browser edition and use **Print / PDF**, saving as `Super-Factory-Manager-Guide.pdf`. When exporting a public PDF from a local copy, use a browser print/export process that resolves relative links against the published website URL rather than a personal filesystem path.\n\nSource code and official examples for the mod are available from [TeamDman/SuperFactoryManager](https://github.com/TeamDman/SuperFactoryManager). This is an independent guide.\n',encoding='utf-8')
print('Built',len(headings),'chapters,',len(examples),'programs; HTML',len(page),'characters')
