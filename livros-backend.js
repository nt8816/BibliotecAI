checkAuth();

const modal = document.getElementById("modal-livro");
const btnAdd = document.getElementById("btn-add-livro");
const closeModalBtn = modal.querySelector(".close");
const formLivro = document.getElementById("form-livro");
const livrosList = document.getElementById("livros-list");
const modalTitle = document.getElementById("modal-title");
const livroIdInput = document.getElementById("livro-id");

let livros = [];
let editIndex = null;
let editingLivroId = null;

async function loadLivros() {
  try {
    const response = await apiRequest('/api/livros');
    livros = await response.json();
    renderTable();
  } catch (error) {
    console.error('Erro ao carregar livros:', error);
    alert('Erro ao carregar livros');
  }
}

btnAdd.onclick = () => {
  modal.classList.add("show");
  modalTitle.textContent = "Adicionar Livro";
  formLivro.reset();
  editIndex = null;
  editingLivroId = null;
};

closeModalBtn.onclick = () => modal.classList.remove("show");
window.onclick = (e) => { if(e.target == modal) modal.classList.remove("show"); }

formLivro.onsubmit = async function(e){
  e.preventDefault();
  
  const livro = {
    area: document.getElementById("area").value,
    tombo: document.getElementById("tombo").value,
    autor: document.getElementById("autor").value,
    titulo: document.getElementById("titulo").value,
    vol: document.getElementById("vol").value,
    edicao: document.getElementById("edicao").value,
    local: document.getElementById("local").value,
    editora: document.getElementById("editora").value,
    ano: parseInt(document.getElementById("ano").value)
  };

  try {
    if(editingLivroId !== null){
      await apiRequest(`/api/livros/${editingLivroId}`, {
        method: 'PUT',
        body: JSON.stringify(livro)
      });
    } else {
      await apiRequest('/api/livros', {
        method: 'POST',
        body: JSON.stringify(livro)
      });
    }

    await loadLivros();
    modal.classList.remove("show");
    formLivro.reset();
  } catch (error) {
    console.error('Erro ao salvar livro:', error);
    alert('Erro ao salvar livro');
  }
}

function renderTable(){
  livrosList.innerHTML = "";
  livros.forEach((livro, index) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td class="py-2 px-4">${livro.area}</td>
      <td class="py-2 px-4">${livro.id}</td>
      <td class="py-2 px-4">${livro.tombo}</td>
      <td class="py-2 px-4">${livro.autor}</td>
      <td class="py-2 px-4">${livro.titulo}</td>
      <td class="py-2 px-4">${livro.vol || ''}</td>
      <td class="py-2 px-4">${livro.edicao || ''}</td>
      <td class="py-2 px-4">${livro.local || ''}</td>
      <td class="py-2 px-4">${livro.editora}</td>
      <td class="py-2 px-4">${livro.ano}</td>
      <td class="py-2 px-4 text-center">
        <button class="text-blue-600 hover:text-blue-800" onclick="editLivro(${index})"><i class='fas fa-pen'></i></button>
        <button class="text-red-600 hover:text-red-800 ml-3" onclick="deleteLivro(${index})"><i class='fas fa-trash'></i></button>
      </td>
    `;
    livrosList.appendChild(row);
  });
}

function editLivro(index){
  const livro = livros[index];
  livroIdInput.value = livro.id;
  document.getElementById("area").value = livro.area;
  document.getElementById("tombo").value = livro.tombo;
  document.getElementById("autor").value = livro.autor;
  document.getElementById("titulo").value = livro.titulo;
  document.getElementById("vol").value = livro.vol || '';
  document.getElementById("edicao").value = livro.edicao || '';
  document.getElementById("local").value = livro.local || '';
  document.getElementById("editora").value = livro.editora;
  document.getElementById("ano").value = livro.ano;

  editIndex = index;
  editingLivroId = livro.id;
  modalTitle.textContent = "Editar Livro";
  modal.classList.add("show");
}

async function deleteLivro(index){
  if(!confirm("Deseja realmente deletar este livro?")){
    return;
  }
  
  const livroId = livros[index].id;
  
  try {
    await apiRequest(`/api/livros/${livroId}`, {
      method: 'DELETE'
    });
    await loadLivros();
  } catch (error) {
    console.error('Erro ao deletar livro:', error);
    alert('Erro ao deletar livro');
  }
}

loadLivros();
