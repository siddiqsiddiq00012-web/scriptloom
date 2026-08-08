import { config } from "../config";

/**
 * Scriptloom Decoupled SSE Progress Stream Service
 */
class ProgressStreamService {
  constructor() {
    this.currentMediaId = null;
    this.listeners = new Set();
    this.connectionState = "DISCONNECTED"; // DISCONNECTED | CONNECTING | CONNECTED | CLOSED
    this.reconnectAttempts = 0;
    this.activeReader = null;
    this.reconnectTimeout = null;
  }

  async connect(mediaId) {
    if (this.currentMediaId === mediaId && (this.connectionState === "CONNECTED" || this.connectionState === "CONNECTING")) {
      return;
    }

    this.disconnect();
    this.currentMediaId = mediaId;
    this.connectionState = "CONNECTING";
    this.notifyListeners({ type: "connection_change", state: "CONNECTING" });

    const url = `${config.apiUrl}/stream/progress/${mediaId}`;

    try {
      const response = await fetch(url, { credentials: "include" });

      // Handle non-2xx responses before consuming the stream
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      this.connectionState = "CONNECTED";
      this.reconnectAttempts = 0;
      this.notifyListeners({ type: "connection_change", state: "CONNECTED" });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      this.activeReader = reader;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop(); // Keep partial line

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith("data: ")) {
            try {
              const payload = JSON.parse(trimmed.slice(6));
              this.notifyListeners({ type: "event", data: payload });
            } catch (err) {
              console.error("Failed to parse SSE payload:", err);
            }
          }
        }
      }
    } catch (err) {
      console.warn("SSE fetch connection error:", err);
      this.connectionState = "DISCONNECTED";
      this.notifyListeners({ type: "connection_change", state: "DISCONNECTED" });

      // Automatically retry connection if not explicitly disconnected by user
      if (this.currentMediaId === mediaId && this.reconnectAttempts < 5) {
        this.reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 16000);
        this.reconnectTimeout = setTimeout(() => this.reconnect(), delay);
      }
    }
  }

  reconnect() {
    if (this.currentMediaId) {
      const mediaId = this.currentMediaId;
      this.disconnect();
      this.connect(mediaId);
    }
  }

  disconnect() {
    if (this.activeReader) {
      try {
        this.activeReader.cancel();
      } catch { /* reader already cancelled */ }
      this.activeReader = null;
    }
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
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
