
// ── PAGE ROUTING ──
const pageNames = {
  luminarias:'Luminarias',  'reg-lum':'Registrar luminaria','reg-consumo':'Registrar consumo',
  consumo:'Consumo',reportes:'Reportes',usuarios:'Usuarios'
};
function showPage(name, navEl) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  if (navEl) navEl.classList.add('active');
  const tt = document.getElementById('topbar-title');
  tt.innerHTML = pageNames[name] + ' <span>/ ' + (name.includes('reg') ? 'Formulario' : 'Listado') + '</span>';
}
