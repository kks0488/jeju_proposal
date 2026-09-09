'use strict';
const cards = [...document.querySelectorAll('.candidate')];
document.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-filter]').forEach(item => {
    item.classList.toggle('active', item === button);
    item.setAttribute('aria-pressed', String(item === button));
  });
  let count = 0;
  cards.forEach(card => {
    card.hidden = button.dataset.filter !== '전체' && card.dataset.group !== button.dataset.filter;
    if (!card.hidden) count++;
  });
  document.getElementById('result-count').textContent = `${count}개 업체·협업팀`;
}));
document.getElementById('copy').addEventListener('click', async () => {
  const field = document.getElementById('inquiry');
  const status = document.getElementById('copy-status');
  try { await navigator.clipboard.writeText(field.value); status.textContent = '복사했습니다.'; }
  catch { field.focus(); field.select(); status.textContent = '문안을 선택했습니다. 기기의 복사 기능을 이용해 주세요.'; }
});
let printState;
window.addEventListener('beforeprint', () => {
  if (printState) return;
  const details = [...document.querySelectorAll('details')];
  printState = { details: details.map(x => [x, x.open]), cards: cards.map(x => [x, x.hidden]) };
  details.forEach(x => { x.open = true; }); cards.forEach(x => { x.hidden = false; });
});
window.addEventListener('afterprint', () => {
  if (!printState) return;
  printState.details.forEach(([x, open]) => { x.open = open; });
  printState.cards.forEach(([x, hidden]) => { x.hidden = hidden; }); printState = undefined;
});
document.getElementById('print').addEventListener('click', () => window.print());
const referenceImage = document.querySelector('.reference img');
referenceImage.addEventListener('error', () => {
  referenceImage.hidden = true;
  const note = document.createElement('p'); note.textContent = '이미지가 표시되지 않으면 출처에서 사례 사진을 확인해 주세요.';
  referenceImage.parentElement.append(note);
});
