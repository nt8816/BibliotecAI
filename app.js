const API_URL = '';

function getToken() {
  return localStorage.getItem('token');
}

function checkAuth() {
  const token = getToken();
  if (!token) {
    window.location.href = 'login.html';
    return false;
  }
  return true;
}

async function apiRequest(endpoint, options = {}) {
  const token = getToken();
  const defaultHeaders = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers
    }
  };

  try {
    const response = await fetch(`${API_URL}${endpoint}`, config);
    
    if (response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('usuario');
      window.location.href = 'login.html';
      return null;
    }

    return response;
  } catch (error) {
    console.error('API Request Error:', error);
    throw error;
  }
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('usuario');
  window.location.href = 'login.html';
}

function getUserInfo() {
  const userStr = localStorage.getItem('usuario');
  return userStr ? JSON.parse(userStr) : null;
}
