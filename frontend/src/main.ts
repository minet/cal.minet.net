import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import DocsHint from './components/DocsHint.vue'

const app = createApp(App)

// Globally available so any element can be linked to a documentation section:
//   <DocsHint path="/bienvenue" search="barre latérale">…</DocsHint>
app.component('DocsHint', DocsHint)

app.use(router).mount('#app')

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration)
      })
      .catch((registrationError: unknown) => {
        console.log('SW registration failed: ', registrationError)
      })
  })
}
