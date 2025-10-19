// Admin Dashboard JavaScript

// Update server time
function updateServerTime() {
    const timeElement = document.getElementById('server-time');
    if (timeElement) {
        const now = new Date();
        timeElement.textContent = now.toLocaleString('ko-KR');
    }
}

// Update every second
setInterval(updateServerTime, 1000);

// Console log for debugging
console.log('WebSocket Admin Dashboard loaded');

