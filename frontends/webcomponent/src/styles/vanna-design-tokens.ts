import { css } from 'lit';

// FundPilot "Data Bureau" design tokens
// Brand spec: BRANDKIT.md
export const vannaDesignTokens = css`
  :host {
    /* FundPilot Core Palette */
    --fp-bureau-black: #141218;
    --fp-graphite-violet: #45405A;
    --fp-electric-saffron: #F0A500;
    --fp-warm-chalk: #F5F3EF;
    --fp-clean-white: #FFFFFF;
    --fp-deep-ink: #1E1B26;

    /* FundPilot Extended Palette */
    --fp-terminal-green: #00C853;
    --fp-signal-amber: #FFB300;
    --fp-alert-crimson: #D32F2F;
    --fp-deep-saffron: #D4920A;
    --fp-saffron-wash: rgba(240, 165, 0, 0.08);
    --fp-chalk-edge: #E2DFD8;
    --fp-stone: #C8C3B8;
    --fp-faded-violet: #7A7590;
    --fp-terminal-wash: #F8F6F2;

    /* Color Palette - Light mode (default) */
    --vanna-background-root: #F5F3EF;
    --vanna-background-default: #F5F3EF;
    --vanna-background-higher: #FFFFFF;
    --vanna-background-highest: #FFFFFF;
    --vanna-background-subtle: #F8F6F2;
    --vanna-background-lower: #F5F3EF;

    --vanna-foreground-default: #1E1B26;
    --vanna-foreground-dimmer: #45405A;
    --vanna-foreground-dimmest: #7A7590;

    --vanna-accent-primary-default: #F0A500;
    --vanna-accent-primary-stronger: #141218;
    --vanna-accent-primary-strongest: #141218;
    --vanna-accent-primary-subtle: rgba(240, 165, 0, 0.08);
    --vanna-accent-primary-hover: #D4920A;

    --vanna-accent-positive-default: #00C853;
    --vanna-accent-positive-stronger: #00A844;
    --vanna-accent-positive-subtle: rgba(0, 200, 83, 0.1);

    --vanna-accent-negative-default: #D32F2F;
    --vanna-accent-negative-stronger: #B71C1C;
    --vanna-accent-negative-subtle: rgba(211, 47, 47, 0.1);

    --vanna-accent-warning-default: #FFB300;
    --vanna-accent-warning-stronger: #F0A500;
    --vanna-accent-warning-subtle: rgba(255, 179, 0, 0.1);

    /* Outline/Border colors */
    --vanna-outline-default: #E2DFD8;
    --vanna-outline-dimmer: #E2DFD8;
    --vanna-outline-dimmest: #F5F3EF;
    --vanna-outline-hover: #C8C3B8;

    /* Typography - FundPilot Data Bureau */
    --vanna-font-family-default: "Outfit", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --vanna-font-family-serif: "Fraunces", ui-serif, Georgia, serif;
    --vanna-font-family-mono: "Fira Code", ui-monospace, SFMono-Regular, "SF Mono", Monaco, Inconsolata, "Roboto Mono", monospace;

    /* Spacing scale (4px base) */
    --vanna-space-0: 0px;
    --vanna-space-1: 4px;
    --vanna-space-2: 8px;
    --vanna-space-3: 12px;
    --vanna-space-4: 16px;
    --vanna-space-5: 20px;
    --vanna-space-6: 24px;
    --vanna-space-7: 28px;
    --vanna-space-8: 32px;
    --vanna-space-10: 40px;
    --vanna-space-12: 48px;
    --vanna-space-16: 64px;

    /* Border radius - Sharp, editorial */
    --vanna-border-radius-sm: 2px;
    --vanna-border-radius-md: 4px;
    --vanna-border-radius-lg: 6px;
    --vanna-border-radius-xl: 4px;
    --vanna-border-radius-2xl: 6px;
    --vanna-border-radius-full: 9999px;

    /* Shadows - Data Bureau double-shadow technique */
    --vanna-shadow-xs: 0 1px 2px rgba(20, 18, 24, 0.05);
    --vanna-shadow-sm: 0 1px 2px rgba(20, 18, 24, 0.05);
    --vanna-shadow-md: 0 2px 8px rgba(20, 18, 24, 0.06), 0 12px 32px rgba(20, 18, 24, 0.04);
    --vanna-shadow-lg: 0 4px 16px rgba(20, 18, 24, 0.08), 0 24px 48px rgba(20, 18, 24, 0.06);
    --vanna-shadow-xl: 0 4px 16px rgba(20, 18, 24, 0.08), 0 24px 48px rgba(20, 18, 24, 0.06);
    --vanna-shadow-2xl: 0 4px 16px rgba(20, 18, 24, 0.08), 0 24px 48px rgba(20, 18, 24, 0.06);
    --vanna-shadow-focus: 0 0 0 3px rgba(240, 165, 0, 0.2);

    /* Animation durations */
    --vanna-duration-75: 75ms;
    --vanna-duration-100: 100ms;
    --vanna-duration-150: 150ms;
    --vanna-duration-200: 200ms;
    --vanna-duration-300: 300ms;
    --vanna-duration-500: 500ms;
    --vanna-duration-700: 700ms;

    /* Z-index scale */
    --vanna-z-dropdown: 1000;
    --vanna-z-sticky: 1020;
    --vanna-z-fixed: 1030;
    --vanna-z-modal: 1040;
    --vanna-z-popover: 1050;
    --vanna-z-tooltip: 1060;

    /* Chat-specific tokens */
    --vanna-chat-bubble-radius: 4px;
    --vanna-chat-bubble-radius-sm: 2px;
    --vanna-chat-spacing: 16px;
    --vanna-chat-avatar-size: 40px;
  }

  /* Dark theme overrides */
  :host([theme="dark"]) {
    --vanna-background-root: #141218;
    --vanna-background-default: #141218;
    --vanna-background-higher: #1E1B26;
    --vanna-background-highest: #2A2636;
    --vanna-background-subtle: #1A1724;
    --vanna-background-lower: #0F0D14;

    --vanna-foreground-default: #E8E4DC;
    --vanna-foreground-dimmer: #9690A8;
    --vanna-foreground-dimmest: #7A7590;

    --vanna-accent-primary-default: #F0A500;
    --vanna-accent-primary-stronger: #F0A500;
    --vanna-accent-primary-strongest: #D4920A;
    --vanna-accent-primary-subtle: rgba(240, 165, 0, 0.12);
    --vanna-accent-primary-hover: #D4920A;

    --vanna-accent-positive-default: #00E676;
    --vanna-accent-positive-stronger: #00C853;
    --vanna-accent-positive-subtle: rgba(0, 230, 118, 0.12);

    --vanna-accent-negative-default: #EF5350;
    --vanna-accent-negative-stronger: #D32F2F;
    --vanna-accent-negative-subtle: rgba(239, 83, 80, 0.12);

    --vanna-accent-warning-default: #FFCA28;
    --vanna-accent-warning-stronger: #FFB300;
    --vanna-accent-warning-subtle: rgba(255, 202, 40, 0.12);

    --vanna-outline-default: #2A2636;
    --vanna-outline-dimmer: #1E1B26;
    --vanna-outline-dimmest: #141218;
    --vanna-outline-hover: #45405A;

    --vanna-shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.4);
    --vanna-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
    --vanna-shadow-md: 0 2px 8px rgba(0, 0, 0, 0.3), 0 12px 32px rgba(0, 0, 0, 0.2);
    --vanna-shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.35), 0 24px 48px rgba(0, 0, 0, 0.25);
    --vanna-shadow-xl: 0 4px 16px rgba(0, 0, 0, 0.35), 0 24px 48px rgba(0, 0, 0, 0.25);
    --vanna-shadow-2xl: 0 4px 16px rgba(0, 0, 0, 0.35), 0 24px 48px rgba(0, 0, 0, 0.25);
  }
`;
