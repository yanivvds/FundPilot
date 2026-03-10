import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { vannaDesignTokens } from '../styles/vanna-design-tokens.js';

const AGENT_NAME = 'Finn';

@customElement('vanna-message')
export class VannaMessage extends LitElement {
  static styles = [
    vannaDesignTokens,
    css`
      :host {
        display: block;
        padding: 0 var(--vanna-space-2);
        margin-bottom: var(--vanna-space-5);
        font-family: var(--vanna-font-family-default);
        animation: fade-in-up 0.25s ease-out;
      }

      /* Outer column: meta header + bubble */
      .message-wrapper {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }

      .message-wrapper.assistant { align-items: flex-start; }
      .message-wrapper.user      { align-items: flex-end; }

      /* Meta row: icon · name · time */
      .message-meta {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 0 4px;
      }

      .message-wrapper.user .message-meta {
        flex-direction: row-reverse;
      }

      /* Agent icon – small rounded square */
      .meta-agent-icon {
        width: 22px;
        height: 22px;
        border-radius: 5px;
        object-fit: cover;
        display: block;
        flex-shrink: 0;
      }

      /* User avatar image */
      .meta-user-icon {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        object-fit: cover;
        display: block;
        flex-shrink: 0;
      }

      .meta-name {
        font-size: 12px;
        font-weight: 600;
        color: var(--vanna-foreground-default);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 200px;
      }

      .meta-time {
        font-size: 11px;
        color: var(--vanna-foreground-dimmest);
        font-weight: 400;
        white-space: nowrap;
      }

      :host(:last-of-type) {
        margin-bottom: 0;
      }

      @keyframes fade-in-up {
        from {
          opacity: 0;
          transform: translateY(16px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .message {
        position: relative;
        padding: var(--vanna-space-4) var(--vanna-space-5);
        border-radius: var(--vanna-chat-bubble-radius);
        word-wrap: break-word;
        line-height: 1.6;
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-2);
        max-width: min(85%, 580px);
        transition: transform var(--vanna-duration-200) ease, box-shadow var(--vanna-duration-200) ease;
        backdrop-filter: blur(8px);
      }

      .message.assistant {
        background: var(--vanna-background-root);
        border: 1px solid var(--vanna-outline-dimmer);
        color: var(--vanna-foreground-default);
        box-shadow: var(--vanna-shadow-sm);
        border-radius: var(--vanna-chat-bubble-radius) var(--vanna-chat-bubble-radius) var(--vanna-chat-bubble-radius) var(--vanna-space-2);
      }

      .message.user {
        max-width: min(80%, 500px);
        background: #141218;
        color: white;
        box-shadow: var(--vanna-shadow-md);
        border-radius: var(--vanna-chat-bubble-radius) var(--vanna-chat-bubble-radius) var(--vanna-space-2) var(--vanna-chat-bubble-radius);
        border: none;
      }

      .message:hover {
        transform: translateY(-1px);
      }

      .message.assistant:hover {
        box-shadow: var(--vanna-shadow-md);
        border-color: var(--vanna-outline-hover);
      }

      .message.user:hover {
        box-shadow: var(--vanna-shadow-lg);
      }

      .message-content {
        margin: 0;
        font-size: 15px;
        letter-spacing: 0.01em;
        white-space: pre-wrap;
        font-weight: 400;
      }

      .message-content a {
        color: inherit;
        font-weight: 500;
        text-decoration: underline;
        text-decoration-thickness: 1px;
        text-underline-offset: 2px;
        opacity: 0.9;
      }

      .message-content code {
        font-family: var(--vanna-font-family-mono);
        background: var(--vanna-background-higher);
        padding: 2px 6px;
        border-radius: var(--vanna-border-radius-sm);
        font-size: 13px;
        border: 1px solid var(--vanna-outline-dimmer);
      }

      .message.user .message-content code {
        background: rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.3);
      }

      :host([theme="dark"]) .message.assistant {
        background: var(--vanna-background-higher);
        border: 1px solid var(--vanna-outline-default);
        color: var(--vanna-foreground-default);
        box-shadow: var(--vanna-shadow-md);
      }

      :host([theme="dark"]) .message.assistant .message-content code {
        background: var(--vanna-background-highest);
        border-color: var(--vanna-outline-default);
      }

      :host([theme="dark"]) .message.user {
        background: #1E1B26;
        color: white;
        box-shadow: var(--vanna-shadow-lg);
      }

      :host([theme="dark"]) .message.user .message-content code {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.25);
      }

      @media (max-width: 600px) {
        .message {
          max-width: 100%;
        }

        .message.user {
          max-width: 100%;
        }
      }
    `
  ];

  @property() content = '';
  @property() type: 'user' | 'assistant' = 'user';
  @property({ type: Number }) timestamp = Date.now();
  @property({ reflect: true }) theme = 'light';
  @property() senderLabel = '';

  private formatTimestamp(ts: number): string {
    return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  render() {
    return html`
      <div class="message-wrapper ${this.type}">
        <div class="message-meta">
          ${this.type === 'assistant'
            ? html`
                <img class="meta-agent-icon" src="/img/app-icon-512.png" alt="" width="22" height="22">
                <span class="meta-name">${AGENT_NAME}</span>
              `
            : html`
                <img class="meta-user-icon" src="/img/avatar-placeholder.png" alt="" width="22" height="22">
                <span class="meta-name">Jij</span>
              `
          }
          <span class="meta-time">${this.formatTimestamp(this.timestamp)}</span>
        </div>
        <div class="message ${this.type}">
          <div class="message-content">${this.content}</div>
        </div>
      </div>
    `;
  }
}
