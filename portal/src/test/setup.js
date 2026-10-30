import '@testing-library/jest-dom/vitest'

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

globalThis.ResizeObserver = ResizeObserverMock
globalThis.URL.createObjectURL = () => 'blob:mock-qr'
globalThis.URL.revokeObjectURL = () => {}
