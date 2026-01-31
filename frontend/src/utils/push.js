
import api from './api';



function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

export async function askPermissionAndSubscribe() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.log('Push messaging not supported');
        return false;
    }

    // check if already prompted
    if (localStorage.getItem('push_prompted') === 'true' && Notification.permission !== 'granted') {
        return false; // Don't annoy if they previously denied or ignored? 
        // Actually 'push_prompted' implies we asked. If denied, browser blocks anyway.
        // If default, we can ask again maybe? But sticking to requirement "for the first time".
    }

    if (Notification.permission === 'granted') {
        return subscribeUserToPush();
    }
    // Ask permission
    const permission = await Notification.requestPermission();
    localStorage.setItem('push_prompted', 'true');

    if (permission === 'granted') {
        return subscribeUserToPush();
    }
    return false;
}

export async function subscribeUserToPush() {
    try {
        // Fetch public key from backend
        const keyResponse = await api.get('/notifications/vapid-public-key');
        const vapidPublicKey = keyResponse.data.public_key;

        if (!vapidPublicKey) {
            console.warn("VAPID Public Key not found");
            return false;
        }

        // Ensure SW is ready
        const registration = await navigator.serviceWorker.ready;

        // Check existing subscription
        let subscription = await registration.pushManager.getSubscription();

        if (!subscription) {
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
            });
        }

        // Send to server (update token)
        await api.post('/notifications/subscribe', {
            endpoint: subscription.endpoint,
            keys: JSON.stringify(subscription.toJSON().keys)
        });

        console.log('Push subscription verified/updated');
        return true;

    } catch (error) {
        console.error('Failed to subscribe user: ', error);
        return false;
    }
}

export async function unsubscribeUserFromPush() {
    try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();

        if (subscription) {
            // Unsubscribe on server
            await api.delete(`/notifications/unsubscribe?endpoint=${encodeURIComponent(subscription.endpoint)}`);

            // Unsubscribe locally
            await subscription.unsubscribe();
            console.log('Push notification unsubscribed');
            return true;
        }
        return false;
    } catch (error) {
        console.error('Failed to unsubscribe user: ', error);
        return false;
    }
}
