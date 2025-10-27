document.addEventListener('DOMContentLoaded', function() {
  const sidebar = document.querySelector('.sidebar nav ul');
  if (!sidebar) return;
  
  const hasEmprestimos = Array.from(sidebar.querySelectorAll('a')).some(a => a.href.includes('emprestimos.html'));
  
  if (!hasEmprestimos) {
    const usuariosLi = Array.from(sidebar.querySelectorAll('li')).find(li => {
      const a = li.querySelector('a');
      return a && a.href.includes('usuarios.html');
    });
    
    if (usuariosLi) {
      const emprestimosLi = document.createElement('li');
      const currentPage = window.location.pathname.split('/').pop();
      const activeClass = currentPage === 'emprestimos.html' ? 'bg-green-600 active' : '';
      
      emprestimosLi.innerHTML = `
        <a href="emprestimos.html" class="sidebar-item flex items-center p-3 rounded-lg hover:bg-green-600 transition-all ${activeClass}">
          <i class="fas fa-handshake text-xl w-8"></i>
          <span class="sidebar-text">Empréstimos</span>
        </a>
      `;
      
      usuariosLi.after(emprestimosLi);
    }
  }
});
