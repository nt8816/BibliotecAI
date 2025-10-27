checkAuth();

const modalU = document.getElementById("modal-usuario");
const btnAddU = document.getElementById("btn-add-usuario");
const closeU = modalU.querySelector(".close");
const formU = document.getElementById("form-usuario");
const usuariosList = document.getElementById("usuarios-list");
const modalTitleU = document.getElementById("modal-title");
const tipoSelect = document.getElementById("tipo");
const extraFields = document.getElementById("extra-fields");
const usuarioIdInput = document.getElementById("usuario-id");

let usuarios = [];
let editIndexU = null;
let editingUsuarioId = null;

async function loadUsuarios() {
  try {
    const response = await apiRequest('/api/usuarios');
    usuarios = await response.json();
    renderUsuarios();
  } catch (error) {
    console.error('Erro ao carregar usuários:', error);
    alert('Erro ao carregar usuários');
  }
}

btnAddU.onclick = () => {
  modalU.classList.add("show");
  formU.reset();
  extraFields.innerHTML = "";
  modalTitleU.textContent = "Adicionar Usuário";
  editIndexU = null;
  editingUsuarioId = null;
};

closeU.onclick = () => modalU.classList.remove("show");
window.onclick = (e) => { if (e.target == modalU) modalU.classList.remove("show"); };

tipoSelect.addEventListener("change", () => {
  const tipo = tipoSelect.value;
  extraFields.innerHTML = "";

  if (tipo === "Aluno") {
    extraFields.innerHTML = `
      <div>
        <label class="font-semibold">Matrícula:</label>
        <input type="text" id="matricula" class="w-full border rounded-lg p-2" required>
      </div>
      <div>
        <label class="font-semibold">Turma:</label>
        <input type="text" id="turma" class="w-full border rounded-lg p-2" required>
      </div>
      <div>
        <label class="font-semibold">Telefone:</label>
        <input type="text" id="telefone" class="w-full border rounded-lg p-2" required>
      </div>
      <div>
        <label class="font-semibold">E-mail (para login):</label>
        <input type="email" id="email" class="w-full border rounded-lg p-2" required>
      </div>
    `;
  } else if (tipo === "Professor") {
    extraFields.innerHTML = `
      <div>
        <label class="font-semibold">CPF:</label>
        <input type="text" id="cpf" class="w-full border rounded-lg p-2" required>
      </div>
      <div>
        <label class="font-semibold">Telefone:</label>
        <input type="text" id="telefone" class="w-full border rounded-lg p-2" required>
      </div>
      <div>
        <label class="font-semibold">E-mail (para login):</label>
        <input type="email" id="email" class="w-full border rounded-lg p-2" required>
      </div>
    `;
  }
});

formU.onsubmit = async function(e) {
  e.preventDefault();
  const tipo = tipoSelect.value;

  const usuario = {
    nome: document.getElementById("nome").value,
    tipo,
    matricula: tipo === "Aluno" ? document.getElementById("matricula").value : "",
    turma: tipo === "Aluno" ? document.getElementById("turma").value : "",
    telefone: (tipo === "Aluno" || tipo === "Professor") ? document.getElementById("telefone").value : "",
    cpf: tipo === "Professor" ? document.getElementById("cpf").value : "",
    email: (tipo === "Aluno" || tipo === "Professor") ? document.getElementById("email").value : "",
  };

  try {
    if (editingUsuarioId !== null) {
      await apiRequest(`/api/usuarios/${editingUsuarioId}`, {
        method: 'PUT',
        body: JSON.stringify(usuario)
      });
    } else {
      await apiRequest('/api/usuarios', {
        method: 'POST',
        body: JSON.stringify(usuario)
      });
    }

    await loadUsuarios();
    modalU.classList.remove("show");
    formU.reset();
    extraFields.innerHTML = "";
  } catch (error) {
    console.error('Erro ao salvar usuário:', error);
    alert('Erro ao salvar usuário');
  }
};

function renderUsuarios() {
  usuariosList.innerHTML = "";

  usuarios.forEach((u, index) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td class="py-2 px-4">${u.nome}</td>
      <td class="py-2 px-4">${u.tipo}</td>
      <td class="py-2 px-4">${u.tipo === "Aluno" ? u.matricula : u.tipo === "Professor" ? u.cpf : "-"}</td>
      <td class="py-2 px-4">${u.tipo === "Aluno" ? u.turma : "-"}</td>
      <td class="py-2 px-4">${u.telefone || "-"}</td>
      <td class="py-2 px-4 text-center">
        <button class="text-blue-600 hover:text-blue-800" onclick="editUsuario(${index})"><i class="fas fa-pen"></i></button>
        <button class="text-red-600 hover:text-red-800 ml-3" onclick="deleteUsuario(${index})"><i class="fas fa-trash"></i></button>
      </td>
    `;
    usuariosList.appendChild(row);
  });
}

function editUsuario(index) {
  const u = usuarios[index];
  usuarioIdInput.value = u.id;
  document.getElementById("nome").value = u.nome;
  tipoSelect.value = u.tipo;
  tipoSelect.dispatchEvent(new Event("change"));

  setTimeout(() => {
    if (u.tipo === "Aluno") {
      document.getElementById("matricula").value = u.matricula;
      document.getElementById("turma").value = u.turma;
      document.getElementById("telefone").value = u.telefone;
      if (document.getElementById("email")) {
        document.getElementById("email").value = u.email || '';
      }
    } else if (u.tipo === "Professor") {
      document.getElementById("cpf").value = u.cpf;
      document.getElementById("telefone").value = u.telefone;
      if (document.getElementById("email")) {
        document.getElementById("email").value = u.email || '';
      }
    }
  }, 50);

  modalTitleU.textContent = "Editar Usuário";
  editIndexU = index;
  editingUsuarioId = u.id;
  modalU.classList.add("show");
}

async function deleteUsuario(index) {
  if (!confirm("Deseja realmente deletar este usuário?")) {
    return;
  }
  
  const usuarioId = usuarios[index].id;
  
  try {
    await apiRequest(`/api/usuarios/${usuarioId}`, {
      method: 'DELETE'
    });
    await loadUsuarios();
  } catch (error) {
    console.error('Erro ao deletar usuário:', error);
    alert('Erro ao deletar usuário');
  }
}

loadUsuarios();
