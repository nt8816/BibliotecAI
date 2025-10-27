checkAuth();

const usuario = getUserInfo();
if (usuario) {
  const nomeGestor = document.querySelector('.sidebar-text .font-bold');
  if (nomeGestor) {
    nomeGestor.textContent = usuario.nome || 'Gestor';
  }
}

async function loadStats() {
  try {
    const response = await apiRequest('/api/stats');
    const stats = await response.json();
    
    document.querySelectorAll('.card p')[0].textContent = stats.total_livros;
    document.querySelectorAll('.card p')[1].textContent = stats.total_usuarios;
    document.querySelectorAll('.card p')[2].textContent = stats.leituras_ativas;
    document.querySelectorAll('.card p')[3].textContent = stats.alertas;
  } catch (error) {
    console.error('Erro ao carregar estatísticas:', error);
  }
}

loadStats();
