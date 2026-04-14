// AMOS Brain WebSocket Client (Browser)
// Usage: Include in HTML and connect to ws://neurosyncai.tech/ws

class AMOSWebSocketClient {
    constructor(url = 'ws://neurosyncai.tech:8765') {
        this.url = url;
        this.ws = null;
        this.onStep = null;
        this.onComplete = null;
        this.onError = null;
    }

    connect() {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log('Connected to AMOS Brain');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            if (this.onError) this.onError(error);
        };

        this.ws.onclose = () => {
            console.log('Disconnected from AMOS Brain');
        };
    }

    handleMessage(data) {
        switch(data.type) {
            case 'start':
                console.log('Starting:', data.action);
                break;
            case 'step':
                if (this.onStep) this.onStep(data);
                break;
            case 'analysis':
                console.log('Analysis:', data.step);
                break;
            case 'complete':
                if (this.onComplete) this.onComplete(data);
                break;
            case 'error':
                if (this.onError) this.onError(data.message);
                break;
        }
    }

    think(query, domain = 'general') {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: 'think',
                query: query,
                domain: domain
            }));
        }
    }

    decide(question, options = []) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: 'decide',
                question: question,
                options: options
            }));
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Example usage:
/*
const client = new AMOSWebSocketClient();
client.onStep = (data) => {
    document.getElementById('output').innerHTML += `<p>Step ${data.number}: ${data.content}</p>`;
};
client.onComplete = (data) => {
    document.getElementById('output').innerHTML += `<p><strong>Done!</strong> Confidence: ${data.confidence}</p>`;
};
client.connect();
client.think("Benefits of microservices?");
*/

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AMOSWebSocketClient };
}
