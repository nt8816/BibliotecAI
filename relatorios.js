checkAuth();

function criarCard(titulo, valor, icone, borda, texto) {
  return `
    <div class="card bg-white rounded-xl p-6 shadow-md border-l-4 ${borda}">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-semibold text-gray-700">${titulo}</h2>
          <p class="text-3xl font-bold ${texto}">${valor}</p>
        </div>
        <i class="fas ${icone} ${texto} text-3xl"></i>
      </div>
    </div>
  `;
}

function renderCards(metrics) {
  const cardsContainer = document.getElementById('cards-container');
  cardsContainer.innerHTML = `
    ${criarCard('Total de Livros', metrics.totalLivros, 'fa-book', 'border-green-600', 'text-green-700')}
    ${criarCard('Total de Usuários', metrics.totalUsuarios, 'fa-users', 'border-blue-600', 'text-blue-700')}
    ${criarCard('Alunos', metrics.totalAlunos, 'fa-user-graduate', 'border-yellow-500', 'text-yellow-600')}
    ${criarCard('Professores', metrics.totalProfessores, 'fa-chalkboard-teacher', 'border-indigo-600', 'text-indigo-700')}
    ${criarCard('Pendências', metrics.totalPendencias, 'fa-exclamation-triangle', 'border-red-600', 'text-red-700')}
  `;
}

function renderTabelaPendencias(pendentes) {
  const tbody = document.getElementById('pendencias-list');
  tbody.innerHTML = '';

  if (!pendentes.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-gray-500">Nenhuma pendência encontrada.</td></tr>';
    return;
  }

  pendentes.forEach((p) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="py-2 px-4">${p.nome}</td>
      <td class="py-2 px-4">${p.tipo}</td>
      <td class="py-2 px-4">${p.telefone || '—'}</td>
      <td class="py-2 px-4">${p.livro}</td>
      <td class="py-2 px-4">${p.dias} dia(s)</td>
    `;
    tbody.appendChild(tr);
  });
}

function calcularDiasAtraso(dataDevolucaoPrevista) {
  const hoje = new Date();
  const limite = new Date(dataDevolucaoPrevista);
  const diffMs = hoje.setHours(0, 0, 0, 0) - limite.setHours(0, 0, 0, 0);
  return Math.max(0, Math.floor(diffMs / (1000 * 60 * 60 * 24)));
}

async function loadRelatorio() {
  try {
    const [livrosRes, usuariosRes, emprestimosRes] = await Promise.all([
      apiRequest('/api/livros'),
      apiRequest('/api/usuarios'),
      apiRequest('/api/emprestimos')
    ]);

    if (!livrosRes || !usuariosRes || !emprestimosRes) {
      return;
    }

    const [livros, usuarios, emprestimos] = await Promise.all([
      livrosRes.json(),
      usuariosRes.json(),
      emprestimosRes.json()
    ]);

    const usuariosComuns = usuarios.filter((u) => u.tipo !== 'Gestor');
    const pendentes = emprestimos
      .filter((emp) => emp.status === 'ativo' && calcularDiasAtraso(emp.data_devolucao_prevista) > 0)
      .map((emp) => ({
        nome: emp.usuario_nome,
        tipo: emp.usuario_tipo,
        telefone: emp.usuario_telefone,
        livro: emp.livro_titulo,
        dias: calcularDiasAtraso(emp.data_devolucao_prevista)
      }));

    renderCards({
      totalLivros: livros.length,
      totalUsuarios: usuariosComuns.length,
      totalAlunos: usuariosComuns.filter((u) => u.tipo === 'Aluno').length,
      totalProfessores: usuariosComuns.filter((u) => u.tipo === 'Professor').length,
      totalPendencias: pendentes.length
    });

    renderTabelaPendencias(pendentes);
  } catch (error) {
    console.error('Erro ao gerar relatórios:', error);
  }
}

async function gerarPDF() {
  const { jsPDF } = window.jspdf;
  const relatorio = document.getElementById('relatorio-container');

  const pdf = new jsPDF('p', 'mm', 'a4');
  const canvas = await html2canvas(relatorio, {
    scale: 2,
    useCORS: true,
    backgroundColor: '#ffffff'
  });

  const imgData = canvas.toDataURL('image/png');
  const imgWidth = 190;
  const imgHeight = (canvas.height * imgWidth) / canvas.width;

  pdf.addImage(imgData, 'PNG', 10, 10, imgWidth, imgHeight);
  pdf.save(`Relatorio_BibliotecAI_${new Date().toLocaleDateString('pt-BR')}.pdf`);
}

document.getElementById('btn-pdf').addEventListener('click', gerarPDF);
loadRelatorio();
