import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { vannaDesignTokens } from '../styles/vanna-design-tokens.js';
import { VannaApiClient, ChatStreamChunk } from '../services/api-client.js';
import { ComponentManager, RichComponent } from './rich-component-system.js';
import './vanna-status-bar.js';
import './vanna-progress-tracker.js';
import './rich-card.js';
import './rich-task-list.js';
import './rich-progress-bar.js';
import './plotly-chart.js';

@customElement('vanna-chat')
export class VannaChat extends LitElement {
  static styles = [
    vannaDesignTokens,
    css`
      *, *::before, *::after {
        box-sizing: border-box;
      }

      :host {
        display: block;
        font-family: var(--vanna-font-family-default);
        --chat-primary: var(--vanna-accent-primary-default);
        --chat-primary-stronger: var(--vanna-accent-primary-stronger);
        --chat-primary-foreground: rgb(255, 255, 255);
        --chat-accent-soft: var(--vanna-accent-primary-subtle);
        --chat-outline: var(--vanna-outline-default);
        --chat-surface: var(--vanna-background-root);
        --chat-muted: var(--vanna-background-default);
        --chat-muted-stronger: var(--vanna-background-higher);
        max-width: 1600px;
        margin: 0 auto;
        background: var(--vanna-background-root);
        border: 1px solid var(--vanna-outline-dimmer);
        border-radius: var(--vanna-border-radius-2xl);
        box-shadow: var(--vanna-shadow-xl);
        overflow: hidden;
        transition: box-shadow var(--vanna-duration-300) ease, transform var(--vanna-duration-300) ease;
        position: relative;
      }

      :host(:hover) {
        box-shadow: var(--vanna-shadow-lg);
      }

      :host([theme="dark"]) {
        --chat-primary: var(--vanna-accent-primary-default);
        --chat-primary-stronger: var(--vanna-accent-primary-stronger);
        --chat-primary-foreground: rgb(255, 255, 255);
        --chat-accent-soft: var(--vanna-accent-primary-subtle);
        --chat-outline: var(--vanna-outline-default);
        --chat-surface: var(--vanna-background-higher);
        --chat-muted: var(--vanna-background-default);
        --chat-muted-stronger: var(--vanna-background-highest);
        background: var(--vanna-background-higher);
        border-color: var(--vanna-outline-default);
      }

      :host(.maximized) {
        position: fixed;
        top: var(--vanna-space-6);
        left: var(--vanna-space-6);
        right: var(--vanna-space-6);
        bottom: var(--vanna-space-6);
        max-width: none;
        width: auto;
        margin: 0;
        z-index: var(--vanna-z-modal);
        border-radius: var(--vanna-border-radius-xl);
        transform: none;
        box-shadow: var(--vanna-shadow-2xl);
      }

      :host(.maximized):hover {
        transform: none;
      }

      :host(.minimized) {
        position: fixed !important;
        bottom: var(--vanna-space-6) !important;
        right: var(--vanna-space-6) !important;
        width: 64px !important;
        height: 64px !important;
        max-width: none !important;
        margin: 0 !important;
        z-index: var(--vanna-z-modal) !important;
        border-radius: var(--vanna-border-radius-full) !important;
        cursor: pointer !important;
        background: linear-gradient(135deg, var(--chat-primary-stronger), var(--chat-primary)) !important;
        border: 2px solid rgba(255, 255, 255, 0.9) !important;
        box-shadow: var(--vanna-shadow-xl) !important;
        overflow: hidden !important;
      }

      :host(.minimized):hover {
        transform: scale(1.05);
        box-shadow: var(--vanna-shadow-2xl) !important;
      }

      :host(.minimized) .chat-layout {
        display: none;
      }

      .minimized-icon {
        display: none;
      }

      :host(.minimized) .minimized-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        color: var(--chat-primary-foreground);
        font-size: 24px;
        transition: transform var(--vanna-duration-200) ease;
      }

      :host(.minimized) .minimized-icon:hover {
        transform: scale(1.1);
      }

      :host(.minimized) .minimized-icon svg {
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
      }

      .chat-layout {
        display: grid;
        grid-template-columns: minmax(0, 1fr) 360px;
        height: 640px;
        max-height: 82vh;
        background: var(--chat-muted);
      }

      :host([no-header]) .chat-layout {
        height: calc(100vh - 130px);
        max-height: calc(100vh - 130px);
      }

      :host(.maximized) .chat-layout {
        height: calc(100vh - 48px);
        max-height: calc(100vh - 48px);
      }

      .chat-layout.compact {
        grid-template-columns: 1fr;
      }

      .chat-main {
        display: flex;
        flex-direction: column;
        border-right: none;
        background: #FFFFFF;
        min-height: 0;
      }

      :host([theme="dark"]) .chat-main {
        background: var(--vanna-background-root);
      }

      .chat-layout.compact .chat-main {
        border-right: none;
      }

      .chat-header {
        padding: var(--vanna-space-4) var(--vanna-space-6);
        background: #141218;
        border-bottom: none;
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-4);
        color: #FFFFFF;
        position: relative;
        overflow: hidden;
      }

      /* 2px saffron loading bar at top */
      .chat-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: #F0A500;
        pointer-events: none;
      }

      :host([theme="dark"]) .chat-header {
        background: #141218;
      }

      .header-top {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        gap: var(--vanna-space-4);
        width: 100%;
      }

      .header-left {
        display: flex;
        align-items: center;
        gap: var(--vanna-space-4);
        min-width: 0;
        flex: 1;
      }

      .header-top-actions {
        display: inline-flex;
        align-items: center;
        gap: var(--vanna-space-2);
        margin-left: auto;
      }

      .chat-avatar {
        width: 36px;
        height: 36px;
        border-radius: 2px;
        background: #F0A500;
        display: grid;
        place-items: center;
        font-weight: 700;
        font-size: 14px;
        letter-spacing: 0.02em;
        color: #141218;
        border: none;
        overflow: hidden;
        flex-shrink: 0;
      }

      .chat-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
      }

      .header-text {
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-1);
        min-width: 0;
      }

      .chat-title {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: #FFFFFF;
        font-family: var(--vanna-font-family-default);
      }

      .chat-title-logo {
        height: 22px;
        width: auto;
        display: block;
        filter: brightness(0) invert(1);
        object-fit: contain;
      }

      .chat-subtitle {
        font-size: 13px;
        letter-spacing: 0.01em;
        opacity: 0.9;
        font-weight: 400;
      }

      :host([theme="dark"]) .chat-subtitle {
        opacity: 0.78;
      }

      .window-controls {
        display: inline-flex;
        gap: var(--vanna-space-2);
      }

      .window-control-btn {
        width: 28px;
        height: 28px;
        border-radius: 2px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        background: transparent;
        color: rgba(255, 255, 255, 0.6);
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        transition: all var(--vanna-duration-150) ease;
        position: relative;
        overflow: hidden;
      }

      .window-control-btn:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #F0A500;
        border-color: rgba(240, 165, 0, 0.3);
      }

      .window-control-btn:active {
        transform: scale(0.95);
      }

      .window-control-btn svg {
        width: 16px;
        height: 16px;
        transition: transform var(--vanna-duration-150) ease;
      }

      .window-control-btn:hover svg {
        transform: scale(1.1);
      }

      :host([theme="dark"]) .window-control-btn {
        border-color: rgba(255, 255, 255, 0.1);
        background: rgba(255, 255, 255, 0.05);
      }

      :host([theme="dark"]) .window-control-btn:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.25);
      }

      .chat-messages {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        padding: var(--vanna-space-6) var(--vanna-space-6) var(--vanna-space-5);
        background: #FFFFFF;
        scroll-behavior: smooth;
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-4);
        min-height: 0;
        max-height: 100%;
        position: relative;
      }

      .chat-messages::-webkit-scrollbar {
        width: 6px;
      }

      .chat-messages::-webkit-scrollbar-track {
        background: transparent;
      }

      .chat-messages::-webkit-scrollbar-thumb {
        background: var(--vanna-outline-default);
        border-radius: var(--vanna-border-radius-full);
        border: 1px solid var(--vanna-background-root);
      }

      .chat-messages::-webkit-scrollbar-thumb:hover {
        background: var(--vanna-outline-hover);
      }

      :host([theme="dark"]) .chat-messages {
        background: radial-gradient(circle at top, rgba(240, 165, 0, 0.08), transparent 55%), var(--chat-surface);
      }

      :host([theme="dark"]) .chat-messages::-webkit-scrollbar-thumb {
        background: var(--vanna-outline-default);
        border-color: var(--vanna-background-higher);
      }

      /* Scroll indicator when there's content above */
      .chat-messages::before {
        content: '';
        position: sticky;
        top: 0;
        display: block;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--vanna-accent-primary-default), transparent);
        opacity: 0;
        transition: opacity var(--vanna-duration-300) ease;
        z-index: 10;
        margin: 0 var(--vanna-space-4) var(--vanna-space-2);
      }

      .chat-messages.has-scroll::before {
        opacity: 0.5;
      }

      .rich-components-container {
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-4);
      }

      .rich-component-wrapper {
        margin: var(--vanna-space-2) 0;
        animation: fade-in-up 0.3s ease-out;
      }

      .unknown-component {
        background: var(--vanna-background-higher);
        border: 1px solid var(--vanna-outline-default);
        border-radius: var(--vanna-border-radius-md);
        padding: var(--vanna-space-4);
        font-family: var(--vanna-font-family-mono);
        font-size: 12px;
      }

      .unknown-component p {
        margin: 0 0 var(--vanna-space-2) 0;
        color: var(--vanna-foreground-dimmer);
      }

      .unknown-component pre {
        margin: 0;
        color: var(--vanna-foreground-dimmest);
        overflow-x: auto;
      }

      .chat-input-area {
        padding: var(--vanna-space-4) var(--vanna-space-5) var(--vanna-space-5);
        background: #F5F3EF;
        border-top: 1px solid #E2DFD8;
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-3);
        flex-shrink: 0;
      }

      :host([theme="dark"]) .chat-input-area {
        background: #141218;
        border-top-color: #2A2636;
      }

      .chat-input-container {
        display: flex;
        align-items: center;
        gap: var(--vanna-space-2);
        padding: 4px 6px 4px 16px;
        border-radius: 2px;
        background: #FFFFFF;
        border: 1.5px solid #E2DFD8;
        transition: border-color var(--vanna-duration-200) ease, box-shadow var(--vanna-duration-200) ease;
      }

      .chat-input-container:focus-within {
        border-color: #141218;
        box-shadow: inset 0 -2px 0 0 #F0A500;
      }

      :host([theme="dark"]) .chat-input-container {
        background: #1E1B26;
        border-color: #2A2636;
      }

      :host([theme="dark"]) .chat-input-container:focus-within {
        border-color: #E8E4DC;
        box-shadow: inset 0 -2px 0 0 #F0A500;
      }

      .message-input {
        flex: 1;
        border: none;
        background: transparent;
        font-size: 15px;
        font-family: var(--vanna-font-family-default);
        line-height: 1.5;
        color: var(--vanna-foreground-default);
        resize: none;
        min-height: 48px;
        max-height: 140px;
        padding: 12px 0;
        outline: none;
      }

      :host([theme="dark"]) .message-input {
        color: rgba(232, 228, 220, 0.95);
      }

      .message-input::placeholder {
        color: rgba(69, 64, 90, 0.8);
      }

      :host([theme="dark"]) .message-input::placeholder {
        color: rgba(122, 117, 144, 0.65);
      }

      .message-input:focus {
        outline: none;
      }

      .message-input:disabled {
        color: rgba(122, 117, 144, 0.65);
        cursor: not-allowed;
      }

      :host([theme="dark"]) .message-input:disabled {
        color: rgba(69, 64, 90, 0.55);
      }

      .web-search-btn {
        width: 36px;
        height: 36px;
        border-radius: 2px;
        border: none;
        background: transparent;
        color: rgba(69, 64, 90, 0.35);
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        transition: color var(--vanna-duration-150) ease, background var(--vanna-duration-150) ease;
        position: relative;
        flex-shrink: 0;
      }

      .web-search-btn.active {
        color: #F0A500;
      }

      .web-search-btn:hover {
        color: #F0A500;
        background: rgba(240, 165, 0, 0.08);
      }

      .web-search-btn svg {
        width: 16px;
        height: 16px;
      }

      .web-search-btn::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: calc(100% + 6px);
        left: 50%;
        transform: translateX(-50%);
        background: #141218;
        color: #E8E4DC;
        font-size: 11px;
        font-family: var(--vanna-font-family-default);
        padding: 3px 8px;
        border-radius: 3px;
        white-space: nowrap;
        pointer-events: none;
        opacity: 0;
        transition: opacity var(--vanna-duration-150) ease;
        z-index: 10;
      }

      .web-search-btn:hover::after {
        opacity: 1;
      }

      :host([theme="dark"]) .web-search-btn {
        color: rgba(150, 144, 168, 0.4);
      }

      :host([theme="dark"]) .web-search-btn.active {
        color: #F0A500;
      }

      :host([theme="dark"]) .web-search-btn:hover {
        color: #F0A500;
        background: rgba(240, 165, 0, 0.1);
      }

      :host([theme="dark"]) .web-search-btn::after {
        background: #2A2636;
        color: #E8E4DC;
      }

      .send-button {
        width: 44px;
        height: 44px;
        border-radius: 2px;
        border: none;
        border-left: 3px solid #F0A500;
        background: #141218;
        color: #FFFFFF;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background var(--vanna-duration-150) ease, transform var(--vanna-duration-100) ease;
      }

      .send-button:hover {
        background: #2A2636;
      }

      .send-button:active {
        transform: scale(0.97);
      }

      .send-button:disabled {
        background: #45405A;
        border-left-color: transparent;
        color: rgba(255, 255, 255, 0.4);
        cursor: not-allowed;
        transform: none;
      }

      .send-button svg {
        width: 18px;
        height: 18px;
      }

      .sidebar {
        background: #FFFFFF;
        border-left: 1px solid #E2DFD8;
        padding: 0;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        min-height: 0;
      }

      .sidebar-scroll {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        padding: var(--vanna-space-5);
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-4);
        min-height: 0;
      }

      .sidebar-scroll::-webkit-scrollbar {
        width: 6px;
      }

      .sidebar-scroll::-webkit-scrollbar-track {
        background: transparent;
      }

      .sidebar-scroll::-webkit-scrollbar-thumb {
        background: var(--vanna-outline-default);
        border-radius: var(--vanna-border-radius-full);
      }

      .sidebar-section {
        display: flex;
        flex-direction: column;
        gap: var(--vanna-space-2);
      }

      .sidebar-section-title {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #7A7590;
        padding-bottom: var(--vanna-space-1);
        border-bottom: 1px solid #E2DFD8;
        margin-bottom: var(--vanna-space-1);
      }

      :host([theme="dark"]) .sidebar-section-title {
        color: #5A5570;
        border-bottom-color: #2A2636;
      }

      .suggested-prompt-btn {
        width: 100%;
        text-align: left;
        background: #F5F3EF;
        border: 1px solid #E2DFD8;
        border-radius: 4px;
        padding: var(--vanna-space-3);
        font-size: 13px;
        font-family: var(--vanna-font-family-default);
        color: #45405A;
        cursor: pointer;
        transition: background var(--vanna-duration-150) ease, border-color var(--vanna-duration-150) ease, color var(--vanna-duration-150) ease;
        line-height: 1.4;
        display: flex;
        align-items: flex-start;
        gap: var(--vanna-space-2);
      }

      .suggested-prompt-btn::before {
        content: '↗';
        flex-shrink: 0;
        color: #F0A500;
        font-size: 12px;
        margin-top: 1px;
      }

      .suggested-prompt-btn:hover {
        background: #EDE9E2;
        border-color: #C8C3BB;
        color: #141218;
      }

      .suggested-prompt-btn:active {
        background: #E3DDD6;
      }

      :host([theme="dark"]) .suggested-prompt-btn {
        background: #2A2636;
        border-color: #3A3547;
        color: #C4BFD8;
      }

      :host([theme="dark"]) .suggested-prompt-btn:hover {
        background: #3A3547;
        border-color: #4A455A;
        color: #E8E4DC;
      }

      .theme-toggle-btn {
        width: 28px;
        height: 28px;
        border-radius: 2px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        background: transparent;
        color: rgba(255, 255, 255, 0.6);
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        transition: all var(--vanna-duration-150) ease;
      }

      .theme-toggle-btn:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #F0A500;
        border-color: rgba(240, 165, 0, 0.3);
      }

      .theme-toggle-btn svg {
        width: 15px;
        height: 15px;
      }

      .sidebar-footer {
        flex-shrink: 0;
        padding: var(--vanna-space-3) var(--vanna-space-5);
        border-top: 1px solid #E2DFD8;
        display: flex;
        align-items: center;
        justify-content: flex-end;
      }

      :host([theme="dark"]) .sidebar-footer {
        border-top-color: #2A2636;
      }

      .sidebar-theme-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: transparent;
        border: 1px solid #E2DFD8;
        border-radius: 4px;
        width: 28px;
        height: 28px;
        padding: 0;
        color: #7A7590;
        cursor: pointer;
        transition: all var(--vanna-duration-150) ease;
      }

      .sidebar-theme-btn svg {
        width: 14px;
        height: 14px;
        flex-shrink: 0;
      }

      .sidebar-theme-btn:hover {
        background: #F5F3EF;
        border-color: #C8C3BB;
        color: #141218;
      }

      :host([theme="dark"]) .sidebar-theme-btn {
        border-color: #3A3547;
        color: #5A5570;
      }

      :host([theme="dark"]) .sidebar-theme-btn:hover {
        background: #2A2636;
        border-color: #4A455A;
        color: #C4BFD8;
      }


      .sidebar::-webkit-scrollbar {
        width: 6px;
      }

      .sidebar::-webkit-scrollbar-track {
        background: transparent;
      }

      .sidebar::-webkit-scrollbar-thumb {
        background: var(--vanna-outline-default);
        border-radius: var(--vanna-border-radius-full);
      }

      :host([theme="dark"]) .sidebar {
        background: #1E1B26;
        border-left-color: #2A2636;
      }

      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: var(--vanna-foreground-dimmer);
        padding: var(--vanna-space-16) var(--vanna-space-8);
        margin: var(--vanna-space-6) var(--vanna-space-6);
        font-size: 15px;
        font-weight: 400;
        line-height: 1.6;
        background: transparent;
        border: none;
      }

      :host([theme="dark"]) .empty-state {
        color: var(--vanna-foreground-dimmer);
      }

      .empty-state-icon {
        width: 120px;
        height: 120px;
        margin: 0 auto var(--vanna-space-5);
        opacity: 0.75;
        color: #45405A;
      }

      .empty-state-icon img {
        width: 100%;
        height: 100%;
        object-fit: contain;
      }

      .empty-state-text {
        font-size: 18px;
        font-weight: 600;
        color: var(--vanna-foreground-default);
        margin-bottom: var(--vanna-space-1);
        font-family: var(--vanna-font-family-serif);
        letter-spacing: -0.01em;
      }

      .empty-state-subtitle {
        font-size: 14px;
        color: #7A7590;
        font-weight: 400;
      }

      :host([theme="dark"]) .empty-state-subtitle {
        color: #9690A8;
      }

      :host([theme="dark"]) .empty-state-icon {
        opacity: 0.55;
        filter: brightness(1.15) saturate(0.85);
      }

      @media (max-width: 880px) {
        .chat-layout {
          grid-template-columns: 1fr;
          height: min(600px, 85vh);
          max-height: 85vh;
        }

        .sidebar {
          display: none;
        }

        .chat-main {
          border-right: none;
        }
      }

      @media (max-width: 600px) {
        :host {
          border-radius: var(--vanna-border-radius-xl);
        }

        .chat-layout {
          height: min(500px, 80vh);
          max-height: 80vh;
        }

        .chat-header {
          border-bottom-width: 0;
          padding: var(--vanna-space-5) var(--vanna-space-5) var(--vanna-space-4);
        }

        .chat-messages {
          padding: var(--vanna-space-4) var(--vanna-space-4);
        }

        .empty-state {
          padding: var(--vanna-space-10) var(--vanna-space-6);
          margin: var(--vanna-space-6) var(--vanna-space-4);
          font-size: 14px;
        }

        .empty-state-text {
          font-size: 15px;
        }

        .empty-state-icon {
          width: 96px;
          height: 96px;
          margin-bottom: var(--vanna-space-5);
        }

        .chat-input-area {
          padding: var(--vanna-space-4) var(--vanna-space-4) var(--vanna-space-5);
        }
      }
    `
  ];

  @property() title = 'FundPilot';
  @property() placeholder = 'Stel een vraag over uw data...';
  @property({ type: Boolean }) disabled = false;
  @property({ type: Boolean }) showProgress = true;
  @property({ type: Boolean }) allowMinimize = true;
  @property({ type: Boolean, attribute: 'no-header' }) noHeader = false;
  @property({ reflect: true }) theme = 'light';
  @property({ attribute: 'api-base' }) apiBaseUrl = '';
  @property({ attribute: 'sse-endpoint' }) sseEndpoint = '/api/vanna/v2/chat_sse';
  @property({ attribute: 'ws-endpoint' }) wsEndpoint = '/api/vanna/v2/chat_websocket';
  @property({ attribute: 'poll-endpoint' }) pollEndpoint = '/api/vanna/v2/chat_poll';
  @property() subtitle = '';
  @property({ attribute: 'user-email' }) userEmail = '';
  @property() startingState: 'normal' | 'maximized' | 'minimized' = 'normal';
  @property({ attribute: 'suggested-prompts' }) suggestedPromptsJson = '';

  @state() private currentMessage = '';
  @state() private _lastClickedPrompt = '';
  @state() private status: 'idle' | 'working' | 'error' | 'success' = 'idle';
  @state() private statusMessage = '';
  @state() private statusDetail = '';
  @state() private webSearchEnabled = true;
  private _windowState: 'normal' | 'maximized' | 'minimized' = 'normal';

  @property({ reflect: false })
  get windowState() {
    return this._windowState;
  }

  set windowState(value: 'normal' | 'maximized' | 'minimized') {
    console.log('windowState setter called with:', value);
    console.trace('Call stack:');
    const oldValue = this._windowState;
    this._windowState = value;
    this.requestUpdate('windowState', oldValue);
  }

  private apiClient!: VannaApiClient;
  private conversationId: string;
  private componentManager: ComponentManager | null = null;
  private componentObserver: MutationObserver | null = null;

  constructor() {
    super();
    // Note: Don't create apiClient here - attributes haven't been set yet!
    // It will be created lazily in getApiClient() or firstUpdated()
    this.conversationId = this.generateId();
  }

  /**
   * Ensure API client is created/updated with current endpoint values
   */
  private ensureApiClient() {
    // Preserve custom headers (e.g. Authorization) across client recreation
    const prevHeaders = this.apiClient?.getCustomHeaders?.() ?? {};

    console.log('[VannaChat] Creating API client with:', {
      baseUrl: this.apiBaseUrl,
      sseEndpoint: this.sseEndpoint,
      wsEndpoint: this.wsEndpoint,
      pollEndpoint: this.pollEndpoint
    });

    this.apiClient = new VannaApiClient({
      baseUrl: this.apiBaseUrl,
      sseEndpoint: this.sseEndpoint,
      wsEndpoint: this.wsEndpoint,
      pollEndpoint: this.pollEndpoint
    });

    // Restore any previously set headers
    if (Object.keys(prevHeaders).length > 0) {
      this.apiClient.setCustomHeaders(prevHeaders);
    }
  }

  firstUpdated() {
    // Create API client now that attributes have been set
    this.ensureApiClient();

    // Initialize component manager with rich components container (fallback)
    const richContainer = this.shadowRoot?.querySelector('.rich-components-container') as HTMLElement;
    if (richContainer) {
      this.componentManager = new ComponentManager(richContainer);
      
      // Watch for changes in the rich components container to manage empty state
      this.componentObserver = new MutationObserver(() => {
        // Update empty state visibility
        this.updateEmptyState();
      });
      
      this.componentObserver.observe(richContainer, {
        childList: true,
        subtree: true,
        attributes: false
      });
    }

    // Listen for edit-and-resend from user message bubbles
    this.addEventListener('message-resend', ((e: CustomEvent) => {
      const { content, componentId } = e.detail;
      if (componentId && this.componentManager) {
        this.componentManager.removeFromComponent(componentId);
        this.updateEmptyState();
      }
      this.sendMessage(content);
    }) as EventListener);

    // Listen for quick-reply button selections from assistant message bubbles
    this.addEventListener('quick-reply-selected', ((e: CustomEvent) => {
      this.sendMessage(e.detail.option);
    }) as EventListener);

    // Set initial window state from startingState property
    if (this.startingState !== 'normal') {
      this._windowState = this.startingState;
    }

    // Set initial CSS class
    this.classList.add(this._windowState);

    // Request starter UI from backend
    this.requestStarterUI();
  }

  /**
   * Request starter UI (buttons, welcome messages) from backend
   */
  private async requestStarterUI(): Promise<void> {
    try {
      const request = {
        message: "",
        conversation_id: this.conversationId,
        request_id: this.generateId(),
        metadata: {
          starter_ui_request: true
        }
      };

      // Stream the starter UI response
      await this.handleStreamingResponse(request);
    } catch (error) {
      console.error('Error requesting starter UI:', error);
      // Fail silently - starter UI is optional
    }
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    
    // Clean up mutation observer
    if (this.componentObserver) {
      this.componentObserver.disconnect();
      this.componentObserver = null;
    }
  }

  updated(changedProperties: Map<string, any>) {
    super.updated(changedProperties);

    // Update host classes based on window state
    if (changedProperties.has('windowState')) {
      console.log('windowState changed to:', this._windowState);
      this.classList.remove('normal', 'maximized', 'minimized');
      this.classList.add(this._windowState);
      console.log('Applied CSS classes:', this.className);
    }
  }

  private handleInput(e: Event) {
    const input = e.target as HTMLInputElement;
    this.currentMessage = input.value;
  }

  private handleKeyPress(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this.sendMessage();
    }
  }

  /**
   * Send a message programmatically (can be called from buttons or external code)
   * Returns a Promise that resolves with success status
   */
  sendMessage(messageText?: string): Promise<boolean> {
    console.log('sendMessage called with:', messageText);

    // Use provided message or fall back to current input
    // Check if messageText is actually a string (not an event object)
    const textToSend = (typeof messageText === 'string') ? messageText : this.currentMessage;

    console.log('Will send:', textToSend);

    if (!textToSend.trim() || this.disabled) {
      console.log('Message empty or disabled, not sending');
      return Promise.resolve(false);
    }

    return this._sendMessageInternal(textToSend);
  }

  private async _sendMessageInternal(messageText: string): Promise<boolean> {
    console.log('_sendMessageInternal called with:', messageText);

    // Auto-maximize window when user sends a message (skip when embedded with no-header)
    if (!this.noHeader && this.windowState !== 'maximized' && this.windowState !== 'minimized') {
      this.maximizeWindow();
    }

    // Create user message as a rich component and send to ComponentManager
    const userRichComponent: RichComponent = {
      id: `user-message-${Date.now()}`,
      type: 'user-message',
      lifecycle: 'create',
      data: {
        content: messageText,
        sender: 'user',
        sender_email: this.userEmail
      },
      children: [],
      timestamp: new Date().toISOString(),
      visible: true,
      interactive: false
    };

    // Add user message to ComponentManager for chronological ordering
    if (this.componentManager) {
      const update = {
        operation: 'create' as const,
        target_id: userRichComponent.id,
        component: userRichComponent,
        timestamp: userRichComponent.timestamp
      };
      this.componentManager.processUpdate(update);
    }

    // Update empty state after a brief delay to let ComponentManager render
    setTimeout(() => this.updateEmptyState(), 0);

    console.log('Added user message as rich component to ComponentManager:', userRichComponent);

    // Update the view
    this.requestUpdate();

    // Update status to working (initial frontend status before backend responds)
    this.setStatus('working', 'Sending message...', '');

    // Clear input only if we're sending from the input field
    if (messageText === this.currentMessage) {
      this.currentMessage = '';
      const input = this.shadowRoot?.querySelector('.message-input') as HTMLTextAreaElement;
      if (input) {
        input.value = '';
        input.style.height = 'auto';
      }
    }

    // Dispatch event for external listeners
    this.dispatchEvent(new CustomEvent('message-sent', {
      detail: { message: { content: messageText, type: 'user' } },
      bubbles: true,
      composed: true
    }));

    try {
      // Create the request
      const request = {
        message: messageText,
        conversation_id: this.conversationId,
        request_id: this.generateId(),
        metadata: { web_search_enabled: this.webSearchEnabled }
      };

      // Stream the response
      await this.handleStreamingResponse(request);
      return true; // Success

    } catch (error) {
      console.error('Error sending message:', error);
      this.setStatus('error', 'Failed to send message', error instanceof Error ? error.message : 'Unknown error');

      // Add error message
      this.addMessage(
        `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'assistant'
      );
      return false; // Failure
    }
  }

  private minimizeWindow(e?: Event) {
    if (e) {
      e.stopPropagation();
      e.preventDefault();
    }
    console.log('minimizeWindow called, current state:', this._windowState);
    this.windowState = 'minimized';
    console.log('minimizeWindow set state to:', this._windowState);
    this.dispatchEvent(new CustomEvent('window-state-changed', {
      detail: { state: 'minimized' },
      bubbles: true,
      composed: true
    }));
  }

  private maximizeWindow(e?: Event) {
    if (e) {
      e.stopPropagation();
      e.preventDefault();
    }
    this.windowState = 'maximized';
    this.dispatchEvent(new CustomEvent('window-state-changed', {
      detail: { state: 'maximized' },
      bubbles: true,
      composed: true
    }));
  }

  private restoreWindow(e?: Event) {
    if (e) {
      e.stopPropagation();
      e.preventDefault();
    }
    this.windowState = 'normal';
    this.dispatchEvent(new CustomEvent('window-state-changed', {
      detail: { state: 'normal' },
      bubbles: true,
      composed: true
    }));
  }


  addMessage(content: string, type: 'user' | 'assistant') {
    // Create message as a rich component and send to ComponentManager
    const richComponent: RichComponent = {
      id: `${type}-message-${Date.now()}`,
      type: `${type}-message`,
      lifecycle: 'create',
      data: {
        content: content,
        sender: type
      },
      children: [],
      timestamp: new Date().toISOString(),
      visible: true,
      interactive: false
    };

    if (this.componentManager) {
      const update = {
        operation: 'create' as const,
        target_id: richComponent.id,
        component: richComponent,
        timestamp: richComponent.timestamp
      };
      this.componentManager.processUpdate(update);
    }
  }

  setStatus(status: typeof this.status, message: string, detail?: string) {
    this.status = status;
    this.statusMessage = message;
    this.statusDetail = detail || '';
  }

  clearStatus() {
    this.statusMessage = '';
    this.statusDetail = '';
    this.status = 'idle';
  }

  getProgressTracker(): HTMLElement | null {
    return this.shadowRoot?.querySelector('vanna-progress-tracker') || null;
  }

  private async handleStreamingResponse(request: any) {
    // Ensure API client exists and is up to date
    if (!this.apiClient || this.apiClient.baseUrl !== this.apiBaseUrl) {
      this.ensureApiClient();
    }

    // Note: Status bar updates are now controlled by backend via StatusBarUpdateComponent
    // Frontend only shows initial "Sending message..." status (set in _sendMessageInternal)
    // and handles connection errors below

    try {
      // Use SSE streaming by default
      const stream = this.apiClient.streamChat(request);

      for await (const chunk of stream) {
        await this.processChunk(chunk);
      }

      // Backend is responsible for final status via StatusBarUpdateComponent
      // No frontend status clearing here

    } catch (error) {
      console.warn('SSE streaming failed, falling back to polling:', error);

      try {
        // Fallback to polling - show user we're retrying
        this.setStatus('working', 'Connection issue, retrying...', 'Using fallback method');
        const response = await this.apiClient.sendPollMessage(request);

        for (const chunk of response.chunks) {
          await this.processChunk(chunk);
        }

        // Backend is responsible for final status via StatusBarUpdateComponent

      } catch (pollError) {
        // Only set error status if polling also fails (connection error)
        this.setStatus('error', 'Connection failed', 'Unable to reach server');
        throw pollError;
      }
    }
  }

  private async processChunk(chunk: ChatStreamChunk) {
    // Dispatch chunk event for external listeners
    this.dispatchEvent(new CustomEvent('chunk-received', {
      detail: { chunk },
      bubbles: true,
      composed: true
    }));

    console.log('Processing chunk:', chunk); // Debug log

    // Handle rich components via ComponentManager
    if (chunk.rich && this.componentManager) {
      console.log('Processing rich component via ComponentManager:', chunk.rich); // Debug log
      
      if (chunk.rich.id && chunk.rich.lifecycle) {
        // Standard rich component with lifecycle
        const component = chunk.rich as RichComponent;
        const update = {
          operation: chunk.rich.lifecycle as any,
          target_id: chunk.rich.id,
          component: component,
          timestamp: new Date().toISOString()
        };
        this.componentManager.processUpdate(update);
      } else if (chunk.rich.type === 'component_update') {
        // Component update format
        this.componentManager.processUpdate(chunk.rich as any);
      } else {
        // Generic rich component
        const component = chunk.rich as RichComponent;
        const update = {
          operation: 'create' as const,
          target_id: component.id || `component-${Date.now()}`,
          component: component,
          timestamp: new Date().toISOString()
        };
        this.componentManager.processUpdate(update);
      }
      
      return;
    }

    // Update progress tracker for legacy components (keep for backward compatibility)
    const progressTracker = this.getProgressTracker();
    if (progressTracker && 'addStep' in progressTracker) {
      (progressTracker as any).addStep({
        id: `chunk-${Date.now()}`,
        title: this.getChunkTitle(chunk),
        status: 'completed',
        timestamp: chunk.timestamp
      });
    }

    // Handle different chunk types (legacy components)
    const componentType = chunk.rich?.type;
    switch (componentType) {
      case 'text':
        // Text chunks are handled in the main loop
        break;

      case 'thinking':
        // Legacy: Status bar updates now handled by backend via StatusBarUpdateComponent
        // This case is kept for backward compatibility but doesn't update status
        break;

      case 'tool_execution':
        // Legacy: Status bar updates now handled by backend via StatusBarUpdateComponent
        // This case is kept for backward compatibility but doesn't update status
        break;

      case 'error':
        throw new Error(chunk.rich.data?.message || 'Unknown error from agent');

      default:
        // Handle other component types as needed
        console.log('Received chunk:', componentType, chunk.rich);
    }
  }


  private getChunkTitle(chunk: ChatStreamChunk): string {
    const componentType = chunk.rich?.type;
    switch (componentType) {
      case 'text':
        return 'Generating response';
      case 'thinking':
        return 'Thinking';
      case 'tool_execution':
        return `Tool: ${chunk.rich.data?.tool_name || 'Unknown'}`;
      default:
        return `Processing ${componentType || 'component'}`;
    }
  }

  private get _suggestedPrompts(): string[] {
    if (this.suggestedPromptsJson) {
      try {
        return JSON.parse(this.suggestedPromptsJson);
      } catch {
        // fall through to defaults
      }
    }
    return [
      'Wat is de werkelijke kostprijs per duurzame donor, inclusief uitval en chargebacks, uitgesplitst per kanaal?',
      'Welke leveranciers of campagnes leveren structureel de hoogste retentie na 6 maanden op?',
      'Welke campagnes of importkanalen hebben de meeste groeiruimte op basis van conversie én gemiddeld donatiebedrag?',
    ];
  }

  private _handleSuggestedPrompt(prompt: string) {
    this._lastClickedPrompt = prompt;
    this.sendMessage(prompt);
    setTimeout(() => { this._lastClickedPrompt = ''; }, 1500);
  }

  private _toggleTheme() {
    this.theme = this.theme === 'dark' ? 'light' : 'dark';
    this.dispatchEvent(new CustomEvent('theme-changed', {
      detail: { theme: this.theme },
      bubbles: true,
      composed: true
    }));
  }

  private _toggleWebSearch() {
    this.webSearchEnabled = !this.webSearchEnabled;
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
  }

  /**
   * Update the API base URL and recreate the client
   */
  updateApiBaseUrl(baseUrl: string) {
    this.apiBaseUrl = baseUrl;
    this.ensureApiClient();
  }

  /**
   * Get the API client instance for direct access
   */
  getApiClient(): VannaApiClient {
    if (!this.apiClient) {
      this.ensureApiClient();
    }
    return this.apiClient;
  }

  /**
   * Set custom headers for authentication or other purposes
   */
  setCustomHeaders(headers: Record<string, string>) {
    this.ensureApiClient();
    this.apiClient.setCustomHeaders(headers);
  }

  /**
   * Update empty state visibility based on whether there are components
   */
  private updateEmptyState() {
    const emptyState = this.shadowRoot?.querySelector('#empty-state') as HTMLElement;
    const richContainer = this.shadowRoot?.querySelector('.rich-components-container') as HTMLElement;
    
    if (emptyState && richContainer) {
      // Show empty state if rich container has no children
      const hasContent = richContainer.children.length > 0;
      emptyState.style.display = hasContent ? 'none' : 'flex';
    }
  }

  /**
   * Update scroll indicator based on scroll position
   */
  private updateScrollIndicator() {
    const messagesContainer = this.shadowRoot?.querySelector('.chat-messages');
    if (!messagesContainer) return;
    
    // Check if there's content scrolled above
    const hasScrolledContent = messagesContainer.scrollTop > 10;
    
    // Update scroll indicator class
    messagesContainer.classList.toggle('has-scroll', hasScrolledContent);
  }

  /**
   * Scroll to the top of the last message/component that was added
   * This always scrolls regardless of current scroll position
   */
  scrollToLastMessage() {
    const messagesContainer = this.shadowRoot?.querySelector('.chat-messages');
    const richContainer = this.shadowRoot?.querySelector('.rich-components-container');
    
    if (!messagesContainer || !richContainer) return;

    // Get the last child element (the most recently added component)
    const lastComponent = richContainer.lastElementChild as HTMLElement;
    if (!lastComponent) return;

    // Scroll so the top of the last component is visible
    lastComponent.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Update scroll indicator after scrolling
    setTimeout(() => this.updateScrollIndicator(), 100);
  }

  /**
   * Clear all messages (useful for testing)
   */
  clearMessages() {
    if (this.componentManager) {
      this.componentManager.clear();
    }
    this.updateEmptyState();
    this.requestUpdate();
  }

  /**
   * Add multiple messages at once (useful for testing scrolling)
   */
  addTestMessages(count: number = 10) {
    for (let i = 1; i <= count; i++) {
      setTimeout(() => {
        const type = i % 2 === 0 ? 'assistant' : 'user';
        const content = `This is test message number ${i}. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.`;
        this.addMessage(content, type);
      }, i * 100); // Stagger the messages to simulate real timing
    }
  }

  render() {
    return html`
      <!-- Minimized icon - shown only when minimized via CSS and allowMinimize is true -->
      ${this.allowMinimize ? html`
        <div class="minimized-icon" @click=${this.restoreWindow}>
          <img src="/img/app-icon-512.png" alt="FundPilot openen" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">
        </div>
      ` : ''}

      <!-- Main chat interface -->
      <div class="chat-layout ${this.showProgress ? '' : 'compact'}">
        <div class="chat-main">
          ${this.noHeader ? html`` : html`
          <div class="chat-header">
            <div class="header-top">
              <div class="header-left">
                <div class="chat-avatar" aria-hidden="true">
                  <img src="/img/app-icon-512.png" alt="" width="36" height="36">
                </div>
                <div class="header-text">
                  <h2 class="chat-title" aria-label="${this.title}">
                    <img src="/img/fund_pilot.png" alt="${this.title}" class="chat-title-logo">
                  </h2>
                </div>
              </div>
              <div class="header-top-actions">
                <div class="window-controls">
                  ${this.allowMinimize ? html`
                    <button
                      class="window-control-btn minimize"
                      @click=${this.minimizeWindow}
                      title="Minimize">
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M5 12h14v2H5z"/>
                      </svg>
                    </button>
                  ` : html``}
                  ${this.windowState === 'maximized' ? html`
                    <button
                      class="window-control-btn restore"
                      @click=${this.restoreWindow}
                      title="Restore">
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M8 8v2h2V8h6v6h-2v2h4V6H8zm-2 4v8h8v-2H8v-6H6z"/>
                      </svg>
                    </button>
                  ` : html`
                    <button
                      class="window-control-btn maximize"
                      @click=${this.maximizeWindow}
                      title="Maximize">
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M5 5v14h14V5H5zm2 2h10v10H7V7z"/>
                      </svg>
                    </button>
                  `}
                </div>
              </div>
            </div>
          </div>
          `}

          <div class="chat-messages">
            <!-- Empty state - shown when no components exist -->
            <div class="empty-state" id="empty-state">
              <div class="empty-state-icon">
                <img
                  src=${this.status === 'error' ? '/img/empty-error.svg' : '/img/empty-first-query.svg'}
                  alt="" aria-hidden="true">
              </div>
              <div class="empty-state-text">${this.status === 'error' ? 'Er is een fout opgetreden' : 'Stel een vraag'}</div>
              <div class="empty-state-subtitle">${this.status === 'error' ? 'Probeer het opnieuw of stel een andere vraag' : 'Typ uw vraag hieronder om te beginnen'}</div>
            </div>

            <!-- Rich Components Container - all content renders here via ComponentManager -->
            <div class="rich-components-container"></div>
          </div>

          <div class="chat-input-area">
            <vanna-status-bar
              .status=${this.status}
              .message=${this.statusMessage}
              .detail=${this.statusDetail}
              theme=${this.theme}>
            </vanna-status-bar>

            <div class="chat-input-container">
              <textarea
                class="message-input"
                autocomplete="off"
                .placeholder=${this.placeholder}
                .disabled=${this.disabled}
                @input=${this.handleInput}
                @keydown=${this.handleKeyPress}
                rows="1"
              ></textarea>
              <button
                class="web-search-btn ${this.webSearchEnabled ? 'active' : ''}"
                type="button"
                data-tooltip="${this.webSearchEnabled ? 'Webzoeken aan' : 'Webzoeken uit'}"
                aria-label="${this.webSearchEnabled ? 'Webzoeken uitschakelen' : 'Webzoeken inschakelen'}"
                aria-pressed="${this.webSearchEnabled}"
                @click=${this._toggleWebSearch}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                  <line x1="2" y1="12" x2="22" y2="12"/>
                </svg>
              </button>
              <button
                class="send-button"
                type="button"
                aria-label="Send message"
                .disabled=${this.disabled || !this.currentMessage.trim()}
                @click=${this.sendMessage}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        ${this.showProgress ? html`
          <div class="sidebar">
            <div class="sidebar-scroll">
              <vanna-progress-tracker theme=${this.theme}></vanna-progress-tracker>
              ${this._suggestedPrompts.length > 0 ? html`
                <div class="sidebar-section">
                  <div class="sidebar-section-title">Voorgestelde vragen</div>
                  ${this._suggestedPrompts.map(prompt => html`
                    <button
                      class="suggested-prompt-btn"
                      style=${this._lastClickedPrompt === prompt ? 'border-color:#F0A500;background:#FFF8E6;' : ''}
                      @click=${() => this._handleSuggestedPrompt(prompt)}>
                      ${prompt}
                    </button>
                  `)}
                </div>
              ` : ''}
            </div>
            <div class="sidebar-footer">
              <button class="sidebar-theme-btn" @click=${this._toggleTheme} title=${this.theme === 'dark' ? 'Licht thema' : 'Donker thema'}>
                ${this.theme === 'dark' ? html`
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 7a5 5 0 1 0 0 10A5 5 0 0 0 12 7zm0-5a1 1 0 0 1 1 1v1a1 1 0 0 1-2 0V3a1 1 0 0 1 1-1zm0 17a1 1 0 0 1 1 1v1a1 1 0 0 1-2 0v-1a1 1 0 0 1 1-1zM4.22 4.22a1 1 0 0 1 1.42 0l.7.7a1 1 0 0 1-1.42 1.42l-.7-.7a1 1 0 0 1 0-1.42zm13.44 13.44a1 1 0 0 1 1.42 0l.7.7a1 1 0 0 1-1.42 1.42l-.7-.7a1 1 0 0 1 0-1.42zM3 12a1 1 0 0 1 1-1h1a1 1 0 0 1 0 2H4a1 1 0 0 1-1-1zm16 0a1 1 0 0 1 1-1h1a1 1 0 0 1 0 2h-1a1 1 0 0 1-1-1zM4.22 19.78a1 1 0 0 1 0-1.42l.7-.7a1 1 0 0 1 1.42 1.42l-.7.7a1 1 0 0 1-1.42 0zm13.44-13.44a1 1 0 0 1 0-1.42l.7-.7a1 1 0 0 1 1.42 1.42l-.7.7a1 1 0 0 1-1.42 0z"/></svg>
                ` : html`
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                `}
              </button>
            </div>
          </div>
        ` : ''}
      </div>
    `;
  }
}
