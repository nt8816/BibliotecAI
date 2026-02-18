checkAuth();

const usuario = getUserInfo();
if (usuario) {
  const nomeGestor = document.querySelector('.sidebar-text .font-bold');
  if (nomeGestor) {
    nomeGestor.textContent = usuario.nome || 'Gestor';
  }
}

function formatRelativeDate(dateString) {
  const date = new Date(dateString);
  const diffHours = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60));

  if (diffHours < 1) {
    return 'agora há pouco';
  }
  if (diffHours < 24) {
    return `há ${diffHours} hora${diffHours > 1 ? 's' : ''}`;
  }

  const diffDays = Math.floor(diffHours / 24);
  return `há ${diffDays} dia${diffDays > 1 ? 's' : ''}`;
}

function renderRecentActivities(emprestimos) {
  const list = document.getElementById('recent-activities');
  if (!list) {
    return;
  }

  const recentes = emprestimos.slice(0, 5);

  if (!recentes.length) {
    list.innerHTML = '<li class="text-gray-500">Ainda não há atividades registradas.</li>';
    return;
  }

  list.innerHTML = recentes.map((emp, idx) => {
    const isLast = idx === recentes.length - 1;
    const status = emp.status === 'devolvido' ? '📗 Devolução registrada' : '📘 Novo empréstimo';
    const message = `${status}: <b>${emp.livro_titulo}</b> para <b>${emp.usuario_nome}</b>`;
    const timeRef = formatRelativeDate(emp.data_emprestimo);

    return `
      <li class="flex justify-between items-center ${!isLast ? 'border-b pb-2' : ''}">
        <span>${message}</span>
        <span class="text-sm text-gray-500">${timeRef}</span>
      </li>
    `;
  }).join('');
}

async function loadStats() {
  try {
    const [statsResponse, emprestimosResponse] = await Promise.all([
      apiRequest('/api/stats'),
      apiRequest('/api/emprestimos')
    ]);

    if (!statsResponse || !emprestimosResponse) {
      return;
    }

    const stats = await statsResponse.json();
    const emprestimos = await emprestimosResponse.json();

    document.querySelectorAll('.card p')[0].textContent = stats.total_livros;
    document.querySelectorAll('.card p')[1].textContent = stats.total_usuarios;
    document.querySelectorAll('.card p')[2].textContent = stats.leituras_ativas;
    document.querySelectorAll('.card p')[3].textContent = stats.alertas;

    renderRecentActivities(emprestimos);
  } catch (error) {
    console.error('Erro ao carregar estatísticas:', error);
  }
}

loadStats();
