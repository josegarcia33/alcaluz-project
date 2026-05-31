
// ── PAGE ROUTING ──
const pageNames = {
  luminarias:'Luminarias',  'reg-lum':'Registrar luminaria','reg-consumo':'Registrar consumo',
  consumo:'Consumo',reportes:'Reportes',usuarios:'Usuarios'
};
function showPage(name, navEl) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  if (navEl) navEl.classList.add('active');
}