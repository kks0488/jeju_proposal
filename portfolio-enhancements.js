'use strict';
// Additive UI enhancement: the existing document, project URLs and reports remain compatible.
const baseCompanies = renderCompanies;
renderCompanies = function () {
  baseCompanies();
  document.querySelectorAll('.company-card').forEach((card, i) => {
    const c = DATA.companies[i];
    card.dataset.companyId = c.id;
    card.querySelector('.rank').textContent = c.id === 'atelier' ? '추가 비교' : '주요 비교';
    card.querySelector('.score-meta').textContent = '기존 점수순 ' + label(c);
    if (c.id === 'dabom') card.querySelector('.company-location').classList.add('warn');
  });
};
function photoStrip(p, modal = false) {
  const bar = document.createElement('div');
  bar.className = modal ? 'photo-strip modal-strip' : 'photo-strip';
  bar.setAttribute('role', 'group');
  bar.setAttribute('aria-label', p.name + ' 사진 선택');
  p.photos.forEach((photo, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'photo-thumb';
    button.setAttribute('aria-label', p.name + ' 사진 ' + (index + 1) + ' 확대');
    if (modal) button.setAttribute('aria-pressed', String(index === photoIndex));
    const img = document.createElement('img');
    img.src = photoURL(p, index);
    img.alt = photo.caption;
    img.loading = 'lazy';
    img.decoding = 'async';
    img.addEventListener('error', () => { img.hidden = true; button.classList.add('thumb-error'); });
    const number = document.createElement('span');
    number.textContent = index + 1;
    button.append(img, number);
    button.addEventListener('click', () => {
      if (modal) {
        photoIndex = index;
        renderModal();
        document.querySelector('.modal-strip [aria-pressed="true"]')?.focus();
      } else openProject(p.id, button, index);
    });
    bar.append(button);
  });
  return bar;
}
const baseProjects = renderProjects;
renderProjects = function () {
  baseProjects();
  document.querySelectorAll('#projects .project').forEach(card => {
    const id = card.querySelector('[data-project]')?.dataset.project;
    const p = DATA.projects.find(p => p.id === id);
    if (!p) return;
    card.dataset.projectId = p.id;
    if (p.photos.length) {
      card.querySelector('.project-image').after(photoStrip(p));
      const credit = document.createElement('p');
      credit.className = 'card-photo-credit';
      credit.textContent = p.photos[0].credit;
      card.querySelector('.photo-strip').after(credit);
    }
  });
  const photographic = DATA.projects.filter(p => p.photos.length).length;
  $('#total-label').textContent = DATA.projects.length + '개 프로젝트 · 사진 ' + DATA.projects.reduce((s,p)=>s+p.photos.length,0) + '장';
  document.getElementById('photo-coverage').textContent = photographic + '개 프로젝트는 이 페이지에서 사진을 볼 수 있습니다. 사진 미확보 사례는 임의 이미지로 채우지 않고 원문을 남겼습니다.';
};
const baseOpenProject = openProject;
openProject = function (id, opener, index = 0) {
  baseOpenProject(id, opener);
  if (selected && Number.isInteger(index) && index > 0 && index < selected.photos.length) {
    photoIndex = index;
    renderModal();
  }
};
const baseModal = renderModal;
renderModal = function () {
  baseModal();
  if (!selected?.photos.length) return;
  $('#detail-body .modal-content').before(photoStrip(selected, true));
  const stage = $('#detail-body .modal-photo');
  let start = null;
  stage.addEventListener('touchstart', e => {
    if (e.touches.length === 1) start = [e.touches[0].clientX, e.touches[0].clientY];
  }, {passive:true});
  stage.addEventListener('touchend', e => {
    if (!start || !e.changedTouches.length) return;
    const dx = e.changedTouches[0].clientX - start[0];
    const dy = e.changedTouches[0].clientY - start[1];
    start = null;
    if (Math.abs(dx) > 55 && Math.abs(dy) < 70) changePhoto(dx < 0 ? 1 : -1);
  }, {passive:true});
};
const baseComparison = renderComparison;
renderComparison = function () {
  baseComparison();
  $('#comparison thead').innerHTML = '<tr><th scope="col">비교 기준</th>' + DATA.companies.map(c=>'<th scope="col">'+esc(c.short)+'</th>').join('') + '</tr>';
};
window.dispatchEvent(new Event('portfolio:ready'));
