'use strict';
// Reuses only existing repository research. No new ratings or remote requests.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'..'),DIR=path.join(ROOT,'research'),read=f=>JSON.parse(fs.readFileSync(path.join(ROOT,f),'utf8'));
const roster=read('site-v3/research-roster.json'),base=read('research.json'),ranking=read('ranking.json'),portfolio=read('portfolio-review.json'),expanded=read('expanded-review.json');
const DOCS=[
 ['RESEARCH.md','기초 업체 조사','업체별 주택 사례·지역 기반·조사 출처'],
 ['PORTFOLIO-REVIEW.md','다른 후보 포트폴리오','9개 후보·협업팀의 준공 사례 비교'],
 ['DETAIL-REVIEW.md','결과물 정밀 검토','설계 의도·조직·사진·공정 기록 대조'],
 ['DUE-DILIGENCE.md','도급범위·반복 팀','11개 프로젝트의 공종 범위와 협력사'],
 ['EXPANDED-REVIEW.md','추가 후보·판단 보완','새 후보와 다봄·GAU 반복 협업 보완'],
 ['FOLIO-AUDIT.md','폴리오·사업장 조사','14개 기본 비교 후보와 추가 업체 검토'],
 ['RANKING.md','공통 채점과 순위','13개 후보의 배점·항목별 근거'],
 ['SEARCH-LOG.md','조사 경로와 진행 기록','매체·협회·설계자·업체·기업정보 조사 경로']
];
const docId=f=>f.toLowerCase().replace(/\.md$/,''),docUrl=f=>'./records/'+docId(f)+'.html';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const redact=s=>String(s??'').replace(/0?1[016789][- .]?\d{3,4}[- .]?\d{4}/g,'[연락처 생략]').replace(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/g,'[이메일 생략]').replace(/경수님/g,'발주자');
const unique=a=>[...new Set(a)];
const safeLink=u=>{try{const x=new URL(u);return x.protocol==='https:'?x.href:'#';}catch{return '#';}};
fs.mkdirSync(DIR+'/records',{recursive:true});
const entries=roster.entries.map(e=>{
 const b=base.candidates.find(x=>x.id===e.id),r=ranking.candidates.find(x=>x.id===e.id),p=portfolio.profiles.find(x=>x.id===e.id),x=expanded.sections.find(x=>x.id===e.id);
 const sources=[...(e.sources||[]),...(p?.sources||[]),...(r?.sources||[]),...(x?.sources||[]),...(b?.projects||[]).map(y=>[y.sourceLabel||y.name,y.source])].filter(s=>Array.isArray(s)&&safeLink(s[1])!=='#');
 const works=e.works||p?.works?.map(w=>w[0])||b?.projects?.map(w=>w.name)||[];
 return {...e,name:e.name||b?.name,main:['ia','gau','dabom'].includes(e.id),scored:!!r,score:r?.total??null,rank:r?.rank??null,points:r?.points||[],works:unique(works),sources:sources.filter((s,i,a)=>a.findIndex(q=>q[1]===s[1])===i),records:e.records};
});
assert.equal(entries.length,24);assert.equal(unique(entries.map(e=>e.id)).length,24);assert.equal(entries.filter(e=>e.scored).length,13);
for(const e of entries){assert(e.name&&e.summary&&e.records.length);for(const f of e.records){assert(DOCS.some(x=>x[0]===f));assert(fs.existsSync(path.join(ROOT,f)));}if(e.scored)assert.equal(e.points.reduce((a,b)=>a+b,0),e.score);}
const stats={total:entries.length,others:entries.filter(e=>!e.main).length,scored:entries.filter(e=>e.scored).length,additional:entries.filter(e=>!e.scored).length,documents:DOCS.length,sourcePeriod:roster.sourcePeriod};
const data={version:roster.version,updated:roster.updated,counting:roster.counting,stats,entries,documents:DOCS.map(([file,title,description])=>({file,title,description,url:docUrl(file)}))};
const head=(title,css='./research.css')=>`<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#173d35"><title>${esc(title)} | 제주집 시공사 선정</title><link rel="stylesheet" href="${css}"></head><body><a class="skip" href="#content">본문으로 바로가기</a>`;
const nav=(home='../',research='./')=>`<header class="top"><div class="wrap mast"><a class="brand" href="${home}">⌂ <span>제주집 시공사 선정<small>평가 순위 · 포트폴리오</small></span></a><nav aria-label="주요 메뉴"><a href="${home}">선정 비교</a><a href="${research}" aria-current="page">전체 업체 조사</a></nav></div></header>`;
const footer='<footer class="wrap"><b>제주집 시공사 선정</b><span>조사 기록 '+roster.sourcePeriod+' · 화면 정리 '+roster.updated+'</span></footer>';
const chip=(text,cl='')=>`<span class="chip ${cl}">${esc(text)}</span>`;
const cards=entries.map((e,i)=>`<article class="candidate" id="${e.id}" data-id="${e.id}" data-main="${e.main}" data-scored="${e.scored}" data-category="${esc(e.category)}"><div class="card-top"><div>${chip(e.category,e.main?'main':'')}${chip(e.tag,'subtle')}<h2>${esc(e.name)}</h2></div><span class="entry-no">${String(i+1).padStart(2,'0')}</span></div><p class="summary">${esc(e.summary)}</p><div class="card-meta"><span>${e.scored?'공통 채점 <b>'+e.score+'점</b>':'추가·탐색 기록'}</span><span>조사 문서 ${e.records.length}종${e.main?' · <a href="../?company='+e.id+'#portfolio">메인 사진 보기 →</a>':''}</span></div><details><summary>검토한 사례와 근거 <span>＋</span></summary><div class="detail">${e.works.length?'<h3>검토한 사례</h3><ul>'+e.works.map(w=>'<li>'+esc(w)+'</li>').join('')+'</ul>':'<p class="muted">상호·업종·자료 연결을 살펴본 탐색 기록입니다.</p>'}${e.scored?'<h3>기존 공통 채점</h3><p class="score-detail">포트폴리오 '+e.points[0]+' / 제주 기반 '+e.points[1]+' / RC 대응 '+e.points[2]+' / 도급 책임 '+e.points[3]+' / 성능·거주 기록 '+e.points[4]+'</p>':''}<h3>관련 조사 문서</h3><div class="source-links">${e.records.map(f=>'<a href="'+docUrl(f)+'">'+esc(DOCS.find(d=>d[0]===f)[1])+' →</a>').join('')}</div>${e.sources.length?'<h3>기록된 원문 출처</h3><div class="external-sources">'+e.sources.map(([label,url])=>'<a href="'+esc(safeLink(url))+'" target="_blank" rel="noopener noreferrer">'+esc(redact(label))+' ↗</a>').join('')+'</div>':''}</div></details></article>`).join('');
const docs=DOCS.map(([file,title,desc],i)=>`<a class="doc-card" href="${docUrl(file)}"><span>0${i+1} / 조사 문서</span><h3>${title}</h3><p>${desc}</p><b>이 페이지에서 읽기 →</b></a>`).join('');
let html=head('전체 업체 조사')+nav()+`<main id="content" class="wrap"><section class="hero"><p class="eyebrow">전체 조사 기록</p><h1>24개 업체·협업팀을<br>비교한 과정입니다.</h1><p class="lede">메인에 보이는 세 곳만 조사한 것이 아닙니다.<br>전체 후보의 실적·지역 기반·구조를 살펴본 뒤, 현재 평가 순위와 비교 조건에 따라 메인 포트폴리오를 정리했습니다.</p><div class="stats"><div><strong>24<small>개</small></strong><span>전체 업체·협업팀</span></div><div><strong>13<small>개</small></strong><span>공통 기준 채점</span></div><div><strong>11<small>개</small></strong><span>추가·탐색·참고</span></div><div><strong>8<small>종</small></strong><span>누적 조사 문서</span></div></div><p class="count-note">업체·협업팀별 조사 항목입니다. 하백·이아, 브라운트리·JD 공동 실적은 각각 한 묶음으로 세었습니다. 추가·탐색 기록은 공통 채점과 구분했습니다.</p></section><section class="process"><h2>어떻게 조사했는가</h2><div><p><b>01 · 폭넓게 찾기</b><span>건축 매체 · 패시브협회 · 건축명장 · 업체 사이트</span></p><p><b>02 · 실제 사례 연결</b><span>설계자·시공사 표기 · 구조·용도 · 반복 협업·도급범위</span></p><p><b>03 · 같은 기준으로 비교</b><span>13개 공통 채점 · 폴리오·사업장 추가 대조 · 후보 보완</span></p></div></section><section id="companies"><div class="section-head"><div><h2>전체 업체 목록</h2><p>업체별 요약을 보고, 세부 사례와 조사 문서를 펼쳐보세요.</p></div><a class="text-link" href="#documents">조사 문서 8종 ↓</a></div><div class="toolbar"><div class="filters" role="group" aria-label="업체 보기 범위"><button type="button" data-filter="all" aria-pressed="true">전체 24</button><button type="button" data-filter="other" aria-pressed="false">메인 이외 21</button><button type="button" data-filter="scored" aria-pressed="false">공통 채점 13</button><button type="button" data-filter="additional" aria-pressed="false">추가·탐색 11</button></div><label><span class="sr-only">업체명·사례·구조 검색</span><input id="query" type="search" placeholder="업체명·사례·구조 검색" autocomplete="off"></label></div><div class="result"><span id="result" role="status" aria-live="polite">23 / 24개 조사 항목</span><button type="button" id="expand">세부 내용 모두 펼치기</button></div><div id="candidate-grid" class="candidate-grid">${cards}</div><div id="empty" hidden><h3>검색 결과가 없습니다.</h3><button type="button" id="reset">검색·필터 초기화</button></div><details class="counting"><summary>집계·점수 표시 기준</summary><p>${esc(roster.counting)}</p><p>공통 채점은 저장소의 기존 점수 원본을 유지했습니다. 현재 메인에서 제외한 아틀리에의 과거 채점·조사도 여기에 남아 있습니다. 각 기록은 작성 당시 조사 단계의 내용입니다.</p></details></section><section id="documents"><div class="section-head"><div><h2>쌓아온 조사 문서</h2><p>별도 GitHub 화면으로 나가지 않고, 여기에서 이어 읽을 수 있습니다.</p></div></div><div class="doc-grid">${docs}</div></section><section class="return"><div><h2>포트폴리오로 돌아가기</h2><p>전체 조사에 이어 현재 메인에서 소개하는 업체의 시공 사례를 비교합니다.</p></div><a href="../">선정 비교 메인 →</a></section></main>`+footer+`<script type="application/json" id="research-data">${JSON.stringify(data).replace(/</g,'\\u003c')}</script><script src="./research.js" defer></script></body></html>`;
fs.writeFileSync(DIR+'/index.html',html);fs.writeFileSync(DIR+'/catalog.json',JSON.stringify(data,null,2));
// Safe, lightweight rendering of archived Markdown; source files are never changed.
function inline(s){return esc(redact(s)).replace(/\[([^\]]+)\]\(([^\s]+)\)/g,(_m,label,url)=>{let href='#';if(/^https:\/\//.test(url))href=url;else if(DOCS.some(d=>d[0]===url))href='./'+docId(url)+'.html';return '<a href="'+href+'"'+(href.startsWith('https:')?' target="_blank" rel="noopener noreferrer"':'')+'>'+label+'</a>';}).replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>').replace(/`([^`]+)`/g,'<code>$1</code>');}
function markdown(s){
 const lines=s.split(/\r?\n/);let out='',paragraph=[];
 const flush=()=>{if(paragraph.length){out+='<p>'+inline(paragraph.join(' '))+'</p>';paragraph=[];}};
 for(let i=0;i<lines.length;i++){
  const line=lines[i];
  if(/^\s*\|/.test(line)){flush();const table=[];while(i<lines.length&&/^\s*\|/.test(lines[i]))table.push(lines[i++]);i--;const row=l=>l.trim().replace(/^\||\|$/g,'').split('|').map(x=>x.trim());const first=row(table[0]);out+='<div class="table-wrap" tabindex="0"><table><thead><tr>'+first.map(c=>'<th>'+inline(c)+'</th>').join('')+'</tr></thead><tbody>'+table.slice(1).filter(l=>!/^\s*\|?[\s:|\-]+$/.test(l)).map(l=>'<tr>'+row(l).map(c=>'<td>'+inline(c)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';continue;}
  const h=line.match(/^(#{1,6})\s+(.+)/);if(h){flush();const level=Math.min(h[1].length+1,6);out+='<h'+level+'>'+inline(h[2])+'</h'+level+'>';continue;}
  if(/^\s*[-*]\s+/.test(line)||/^\s*\d+\.\s+/.test(line)){flush();out+='<p class="record-item">'+inline(line.replace(/^\s*[-*]\s+/,'• '))+'</p>';continue;}
  if(!line.trim()){flush();continue;}paragraph.push(line);
 }flush();return out;
}
for(const [file,title,desc] of DOCS){
 let raw=fs.readFileSync(path.join(ROOT,file),'utf8');
 if(file==='RESEARCH.md')raw=raw.replace(/## 현재 설계[\s\S]*?(?=\n## )/,'')+'\n\n## 전문공종 참고 조사\n'+base.extras.filter(x=>x[0]==='골조업체와 총괄 시공사 구분').map(x=>x[1]+'\n\n[공식 회사 소개]('+x[2]+')').join('\n');
 const page=head(title,'../research.css')+nav('../../','../')+`<main id="content" class="wrap record"><a class="back" href="../#documents">← 전체 조사 문서</a><p class="eyebrow">기존 조사 기록 · ${roster.sourcePeriod}</p><h1>${title}</h1><p class="lede">${desc}</p><p class="count-note">자료에 기재된 작성 당시 검토 기록입니다. 연락처·이메일과 기초 문서의 현장 설계조건은 화면에서 생략했습니다.</p><article class="record-body">${markdown(raw)}</article><a class="back bottom" href="../#documents">← 전체 조사 문서로 돌아가기</a></main>`+footer+'</body></html>';
 fs.writeFileSync(DIR+'/records/'+docId(file)+'.html',page);
}
// Idempotent additions to the main page; all 178 image paths remain untouched.
for(const rel of ['index.html','public-portfolio.html','site-v3/published/index.html']){
 const file=path.join(ROOT,rel);if(!fs.existsSync(file))continue;let s=fs.readFileSync(file,'utf8');
 const before=s.match(/<script type="application\/json" id="site-data">([\s\S]*?)<\/script>/)?.[1];
 const prefix=rel.startsWith('site-v3/')?'../../research/':'./research/';
 s=s.replace(/<!--research-start-->[\s\S]*?<!--research-end-->/g,'').replace(/<a class="research-nav"[^>]*>[\s\S]*?<\/a>/g,'');
 s=s.replace('</nav>','<a class="research-nav" href="'+prefix+'">전체 업체 조사</a></nav>');
 const banner=`<!--research-start--><style>.research-strip{margin:20px 0 26px;border:1px solid #d4ded0;background:#edf1e7;border-radius:14px;padding:23px 24px;display:flex;gap:25px;align-items:center;justify-content:space-between}.research-strip h2{font-size:20px;margin:0 0 6px;line-height:1.45;letter-spacing:-.5px}.research-strip p{font-size:13px;margin:0;color:#566b61}.research-strip a{flex-shrink:0;display:block;background:#173d35;color:#fff;padding:13px 18px;border-radius:9px;text-decoration:none;font-size:13px;font-weight:700}.research-stats{display:flex;gap:20px;flex-wrap:wrap;margin-top:13px;font-size:12px;color:#53685d}.research-stats b{color:#173d35;font-size:16px;margin-right:3px}header .research-nav{color:#173d35;font-weight:750}@media(max-width:700px){.research-strip{display:block;padding:20px;margin:17px 0 22px}.research-strip h2{font-size:19px}.research-strip a{margin-top:17px;text-align:center}.research-strip p{font-size:12px}.research-stats{gap:15px}.mast{flex-wrap:wrap;padding-top:12px;padding-bottom:12px}header nav{flex-wrap:wrap;gap:12px}header nav a{font-size:12px}header .brand{font-size:15px}}@media print{.research-strip a,header .research-nav{display:none}}</style><section class="research-strip" aria-label="전체 조사 범위"><div><h2>24개 업체·협업팀을 살펴본 조사 기록</h2><p>전체 조사에서 현재 비교 조건과 평가 순위에 따라 메인 포트폴리오를 먼저 정리했습니다.</p><div class="research-stats"><span><b>13개</b> 공통 기준 채점</span><span><b>11개</b> 추가·탐색·참고</span><span><b>8종</b> 조사 문서</span></div></div><a href="${prefix}">전체 조사 · 다른 21개 업체 보기 →</a></section><!--research-end-->`;
 s=s.replace(/<div class="notice">[\s\S]*?<\/div>/,'<div class="notice"><b>현재 평가 순위에 따라 시공사를 비교합니다.</b> 포트폴리오와 같은 도면 기준의 견적, 공사 일정, 현장소장을 함께 비교합니다.</div>');
 s=s.replace(/<p class="summary">[\s\S]*?<\/p>/,'<p class="summary">전체 조사 24개 업체·협업팀 · 현재 메인 3개 업체 / 17개 프로젝트 / 178개 이미지</p>');
 s=s.replace('<section class="company-grid"',banner+'<section class="company-grid"');
 assert.equal(s.match(/<script type="application\/json" id="site-data">([\s\S]*?)<\/script>/)?.[1],before);
 assert(!s.includes('중에서 선정합니다.'));assert(s.includes(prefix));fs.writeFileSync(file,s);
}
console.log('RESEARCH_LIBRARY '+JSON.stringify(stats));
module.exports={data,stats};
