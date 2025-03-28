document.addEventListener('DOMContentLoaded', () => {
    const statusElement = document.getElementById('status');
    const streamElement = document.getElementById('browser-stream');
    let ws = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;

    function connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        console.log('Attempting to connect to:', wsUrl);
        
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('WebSocket connected');
            statusElement.textContent = 'Connected';
            statusElement.className = 'status connected';
            reconnectAttempts = 0;
        };

        ws.onclose = (event) => {
            console.log('WebSocket closed:', event.code, event.reason);
            statusElement.textContent = 'Disconnected';
            statusElement.className = 'status disconnected';
            
            if (reconnectAttempts < maxReconnectAttempts) {
                reconnectAttempts++;
                console.log(`Reconnecting... Attempt ${reconnectAttempts}/${maxReconnectAttempts}`);
                setTimeout(connect, 5000);
            } else {
                statusElement.textContent = 'Connection failed. Please refresh the page.';
                console.error('Max reconnection attempts reached');
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            statusElement.textContent = 'Error: Connection failed';
            statusElement.className = 'status disconnected';
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('Received message type:', data.type);
                
                if (data.type === 'screenshot') {
                    streamElement.src = `data:image/png;base64,${data.data}`;
                } else if (data.type === 'error') {
                    console.error('Server error:', data.message);
                    statusElement.textContent = 'Error: ' + data.message;
                    statusElement.className = 'status disconnected';
                }
            } catch (error) {
                console.error('Error processing message:', error);
            }
        };
    }

    // Start the connection
    connect();
}); 