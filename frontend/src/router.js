import { createRouter, createWebHistory } from 'vue-router'

const LibraryViewSimple = () => import('@/views/LibraryViewSimple.vue')
const MangaDetailView = () => import('@/views/MangaDetailView.vue')
const MangaReaderView = () => import('@/views/MangaReaderView.vue')
const SettingsView = () => import('@/views/SettingsView.vue')
const ManualView = () => import('@/views/ManualView.vue')

const LibrarySetup = () => import('@/components/LibrarySetup.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: '/library'
  },
  {
    path: '/library',
    name: 'Library',
    component: LibraryViewSimple,
    meta: {
      title: 'Library - Ohara'
    }
  },
  {
    path: '/setup',
    name: 'Setup',
    component: LibrarySetup,
    meta: {
      title: 'Configure Library - Ohara'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
    meta: {
      title: 'Settings - Ohara'
    }
  },
  {
    path: '/manual',
    name: 'Manual',
    component: ManualView,
    meta: {
      title: 'User Manual - Ohara'
    }
  },
  {
    path: '/manga/:id',
    name: 'MangaDetail',
    component: MangaDetailView,
    meta: {
      title: 'Manga Details - Ohara'
    }
  },
  {
    path: '/manga/:mangaId/chapter/:chapterId',
    name: 'MangaReader',
    component: MangaReaderView,
    meta: {
      title: 'Reader - Ohara'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {

  if (to.meta.title) {
    document.title = to.meta.title
  }

  next()
})

export default router
