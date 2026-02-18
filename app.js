const API_URL_STORAGE_KEY = 'api_url';

function normalizeApiUrl(url) {
  return (url || '').trim().replace(/\/$/, '');
}

function getApiUrl() {
  const runtimeApiUrl = normalizeApiUrl(window.BIBLIOTECAI_API_URL || '');
  const savedApiUrl = normalizeApiUrl(localStorage.getItem(API_URL_STORAGE_KEY) || '');

  if (runtimeApiUrl) {
    return runtimeApiUrl;
  }

  if (savedApiUrl) {
    return savedApiUrl;
  }

  return '';
}

function setApiUrl(url) {
  const normalized = normalizeApiUrl(url);

  if (!normalized) {
    localStorage.removeItem(API_URL_STORAGE_KEY);
    return '';
  }

  localStorage.setItem(API_URL_STORAGE_KEY, normalized);
  return normalized;
}

function clearApiUrl() {
  localStorage.removeItem(API_URL_STORAGE_KEY);
}

function buildApiUrl(endpoint) {
  if (/^https?:\/\//i.test(endpoint)) {
    return endpoint;
  }

  return `${getApiUrl()}${endpoint}`;
}

function shouldRetryWithSameOrigin(endpoint) {
  if (/^https?:\/\//i.test(endpoint)) {
    return false;
  }

  return Boolean(getApiUrl());
}

async function fetchWithApiFallback(endpoint, options = {}) {
  const primaryUrl = buildApiUrl(endpoint);

  try {
    return await fetch(primaryUrl, options);
  } catch (error) {
    if (!shouldRetryWithSameOrigin(endpoint)) {
      throw error;
    }

    console.warn('Falha na URL de API configurada, tentando mesma origem:', primaryUrl);
    return fetch(endpoint, options);
  }
}

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
    Authorization: `Bearer ${token}`
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers
    }
  };

  try {
    const response = await fetchWithApiFallback(endpoint, config);

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
