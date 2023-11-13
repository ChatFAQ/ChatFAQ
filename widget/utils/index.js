export function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0,
            v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

export function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

export function setCookie(name, value, days) {
    const expirationDate = new Date();
    expirationDate.setTime(expirationDate.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = `${name}=${value};expires=${expirationDate.toUTCString()};path=/`;
}

export function getUserId() {
    const cookieName = 'chatfaq-user-uuid'
    let uuid = getCookie(cookieName);
    if (!uuid) {
        uuid = generateUUID();
        setCookie(cookieName, uuid, 365 * 10); // Save the UUID in cookies for 10 years
    }
    return uuid;
}
