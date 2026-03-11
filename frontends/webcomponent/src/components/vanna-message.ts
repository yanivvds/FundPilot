import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
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

      /* Quick reply buttons */
      .quick-replies {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid var(--vanna-outline-dimmer);
      }

      .quick-reply-btn {
        padding: 6px 14px;
        border-radius: 2px;
        border: 1.5px solid #E2DFD8;
        background: #FAFAF8;
        color: #141218;
        font-size: 13px;
        font-weight: 500;
        font-family: var(--vanna-font-family-default);
        cursor: pointer;
        transition: background var(--vanna-duration-150) ease, border-color var(--vanna-duration-150) ease, color var(--vanna-duration-150) ease, transform var(--vanna-duration-100) ease;
        white-space: nowrap;
        line-height: 1.4;
      }

      .quick-reply-btn:hover {
        background: #F0A500;
        border-color: #F0A500;
        color: #141218;
        transform: translateY(-1px);
      }

      .quick-reply-btn:active {
        transform: scale(0.97);
        background: #d4910a;
        border-color: #d4910a;
      }

      :host([theme="dark"]) .quick-reply-btn {
        background: #2A2636;
        border-color: #3A3547;
        color: #E8E4DC;
      }

      :host([theme="dark"]) .quick-reply-btn:hover {
        background: #F0A500;
        border-color: #F0A500;
        color: #141218;
      }

      /* ---- User bubble wrapper + action row ---- */
      .user-bubble-wrapper {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 4px;
      }

      .message-actions {
        display: flex;
        gap: 2px;
        opacity: 0;
        transition: opacity var(--vanna-duration-150) ease;
      }

      .message-wrapper.user:hover .message-actions {
        opacity: 1;
      }

      .action-btn {
        width: 28px;
        height: 28px;
        border: none;
        background: transparent;
        color: var(--vanna-foreground-dimmer);
        cursor: pointer;
        border-radius: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        transition: background var(--vanna-duration-150) ease, color var(--vanna-duration-150) ease;
      }

      .action-btn:hover {
        background: var(--vanna-background-higher);
        color: var(--vanna-foreground-default);
      }

      :host([theme="dark"]) .action-btn:hover {
        background: var(--vanna-background-highest);
      }

      /* Edit mode */
      .message.user.is-editing {
        box-shadow: 0 0 0 2px #F0A500;
        transition: box-shadow var(--vanna-duration-150) ease;
      }

      .edit-textarea {
        width: 100%;
        border: none;
        background: transparent;
        color: white;
        font-size: 15px;
        font-family: var(--vanna-font-family-default);
        line-height: 1.6;
        resize: none;
        padding: 0;
        margin: 0;
        outline: none;
        min-height: 0;
        height: auto;
        overflow: hidden;
        display: block;
        box-sizing: border-box;
        caret-color: #F0A500;
      }

      .edit-hint {
        font-size: 11px;
        color: rgba(255,255,255,0.35);
        margin-top: 6px;
        text-align: right;
        user-select: none;
      }

      .edit-actions {
        display: flex;
        gap: 6px;
        justify-content: flex-end;
        align-items: center;
        margin-top: 4px;
      }

      .edit-action-btn {
        padding: 5px 14px;
        border-radius: 999px;
        border: none;
        font-size: 12px;
        font-weight: 500;
        font-family: var(--vanna-font-family-default);
        cursor: pointer;
        line-height: 1.4;
        transition: background var(--vanna-duration-150) ease, opacity var(--vanna-duration-150) ease;
      }

      .edit-action-btn.send {
        background: #F0A500;
        color: #141218;
        font-weight: 600;
      }

      .edit-action-btn.send:hover {
        background: #d4910a;
      }

      .edit-action-btn.cancel {
        background: transparent;
        color: rgba(255,255,255,0.55);
        border: 1px solid rgba(255,255,255,0.18);
      }

      .edit-action-btn.cancel:hover {
        color: rgba(255,255,255,0.85);
        border-color: rgba(255,255,255,0.35);
      }
    `
  ];

  @property() content = '';
  @property() type: 'user' | 'assistant' = 'user';
  @property({ type: Number }) timestamp = Date.now();
  @property({ reflect: true }) theme = 'light';
  @property() senderLabel = '';

  @state() private _isEditing = false;
  @state() private _editContent = '';
  @state() private _copied = false;
  @state() private _optionsUsed = false;

  private formatTimestamp(ts: number): string {
    return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  private async _copyMessage() {
    try {
      await navigator.clipboard.writeText(this.content);
      this._copied = true;
      setTimeout(() => { this._copied = false; }, 1800);
    } catch (_) {}
  }

  private _startEdit() {
    this._editContent = this.content;
    this._isEditing = true;
    this.updateComplete.then(() => {
      const textarea = this.shadowRoot?.querySelector('.edit-textarea') as HTMLTextAreaElement;
      if (textarea) {
        textarea.style.height = '0';
        textarea.style.height = textarea.scrollHeight + 'px';
        textarea.focus();
        textarea.setSelectionRange(textarea.value.length, textarea.value.length);
      }
    });
  }

  private _cancelEdit() {
    this._isEditing = false;
  }

  private _onEditInput(e: Event) {
    const textarea = e.target as HTMLTextAreaElement;
    this._editContent = textarea.value;
    // Auto-resize
    textarea.style.height = '0';
    textarea.style.height = textarea.scrollHeight + 'px';
  }

  private _onEditKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this._confirmEdit();
    } else if (e.key === 'Escape') {
      this._cancelEdit();
    }
  }

  private _confirmEdit() {
    if (!this._editContent.trim()) return;
    this.dispatchEvent(new CustomEvent('message-resend', {
      detail: {
        content: this._editContent.trim(),
        componentId: this.dataset.componentId
      },
      bubbles: true,
      composed: true
    }));
    this._isEditing = false;
  }

  private _parseContent(): { text: string; options: string[] } {
    const match = this.content.match(/\[KNOPPEN:\s*([^\]]+)\]\s*$/);
    if (!match) return { text: this.content, options: [] };
    const options = match[1].split('|').map(o => o.trim()).filter(Boolean);
    const text = this.content.slice(0, match.index).trimEnd();
    return { text, options };
  }

  private _onQuickReply(option: string) {
    this._optionsUsed = true;
    this.dispatchEvent(new CustomEvent('quick-reply-selected', {
      detail: { option },
      bubbles: true,
      composed: true
    }));
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
        ${this.type === 'user' ? html`
          <div class="user-bubble-wrapper">
            <div class="message user ${this._isEditing ? 'is-editing' : ''}">
              ${this._isEditing ? html`
                <textarea
                  class="edit-textarea"
                  .value=${this._editContent}
                  @input=${this._onEditInput}
                  @keydown=${this._onEditKeydown}
                ></textarea>
                <div class="edit-hint">↵ sturen &nbsp;·&nbsp; Esc annuleer</div>
              ` : html`
                <div class="message-content">${this.content}</div>
              `}
            </div>
            ${this._isEditing ? html`
              <div class="edit-actions">
                <button class="edit-action-btn cancel" @click=${this._cancelEdit}>Annuleer</button>
                <button class="action-btn" @click=${this._copyMessage} title="Kopieer" aria-label="Copy message" style="opacity:1">
                  ${this._copied ? html`
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
                    </svg>
                  ` : html`
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M16 1H4C3 1 2 2 2 3v14h2V3h12V1zm3 4H8C7 5 6 6 6 7v14c0 1 1 2 2 2h11c1 0 2-1 2-2V7c0-1-1-2-2-2zm0 16H8V7h11v14z"/>
                    </svg>
                  `}
                </button>
                <button class="edit-action-btn send" @click=${this._confirmEdit}>Opnieuw sturen</button>
              </div>
            ` : html`
              <div class="message-actions">
                <button class="action-btn" @click=${this._copyMessage} title="Kopieer" aria-label="Copy message">
                  ${this._copied ? html`
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
                    </svg>
                  ` : html`
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M16 1H4C3 1 2 2 2 3v14h2V3h12V1zm3 4H8C7 5 6 6 6 7v14c0 1 1 2 2 2h11c1 0 2-1 2-2V7c0-1-1-2-2-2zm0 16H8V7h11v14z"/>
                    </svg>
                  `}
                </button>
                <button class="action-btn" @click=${this._startEdit} title="Bewerk bericht" aria-label="Edit message">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                  </svg>
                </button>
              </div>
            `}
          </div>
        ` : html`
          ${(() => {
            const { text, options } = this._parseContent();
            return html`
              <div class="message assistant">
                <div class="message-content">${text}</div>
                ${options.length > 0 && !this._optionsUsed ? html`
                  <div class="quick-replies">
                    ${options.map(opt => html`
                      <button class="quick-reply-btn" @click=${() => this._onQuickReply(opt)}>${opt}</button>
                    `)}
                  </div>
                ` : ''}
              </div>
            `;
          })()}
        `}
      </div>
    `;
  }
}
