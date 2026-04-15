import { computed, ref } from 'vue';
import { defineStore } from 'pinia';

import { getStoredToken, login as loginRequest, persistToken } from '@/services/api';

export const useAuthStore = defineStore('auth', () => {
  const token = ref('');
  const userId = ref('');
  const role = ref('');
  const ready = ref(false);
  const pendingPath = ref('/app/workspace/chat');

  const isAuthenticated = computed(() => Boolean(token.value && userId.value && role.value));

  function restore() {
    if (ready.value) return;
    const stored = getStoredToken();
    if (stored) {
      token.value = stored;
      const storedUser = window.localStorage.getItem('noi-agent-user-id') || '';
      const storedRole = window.localStorage.getItem('noi-agent-role') || '';
      userId.value = storedUser;
      role.value = storedRole;
    }
    ready.value = true;
  }

  async function login(credentials) {
    const result = await loginRequest(credentials);
    token.value = result.token;
    userId.value = result.user_id;
    role.value = result.role;
    persistToken(result.token);
    window.localStorage.setItem('noi-agent-user-id', result.user_id);
    window.localStorage.setItem('noi-agent-role', result.role);
    return result;
  }

  function logout() {
    token.value = '';
    userId.value = '';
    role.value = '';
    persistToken('');
    window.localStorage.removeItem('noi-agent-user-id');
    window.localStorage.removeItem('noi-agent-role');
  }

  function setPendingPath(path) {
    pendingPath.value = path;
  }

  return {
    token,
    userId,
    role,
    ready,
    pendingPath,
    isAuthenticated,
    restore,
    login,
    logout,
    setPendingPath,
  };
});
