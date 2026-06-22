import DocsHint from './components/DocsHint.vue'

// Make the globally-registered DocsHint component known to the template type-checker.
declare module 'vue' {
  interface GlobalComponents {
    DocsHint: typeof DocsHint
  }
}

export {}
