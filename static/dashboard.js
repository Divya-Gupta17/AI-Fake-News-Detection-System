const newsContainer = document.getElementById('newsContainer');
const btnLogout = document.getElementById('btnLogout');
const btnSavePrefs = document.getElementById('btnSavePrefs');
const btnRefresh = document.getElementById('btnRefresh');
const topicsInput = document.getElementById('topics');
const sourcesInput = document.getElementById('sources');
const typeSel = document.getElementById('type');
const prefMsg = document.getElementById('prefMsg');

async function api(path, opts={}){
  const res = await fetch(path, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...opts
  });
  return { ok: res.ok, json: await res.json() };
}

async function loadPrefs(){
  const { ok, json } = await api('/user/preferences');
  if (!ok) return;
  topicsInput.value = (json.topics || []).join(', ');
  sourcesInput.value = (json.sources || []).join(', ');
  typeSel.value = json.type || 'all';
}

async function savePrefs(){
  const body = {
    topics: topicsInput.value.split(',').map(s => s.trim()).filter(Boolean),
    sources: sourcesInput.value.split(',').map(s => s.trim()).filter(Boolean),
    type: typeSel.value
  };
  const { ok, json } = await api('/user/preferences', { method:'PUT', body: JSON.stringify(body) });
  prefMsg.textContent = json.message || (ok ? 'Saved' : 'Failed');
  // reload news after saving
  loadNews();
}

async function loadNews(){
  newsContainer.innerHTML = 'Loading...';
  const { ok, json } = await api('/news');
  if (!ok) { newsContainer.textContent = '❌ Error loading news'; return; }
  renderNews(json);
}

function renderNews(list){
  newsContainer.innerHTML = list.map(n => {
    const conf = Number(n.confidence || 0).toFixed(2);
    const predClass = n.prediction === 'Real' ? 'green' : 'red';
    const factLine = n.fact_check ? 
      `<p class="fact">🔎 <a target="_blank" href="${n.fact_check.link}">${escapeHtml(n.fact_check.title)}</a><br><small>${escapeHtml(n.fact_check.snippet || '')}</small></p>`
      : '';
    const full = escapeHtml(n.content || n.description || '');
    return `
      <article class="news-card">
        <h3>${escapeHtml(n.title || '')}</h3>
        <div class="meta">
          <span>${escapeHtml(n.source || '')}</span>
          <a href="${n.url}" target="_blank">Open</a>
        </div>
        <div class="tags">
          <span class="tag ${predClass}">${n.prediction}</span>
          <span class="tag">conf: ${conf}</span>
          ${n.fact_check ? '<span class="tag green">verified</span>' : ''}
        </div>
        ${n.summary ? `<p class="summary">${escapeHtml(n.summary)}</p>` : ''}
        ${full ? `
          <button class="toggle" onclick="toggleFull(this)">Read full article</button>
          <div class="full">${full}</div>
        ` : ''}
        ${factLine}
      </article>
    `;
  }).join('');
}

function toggleFull(btn){
  const full = btn.nextElementSibling;
  const showing = full.style.display === 'block';
  full.style.display = showing ? 'none' : 'block';
  btn.textContent = showing ? 'Read full article' : 'Hide full article';
}

function escapeHtml(str){
  return (str || '').replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[s]));
}

btnLogout.onclick = async () => {
  await api('/logout', { method:'POST' });
  window.location = '/';
};
btnSavePrefs.onclick = savePrefs;
btnRefresh.onclick = loadNews;

// initial load
loadPrefs().then(loadNews);

// auto refresh every 5 minutes
setInterval(loadNews, 5 * 60 * 1000);
