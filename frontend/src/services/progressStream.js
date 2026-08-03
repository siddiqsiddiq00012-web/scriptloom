/**
 * Scriptloom Decoupled SSE Progress Stream Service
 */
class ProgressStreamService {
  constructor() {
    this.eventSource = null;
    this.currentMediaId = null;
    this.listeners = new Set();
    this.connectionState = "DISCONNECTED"; // DISCONNECTED | CONNECTING | CONNECTED | CLOSED
    this.reconnectAttempts = 0;
  }

  connect(mediaId) {
    if (this.eventSource && this.currentMediaId === mediaId) {
      return;
    }

    this.disconnect();
    this.currentMediaId = mediaId;
    this.connectionState = "CONNECTING";

    const url = `/api/v1/stream/progress/${mediaId}`;
    this.eventSource = new EventSource(url);

    this.eventSource.onopen = () => {
      this.connectionState = "CONNECTED";
      this.reconnectAttempts = 0;
      this.notifyListeners({ type: "connection_change", state: "CONNECTED" });
    };

    this.eventSource.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        this.notifyListeners({ type: "event", data: payload });
      } catch (err) {
        console.error("Failed to parse SSE payload:", err);
      }
    };

    this.eventSource.onerror = (err) => {
      console.warn("SSE stream connection error:", err);
      this.connectionState = "DISCONNECTED";
      this.notifyListeners({ type: "connection_change", state: "DISCONNECTED" });

      if (this.reconnectAttempts < 5) {
        this.reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 16000);
        setTimeout(() => this.reconnect(), delay);
      }
    };
  }

  reconnect() {
    if (this.currentMediaId) {
      const mediaId = this.currentMediaId;
      this.disconnect();
      this.connect(mediaId);
    }
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.currentMediaId = null;
    this.connectionState = "DISCONNECTED";
    this.notifyListeners({ type: "connection_change", state: "DISCONNECTED" });
  }

  subscribe(listener) {
    this.listeners.add(listener);
  }

  unsubscribe(listener) {
    this.listeners.delete(listener);
  }

  getConnectionState() {
    return this.connectionState;
  }

  notifyListeners(data) {
    this.listeners.forEach((listener) => {
      try {
        listener(data);
      } catch (err) {
        console.error("Error in SSE listener:", err);
      }
    });
  }
}

export const progressStream = new ProgressStreamService();
