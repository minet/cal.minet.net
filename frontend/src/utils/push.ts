import { api } from '../api'

function urlBase64ToUint8Array(base64String: string): ArrayBuffer {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')

  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray.buffer as ArrayBuffer
}

export async function askPermissionAndSubscribe(): Promise<boolean> {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    console.log('Push messaging not supported')
    return false
  }

  if (
    localStorage.getItem('push_prompted') === 'true' &&
    Notification.permission !== 'granted'
  ) {
    return false
  }

  if (Notification.permission === 'granted') {
    return subscribeUserToPush()
  }

  const permission = await Notification.requestPermission()
  localStorage.setItem('push_prompted', 'true')

  if (permission === 'granted') {
    return subscribeUserToPush()
  }
  return false
}

export async function subscribeUserToPush(): Promise<boolean> {
  try {
    const { public_key: vapidPublicKey } = await api.notifications.get_vapid_public_key()

    if (!vapidPublicKey) {
      console.warn('VAPID Public Key not found')
      return false
    }

    const registration = await navigator.serviceWorker.ready
    let subscription = await registration.pushManager.getSubscription()

    if (!subscription) {
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
      })
    }

    await api.notifications.subscribe_push({
      endpoint: subscription.endpoint,
      keys: JSON.stringify(subscription.toJSON().keys),
    })

    console.log('Push subscription verified/updated')
    return true
  } catch (error) {
    console.error('Failed to subscribe user: ', error)
    return false
  }
}

export async function unsubscribeUserFromPush(): Promise<boolean> {
  try {
    const registration = await navigator.serviceWorker.ready
    const subscription = await registration.pushManager.getSubscription()

    if (subscription) {
      await api.notifications.unsubscribe_push(subscription.endpoint)
      await subscription.unsubscribe()
      console.log('Push notification unsubscribed')
      return true
    }
    return false
  } catch (error) {
    console.error('Failed to unsubscribe user: ', error)
    return false
  }
}
