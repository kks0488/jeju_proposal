'use strict';
// Editorial update only. Original research and every image file remain unchanged.
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path');
const ROOT=path.resolve(__dirname,'..'),DIR=path.join(__dirname,'published'),title='제주집 시공사 선정';
const profiles={
 ia:{tagline:'건축가 설계 주택과 외장·실내 마감 사례',strength:'솔비나무집·화분·연안재를 중심으로 큰 창, 외장 재료와 실내 마감을 비교합니다.',question:'우리 도면 기준 공사비, 현장소장, 창호·석재·지붕 공종팀과 마감 견본을 상담합니다.'},
 gau:{tagline:'단층 RC 주택과 마당·중정의 연결',strength:'호미·하천리 H·남원 항심당을 중심으로 단층 주택과 외부공간의 연결을 비교합니다.',question:'건축·토목의 견적 범위, 현장소장, 외부공간 공정과 착공 일정을 상담합니다.'},
 dabom:{tagline:'작은 RC 주택과 에이루트의 반복 협업 사례',strength:'저지 오름 아래·용담 심양재를 중심으로 RC 주택을, 나머지 사례에서 실내외 마감을 비교합니다.',question:'기존 현장 방문, 담당 소장, 우리 도면 기준 견적과 공정·보수 일정을 상담합니다.'}
};
const focus={
 solbinamujip:'큰 창, 낮은 마당과 연결되는 실내, 외장과 바닥의 마감선을 봅니다.',
 hwabun:'문·창 프레임과 천장선, 단층 주택의 외부 통로 마감을 봅니다.',
 yeonanjae:'경사지의 레벨과 지붕, 외부 통로와 실내가 이어지는 구성을 봅니다.',
 jaejaesoso:'여러 동의 배치, 징크·현무암 외장과 객실의 실내 마감을 봅니다.',
 eoheung:'제주 스테이의 건물 배치, 외장과 실내 마감을 봅니다.',
 yeongpyeong:'단독주택과 근린생활시설이 함께 있는 프로젝트의 외장·창호·실내 마감을 봅니다.',
 homi:'단층 RC 주택의 현무암 벽, 큰 창과 중정의 연결을 봅니다.',
 hacheon:'주택·사무실·구옥이 연결된 배치와 목재 문, 목욕채의 타일 마감을 봅니다.',
 got:'노출콘크리트 외장, 처마·곡면·개구부와 숲을 향한 실내 공간을 봅니다.',
 hangsimdang:'RC 주택의 경사지붕, 큰 창과 정원에 면한 입면을 봅니다.',
 woljeong:'두 동의 단층 스테이, 외장과 실내 공간의 구성을 봅니다.',
 ora:'RC 주택의 건축·설비·전기·인테리어 도급 사례입니다.',
 jeoji:'작은 단층 RC 주택의 처마, 큰 창과 외부공간, 실내 마감을 봅니다.',
 simyang:'RC 2층 주택의 중정, 큰 창과 낮은 가로창, 서로 다른 외장 재료를 봅니다.',
 haean:'1층 RC와 2층 목구조가 결합된 주택의 목재 외피, 처마와 마당을 봅니다.',
 sowon:'과수원에 면한 낮은 건물, 큰 창과 주택·티룸·스테이의 실내외 연결을 봅니다.',
 little:'단층 목조 주택과 정원, 처마 아래의 실내외 공간을 봅니다.'
};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const sourceData=JSON.parse(fs.readFileSync(path.join(DIR,'catalog.json'),'utf8'));
assert.deepEqual(sourceData.companies.map(c=>c.id),['ia','gau','dabom']);
const originalImages=sourceData.projects.flatMap(p=>p.photos.map(x=>x.url));
const data=structuredClone(sourceData);data.title=title;data.presentation='selection-20260915';
for(const c of data.companies){Object.assign(c,profiles[c.id]);delete c.pending;}
const creditText=s=>String(s||'').replace(/ · 사진가 (?:원문 미표기|별도 확인|미확인)/g,'').replace(/ · 설계 설계자·참여자 원문 참조/g,'');
for(const p of data.projects){
 p.focus=focus[p.id]||p.focus;delete p.caution;
 // Omit unresolved fields instead of turning them into positive factual assertions.
 for(const key of ['area','period','designer','structure']){
  if(!p[key])continue;
  if(/필드 불일치|미확인|미확보|공식 면적:|정확한|원문 참조|재확인/.test(p[key]))delete p[key];
 }
 if(p.id==='hwabun')p.structure='단층';
 if(p.id==='yeongpyeong')p.structure='지상 2층';
 if(p.id==='yeonanjae')delete p.area;
 if(p.id==='sowon')p.structure='목구조 중심';
 if(p.area)p.area=p.area.replace(/ · 전체 합산 아님/g,'');
 for(const photo of p.photos)photo.credit=creditText(photo.credit);
}
const comparison=data.companies.map(c=>'<article class="comparison"><h3>'+esc(c.short)+'</h3><b>포트폴리오에서 볼 부분</b><p>'+esc(c.strength)+'</p><b>상담할 내용</b><p class="question">'+esc(c.question)+'</p></article>').join('');
const notices='<div class="notice"><b>하백·이아 / GAU / 다봄 중에서 선정합니다.</b> 포트폴리오와 같은 도면 기준의 견적, 공사 일정, 현장소장을 함께 비교합니다.</div>';
function editHTML(html,isTemplate=false){
 html=html.replace(/<title>[\s\S]*?<\/title>/,'<title>'+title+'</title>');
 html=html.replace(/<meta name="description" content="[^"]*">/,'<meta name="description" content="제주집 시공사 선정. 하백·이아, GAU, 다봄의 포트폴리오와 상담 내용을 한곳에서 비교합니다.">');
 html=html.replace(/<a class="brand"[\s\S]*?<\/a>/,'<a class="brand" href="./">⌂ <span>'+title+'<small>하백·이아 · GAU · 다봄</small></span></a>');
 html=html.replace(/<h1>[\s\S]*?<\/h1>/,'<h1>'+title+'</h1>');
 html=html.replace('<p class="eyebrow">단독주택 시공사 선정 준비</p>','<p class="eyebrow">우리 집을 지을 세 업체 비교</p>');
 html=html.replace(/<p class="lede">[\s\S]*?<\/p>/,'<p class="lede">하백·이아, GAU, 다봄의 실제 시공 사례를 보고<br>우리 집을 맡길 업체를 고릅니다.</p>');
 html=html.replace(/<div class="notice">[\s\S]*?<\/div>/,notices);
 html=html.replace(/PROJECT GALLERY/g,'업체별 포트폴리오').replace(/BEYOND THE PHOTOGRAPHS/g,'선정할 때 비교할 내용');
 html=html.replace('프로젝트 사진 둘러보기','포트폴리오 둘러보기').replace('사진 다음에 확인할 것','세 업체 비교와 상담');
 html=html.replace('비교 기준</a>','업체 비교</a>').replace('RC 본체 확인 사례','철근콘크리트(RC)');
 html=html.replace(/<p class="muted">사진은 우리 페이지에 저장된 파일로 열립니다\.<\/p>/,'<p class="muted">사진을 누르면 크게 볼 수 있습니다.</p>');
 html=html.replace('링크 공유 ↗','주소 복사').replace('이 프로젝트 공유 ↗','프로젝트 주소 복사');
 html=html.replace(/<details class="method">[\s\S]*?<\/details>/,'');
 html=html.replace(/<footer class="wrap">[\s\S]*?<\/footer>/,'<footer class="wrap"><p><b>'+title+' · 2026.09.15</b></p><p>사진·도면의 출처와 촬영자는 각 이미지에 표기했습니다.</p></footer>');
 html=html.replace(/<p id="project-caution"><\/p>/,'');
 if(!isTemplate){
  html=html.replace(/<div class="comparison-grid">[\s\S]*?<\/div>/,'<div class="comparison-grid">'+comparison+'</div>');
  for(const p of data.projects){
   const reg=new RegExp('(<article class="project" data-project="'+p.id+'">)([\\s\\S]*?)(</article>)');
   html=html.replace(reg,(_m,start,body,end)=>{
    body=body.replace(/<p class="focus">[\s\S]*?<\/p>/,'<p class="focus">'+esc(p.focus)+'</p>');
    body=body.replace(/<p class="meta">[\s\S]*?<\/p>/,'<p class="meta">'+esc(p.place)+(p.structure?'<br>'+esc(p.structure):'')+'</p>');
    const facts=[['규모',p.area],['기간',p.period],['설계',p.designer],['시공',p.credit]].filter(x=>x[1]&&!/별도 확인|별도 표기|원문 미표기|기존 .*검토|원문 참조/.test(x[1]));
    const links=p.sources.map(([name,url])=>'<a href="'+esc(url)+'" target="_blank" rel="noopener">'+esc(name)+' ↗</a>').join(' ');
    body=body.replace(/<details>[\s\S]*?<\/details>/,'<details><summary>프로젝트 정보 ▾</summary><p>'+facts.map(([label,v])=>'<b>'+label+'</b> '+esc(v)).join('<br>')+'</p>'+links+'</details>');
    body=body.replace('사진 확보 중','오라동 현이네').replace('<p>다른 프로젝트 사진으로 대신하지 않았습니다.</p>','<p>프로젝트 소개</p>').replace('공식 사진을 확보하지 못했습니다.','');
    body=body.replace(/<p class="credit">[\s\S]*?<\/p>/,'<p class="credit">'+esc(p.photos[0]?.credit||'')+'</p>');
    return start+body+end;
   });
  }
  for(const c of data.companies){const old=sourceData.companies.find(x=>x.id===c.id);html=html.replace('<p>'+esc(old.tagline)+'</p>','<p>'+esc(c.tagline)+'</p>');}
  html=html.replace(/<script type="application\/json" id="site-data">[\s\S]*?<\/script>/,'<script type="application/json" id="site-data">'+JSON.stringify(data).replace(/</g,'\\u003c')+'</script>');
  html=html.replace(/<p class="summary">[\s\S]*?<\/p>/,'<p class="summary">3개 업체 · '+data.projects.length+'개 프로젝트 · '+originalImages.length+'개 이미지</p>');
 }
 return html;
}
for(const [file,template] of [[path.join(DIR,'index.html'),false],[path.join(__dirname,'template.html'),true]]){
 if(!fs.existsSync(file))continue;
 fs.writeFileSync(file,editHTML(fs.readFileSync(file,'utf8'),template));
}
for(const file of [path.join(DIR,'app.js'),path.join(__dirname,'app.js')]){
 if(!fs.existsSync(file))continue;
 fs.writeFileSync(file,fs.readFileSync(file,'utf8').replace("$('#project-caution').textContent=project.caution;",''));
}
fs.writeFileSync(path.join(DIR,'catalog.json'),JSON.stringify(data,null,2)+'\n');
// Apply the same view after future media refreshes.
const buildFile=path.join(__dirname,'build.mjs');
if(fs.existsSync(buildFile)){
 let build=fs.readFileSync(buildFile,'utf8');
 if(!build.includes('selection-edit.cjs')){build+="\n// Keep the internal selection view after a media refresh.\nconst {execFileSync}=await import('node:child_process');execFileSync(process.execPath,['site-v3/selection-edit.cjs'],{stdio:'inherit'});\n";fs.writeFileSync(buildFile,build);}
}
for(const rel of ['index.html','public-portfolio.html']){
 const file=path.join(ROOT,rel);if(!fs.existsSync(file))continue;
 let html=fs.readFileSync(file,'utf8');
 if(/site-v3\/published/.test(html)&&html.length<4000){html=html.replace(/<title>[\s\S]*?<\/title>/,'<title>'+title+'</title>');fs.writeFileSync(file,html);}
}
const final=fs.readFileSync(path.join(DIR,'index.html'),'utf8');
assert(final.includes('<title>'+title+'</title>')&&final.includes('<h1>'+title+'</h1>'));
assert(!final.includes('project-caution'));
assert(!/계약 적격 판정 아님|공개자료 기반 검토용|확인을 대신하지|방수.{0,60}검증|아틀리에/.test(final));
assert.deepEqual(data.projects.flatMap(p=>p.photos.map(x=>x.url)),originalImages);
console.log(JSON.stringify({title,companies:data.companies.length,projects:data.projects.length,images:originalImages.length,imagesUnchanged:true,disclaimersRemoved:true,sourceResearchPreserved:true}));
