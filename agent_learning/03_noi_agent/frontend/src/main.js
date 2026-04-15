import { createApp } from 'vue';
import { createPinia } from 'pinia';

import App from './App.vue';
import router from './router';
import { setUnauthorizedHandler } from './services/api';
import { useAuthStore } from './stores/auth';
import './styles.css';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
const auth = useAuthStore(pinia);
auth.restore();
setUnauthorizedHandler(() => {
  auth.setPendingPath(router.currentRoute.value.fullPath);
  auth.logout();
});
app.use(router);

router.isReady().finally(() => {
  app.mount('#app');
});
