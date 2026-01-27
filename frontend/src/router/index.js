import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Feed from '../views/Feed.vue'

const routes = [
    {
        path: '/',
        name: 'Feed',
        component: Feed,
        meta: { layout: 'normal' }
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { layout: 'normal', requiresAuth: true }
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { layout: 'normal' }
    },

    {
        path: '/organizations',
        name: 'Organizations',
        component: () => import('../views/Organizations.vue'),
        meta: { layout: 'normal' }
    },
    {
        path: '/organizations/create',
        name: 'CreateOrganization',
        component: () => import('../views/CreateOrganization.vue'),
        meta: { layout: 'normal' }
    },
    {
        path: '/events',
        name: 'Events',
        component: () => import('../views/Events.vue'),
        meta: { layout: 'normal' }
    },
    {
        path: '/events/create',
        name: 'CreateEvent',
        component: () => import('../views/CreateEvent.vue'),
        meta: { layout: 'normal' }
    },
    {
        path: '/events/:id/edit',
        name: 'EventEdit',
        component: () => import('../views/EventEdit.vue'),
        meta: { layout: 'normal' }
    },
    {
        path: '/profile',
        name: 'Profile',
        component: () => import('../views/UserProfileView.vue'),
        meta: { layout: 'normal' }
    },
    {
        path: '/users/:id',
        name: 'UserProfile',
        component: () => import('../views/UserProfileView.vue'),
        meta: { layout: 'normal' }
    },
    {
        path: '/organizations/:id',
        name: 'OrganizationView',
        component: () => import('../views/OrganizationView.vue'),
        meta: { layout: 'normal' }
    },
    {
        path: '/organizations/:id/edit',
        name: 'OrganizationEdit',
        component: () => import('../views/OrganizationEdit.vue'),
        meta: { layout: 'normal' }
    },
    {
        path: '/organizations/:id/members',
        name: 'OrganizationMembers',
        component: () => import('../views/OrganizationMembers.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/organizations/:id/tags',
        name: 'OrganizationTags',
        component: () => import('../views/OrganizationTags.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/organizations/:id/groups',
        name: 'OrganizationGroups',
        component: () => import('../views/OrganizationGroups.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/subscriptions',
        name: 'Subscriptions',
        component: () => import('../views/SubscriptionsView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/events/:id',
        name: 'EventView',
        component: () => import('../views/EventView.vue'),
        meta: { layout: 'normal' }
    },
    {
        path: '/countdown/:id',
        name: 'EventCountdown',
        component: () => import('../views/EventCountdown.vue'),
        meta: { layout: 'none' }
    },
    {
        path: '/approval-requests',
        name: 'ApprovalRequests',
        component: () => import('../views/ApprovalRequests.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/admin/users',
        name: 'AdminUsers',
        component: () => import('../views/AdminUsers.vue'),
        meta: { layout: 'normal', requiresAuth: true }
    },
    {
        path: '/my-events',
        name: 'MyEvents',
        component: () => import('../views/MyEvents.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/walldisplay',
        name: 'WallDisplay',
        component: () => import('../views/WallDisplayView.vue'),
        meta: { layout: 'none' }
    },
    {
        path: '/admin/tags',
        name: 'AdminTags',
        component: () => import('../views/AdminTags.vue'),
        meta: { layout: 'normal', requiresAuth: true }
    },
    {
        path: '/consent/:shortId',
        name: 'ShortLinkConsent',
        component: () => import('../views/ShortLinkConsent.vue'),
        meta: { layout: 'normal' }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('auth_token')
    const isAuthenticated = !!token

    // Public routes that anyone can access
    const publicRoutes = ['/login', '/', '/events', '/organizations', '/walldisplay']
    // Also allow organization and event detail pages, and countdown
    const isPublicDetailPage = (
        (to.path.match(/^\/(organizations|events)\/[^/]+$/) && !to.path.endsWith('/edit')) ||
        to.path.match(/^\/countdown\/[^/]+$/)
    )

    if (publicRoutes.includes(to.path) || isPublicDetailPage) {
        // If authenticated and trying to access login, redirect to dashboard
        if (isAuthenticated && to.path === '/login') {
            next('/dashboard')
        } else {
            next()
        }
        return
    }

    // Protected routes - require authentication
    if (!isAuthenticated) {
        // Store target path for redirect after login
        localStorage.setItem('auth_redirect_url', to.fullPath)
        next('/login')
    } else {
        next()
    }
})

export default router
