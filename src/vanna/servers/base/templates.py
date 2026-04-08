"""
HTML templates for Vanna Agents servers.
"""

from typing import Optional


def get_vanna_component_script(
    dev_mode: bool = False,
    static_path: str = "/static",
    cdn_url: str = "https://img.vanna.ai/vanna-components.js",
) -> str:
    """Get the script tag for loading Vanna web components.

    Args:
        dev_mode: If True, load from local static files
        static_path: Path to static assets in dev mode
        cdn_url: CDN URL for production

    Returns:
        HTML script tag for loading components
    """
    if dev_mode:
        return (
            f'<script type="module" src="{static_path}/vanna-components.js"></script>'
        )
    else:
        return f'<script type="module" src="{cdn_url}"></script>'


def get_index_html(
    dev_mode: bool = False,
    static_path: str = "/static",
    cdn_url: str = "https://img.vanna.ai/vanna-components.js",
    api_base_url: str = "",
    supabase_url: str = "",
    supabase_publishable_key: str = "",
    require_mfa: bool = True,
) -> str:
    """Generate index HTML with configurable component loading.

    Args:
        dev_mode: If True, load components from local static files
        static_path: Path to static assets in dev mode
        cdn_url: CDN URL for production components
        api_base_url: Base URL for API endpoints
        supabase_url: Supabase project URL (enables real auth when set)
        supabase_publishable_key: Supabase publishable key (safe for browser)
        require_mfa: If True, users without MFA enrolled are blocked from login

    Returns:
        Complete HTML page as string
    """
    component_script = get_vanna_component_script(dev_mode, static_path, cdn_url)

    return f"""<!DOCTYPE html>
<html lang="en" data-require-mfa="{'true' if require_mfa else 'false'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FundPilot</title>
    <meta name="description" content="FundPilot — AI-Powered Data Analyst">
    <meta property="og:title" content="FundPilot">
    <meta property="og:description" content="AI-Powered Data Analyst">
    <meta property="og:image" content="/img/og-image.png">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="/img/og-image.png">
    <link rel="icon" type="image/x-icon" href="/img/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/img/favicon-16.png">
    <link rel="apple-touch-icon" sizes="512x512" href="/img/app-icon-512.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700;800&family=Outfit:wght@300;400;500;600&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        'fp-black': '#141218',
                        'fp-violet': '#45405A',
                        'fp-saffron': '#F0A500',
                        'fp-chalk': '#F5F3EF',
                        'fp-ink': '#1E1B26',
                        'fp-edge': '#E2DFD8',
                        'fp-stone': '#C8C3B8',
                        'fp-faded': '#7A7590',
                        'fp-green': '#00C853',
                        'fp-amber': '#FFB300',
                        'fp-crimson': '#D32F2F',
                        'fp-saffron-deep': '#D4920A',
                        'fp-wash': '#F8F6F2',
                    }},
                    fontFamily: {{
                        'sans': ['Outfit', 'ui-sans-serif', 'system-ui'],
                        'serif': ['Fraunces', 'ui-serif', 'Georgia'],
                        'mono': ['Fira Code', 'ui-monospace', 'monospace'],
                    }}
                }}
            }}
        }}
    </script>
    <style>
        *, *::before, *::after {{ box-sizing: border-box; }}

        body {{
            background: #F5F3EF;
            min-height: 100vh;
            height: 100vh;
            overflow: hidden;
            font-family: 'Outfit', ui-sans-serif, system-ui, sans-serif;
            color: #1E1B26;
            margin: 0;
        }}

        /* ── UTILITIES ───────────────────────────────────────────── */
        .hidden {{ display: none !important; }}

        /* ── LOADING BAR ─────────────────────────────────────────── */
        .fp-loading-bar {{
            height: 2px;
            background: #F0A500;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 200;
            opacity: 0;
            transition: opacity 0.2s;
        }}

        /* ═══════════════════════════════════════════════════════════
           LOGIN SCREEN — full-screen split layout
        ═══════════════════════════════════════════════════════════ */
        #loginContainer {{
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}

        /* Left branding panel */
        .fp-login-left {{
            width: 50%;
            background: #141218;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: flex-start;
            padding: 80px 72px;
            position: relative;
            overflow: hidden;
            animation: slideInLeft 400ms ease-out;
        }}

        .fp-login-left::before {{
            content: '';
            position: absolute;
            inset: 0;
            background-image:
                linear-gradient(rgba(240, 165, 0, 0.07) 1px, transparent 1px),
                linear-gradient(90deg, rgba(240, 165, 0, 0.07) 1px, transparent 1px);
            background-size: 48px 48px;
            pointer-events: none;
        }}

        .fp-login-brand-logo {{
            height: 64px;
            width: auto;
            margin-bottom: 56px;
            position: relative;
            z-index: 1;
        }}

        .fp-login-headline {{
            font-family: 'Fraunces', serif;
            font-size: 62px;
            font-weight: 700;
            color: #FFFFFF;
            line-height: 1.1;
            letter-spacing: -0.03em;
            margin: 0 0 20px;
            position: relative;
            z-index: 1;
        }}

        .fp-login-tagline {{
            font-size: 17px;
            color: #9690A8;
            margin: 0 0 40px;
            line-height: 1.65;
            max-width: 320px;
            position: relative;
            z-index: 1;
        }}

        .fp-login-rule {{
            width: 56px;
            height: 3px;
            background: #F0A500;
            border: none;
            margin: 0;
            position: relative;
            z-index: 1;
            border-radius: 1px;
        }}

        /* Right form panel */
        .fp-login-right {{
            width: 50%;
            background: #F5F3EF;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 80px 72px;
        }}

        .fp-login-form-inner {{
            width: 100%;
            max-width: 420px;
        }}

        .fp-login-form-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 36px;
        }}

        .fp-login-form-logo {{
            height: 36px;
            width: auto;
        }}

        .fp-login-form-brand-text {{
            font-size: 14px;
            font-weight: 700;
            color: #45405A;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .fp-login-form-title {{
            font-family: 'Fraunces', serif;
            font-size: 32px;
            font-weight: 600;
            color: #141218;
            margin: 0 0 32px;
            letter-spacing: -0.02em;
        }}

        /* ═══════════════════════════════════════════════════════════
           APP SHELL — sidebar + chat layout
        ═══════════════════════════════════════════════════════════ */
        #chatSections {{
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }}

        #chatSections:not(.hidden) {{
            display: flex;
        }}

        /* Thin top bar */
        .fp-topbar {{
            height: 36px;
            background: #141218;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding: 0 16px;
            gap: 12px;
            flex-shrink: 0;
            z-index: 50;
        }}

        .fp-topbar-user {{
            font-size: 12px;
            color: rgba(255, 255, 255, 0.5);
            font-weight: 400;
        }}

        .fp-topbar-user strong {{
            color: rgba(255, 255, 255, 0.75);
            font-weight: 500;
        }}

        .fp-topbar-btn {{
            padding: 3px 10px;
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 2px;
            color: rgba(255, 255, 255, 0.5);
            font-size: 11px;
            font-weight: 500;
            font-family: 'Outfit', sans-serif;
            cursor: pointer;
            transition: color 0.15s ease, border-color 0.15s ease;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .fp-topbar-btn:hover {{
            color: #F0A500;
            border-color: rgba(240, 165, 0, 0.3);
        }}

        /* Main content row */
        .fp-main {{
            flex: 1;
            display: flex;
            overflow: hidden;
            min-height: 0;
            height: calc(100vh - 36px);
        }}

        /* ── SIDEBAR ─────────────────────────────────────────────── */
        .fp-sidebar {{
            width: 240px;
            flex-shrink: 0;
            background: #FFFFFF;
            border-right: 1px solid #E2DFD8;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .fp-sidebar-logo-area {{
            height: 56px;
            background: #F5F3EF;
            border-bottom: 1px solid #E2DFD8;
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 0 20px;
            flex-shrink: 0;
        }}

        .fp-sidebar-logo-img {{
            height: 22px;
            width: auto;
        }}

        .fp-sidebar-logo-text {{
            font-size: 13px;
            font-weight: 600;
            color: #141218;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        .fp-sidebar-body {{
            flex: 1;
            overflow-y: auto;
            overflow-x: hidden;
            display: flex;
            flex-direction: column;
        }}

        .fp-sidebar-overline {{
            font-size: 11px;
            font-weight: 600;
            color: #45405A;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 16px 20px 6px;
        }}

        .fp-sidebar-nav-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 9px 20px;
            font-size: 14px;
            font-weight: 500;
            color: #45405A;
            cursor: pointer;
            transition: color 0.15s ease, background 0.15s ease;
            border-left: 3px solid transparent;
            text-decoration: none;
            animation: fadeInItem 200ms ease-out both;
        }}

        .fp-sidebar-nav-item:hover {{
            color: #141218;
            background: rgba(240, 165, 0, 0.06);
        }}

        .fp-sidebar-nav-item.active {{
            color: #141218;
            background: rgba(240, 165, 0, 0.08);
            border-left-color: #F0A500;
        }}

        .fp-sidebar-divider {{
            height: 1px;
            background: #E2DFD8;
            margin: 8px 0;
            flex-shrink: 0;
        }}

        /* History section */
        .fp-history-section {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            min-height: 0;
        }}

        .fp-history-list {{
            flex: 1;
            overflow-y: auto;
        }}

        .fp-history-item {{
            display: block;
            padding: 8px 20px;
            cursor: pointer;
            border: none;
            background: transparent;
            width: 100%;
            text-align: left;
            transition: background 0.15s ease;
            opacity: 0;
            transform: translateX(-8px);
            animation: slideInItem 200ms ease-out forwards;
        }}

        .fp-history-item:hover {{
            background: rgba(240, 165, 0, 0.08);
        }}

        .fp-history-item-text {{
            font-size: 13px;
            color: #1E1B26;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            display: block;
            line-height: 1.4;
            font-family: 'Outfit', sans-serif;
        }}

        .fp-history-item-ts {{
            font-size: 11px;
            color: #7A7590;
            display: block;
            margin-top: 1px;
            font-family: 'Outfit', sans-serif;
        }}

        .fp-history-empty {{
            padding: 12px 20px;
            font-size: 13px;
            color: #7A7590;
        }}

        .fp-sidebar-footer {{
            padding: 10px 20px;
            border-top: 1px solid #E2DFD8;
            flex-shrink: 0;
        }}

        .fp-clear-btn {{
            font-size: 12px;
            color: #7A7590;
            background: transparent;
            border: none;
            cursor: pointer;
            padding: 0;
            font-family: 'Outfit', sans-serif;
            transition: color 0.15s ease;
        }}

        .fp-clear-btn:hover {{
            color: #D32F2F;
        }}

        /* ── CHAT AREA ────────────────────────────────────────────── */
        .fp-chat-area {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            min-width: 0;
            position: relative;
        }}

        /* Chat mount */
        .fp-chat-mount {{
            flex: 1;
            overflow: hidden;
            display: block;
        }}

        /* Override vanna-chat's floating-widget defaults so it embeds cleanly */
        .fp-chat-mount vanna-chat {{
            display: block !important;
            position: static !important;
            top: auto !important;
            left: auto !important;
            right: auto !important;
            bottom: auto !important;
            width: 100% !important;
            /* Match calc(100vh - 48px) inside maximized .chat-layout exactly */
            height: calc(100vh - 48px) !important;
            max-width: none !important;
            margin: 0 !important;
            border-radius: 0 !important;
            border: none !important;
            box-shadow: none !important;
        }}

        /* ── ANIMATIONS ───────────────────────────────────────────── */
        @keyframes slideInLeft {{
            from {{ transform: translateX(-16px); opacity: 0; }}
            to   {{ transform: translateX(0);     opacity: 1; }}
        }}

        @keyframes slideInItem {{
            from {{ transform: translateX(-8px); opacity: 0; }}
            to   {{ transform: translateX(0);    opacity: 1; }}
        }}

        @keyframes fadeInItem {{
            from {{ opacity: 0; }}
            to   {{ opacity: 1; }}
        }}

        /* ── RESPONSIVE ───────────────────────────────────────────── */
        @media (max-width: 768px) {{
            .fp-sidebar {{ display: none; }}
            .fp-login-left {{ display: none; }}
            .fp-login-right {{ width: 100%; }}
        }}
    </style>
    {component_script}
</head>
<body>
    <div class="fp-loading-bar" id="fpLoadingBar"></div>

    <!-- ══════════════════════════════════════════════════════════
         LOGIN SCREEN
    ══════════════════════════════════════════════════════════ -->
    <div id="loginContainer">

        <!-- Left: branding panel -->
        <div class="fp-login-left">
            <img class="fp-login-brand-logo" src="/img/fund_pilot.png" alt="FundPilot">
            <h1 class="fp-login-headline">Uw data,<br>beantwoord.</h1>
            <p class="fp-login-tagline">AI-gestuurde data-analyse voor uw fondsenwervingsteam.</p>
            <hr class="fp-login-rule">
        </div>

        <!-- Right: form panel -->
        <div class="fp-login-right">
            <div class="fp-login-form-inner">

                <div class="fp-login-form-header">
                    <img class="fp-login-form-logo" src="/img/fund_pilot.png" alt="FundPilot">
                    <span class="fp-login-form-brand-text">FundPilot</span>
                </div>

                <h2 class="fp-login-form-title">{'Inloggen' if supabase_url else 'Selecteer account'}</h2>

                {'<!-- Supabase real login form -->' if supabase_url else '<!-- Demo login form -->'}
                {_get_login_form_html(supabase_url)}

            </div>
        </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════
         APP SHELL (shown after login)
    ══════════════════════════════════════════════════════════ -->
    <div id="chatSections" class="hidden">

        <!-- Thin top bar -->
        <div class="fp-topbar">
            {('            <div style="font-size:11px;font-weight:500;letter-spacing:0.06em;text-transform:uppercase;color:#F0A500;margin-right:auto;padding-left:4px;">Dev</div>' if dev_mode else '')}
            <span class="fp-topbar-user" id="navUserDisplay" style="display:none;">
                Ingelogd als <strong id="navUserEmail"></strong>
            </span>
            <button class="fp-topbar-btn" id="navLogoutBtn" style="display:none;"
                    onclick="document.getElementById('logoutButton').click()">
                Uitloggen
            </button>
        </div>

        <!-- Main content: sidebar + chat -->
        <div class="fp-main">

            <!-- Sidebar -->
            <aside class="fp-sidebar">
                <div class="fp-sidebar-logo-area">
                    <img class="fp-sidebar-logo-img" src="/img/fund_pilot.png" alt="FundPilot">
                    <span class="fp-sidebar-logo-text">FundPilot</span>
                </div>

                <div class="fp-sidebar-body">

                    <!-- Navigation -->
                    <div>
                        <div class="fp-sidebar-overline">Analyse</div>
                        <a class="fp-sidebar-nav-item active" style="animation-delay:0ms;">
                            <!-- Chat icon -->
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                            </svg>
                            Chat
                        </a>
                    </div>

                    <div class="fp-sidebar-divider"></div>

                    <!-- Query history -->
                    <div class="fp-history-section">
                        <div class="fp-sidebar-overline">Recente vragen</div>
                        <div class="fp-history-list" id="historyList">
                            <div class="fp-history-empty">Nog geen vragen gesteld</div>
                        </div>
                    </div>

                    <!-- Clear history footer -->
                    <div class="fp-sidebar-footer" id="historyClearFooter" style="display:none;">
                        <button class="fp-clear-btn" id="clearHistoryBtn">Wissen</button>
                    </div>

                </div>
            </aside>

            <!-- Chat area -->
            <div class="fp-chat-area">

                <!-- Chat mount: vanna-chat injected here after login -->
                <div class="fp-chat-mount" id="chatMount"
                     data-api-base="{api_base_url}"
                     data-sse-endpoint="{api_base_url}/api/vanna/v2/chat_sse"
                     data-ws-endpoint="{api_base_url}/api/vanna/v2/chat_websocket"
                     data-poll-endpoint="{api_base_url}/api/vanna/v2/chat_poll">
                </div>

            </div><!-- /.fp-chat-area -->
        </div><!-- /.fp-main -->
    </div><!-- /#chatSections -->

    <!-- Hidden auth state trackers (used by auth scripts) -->
    <div id="loggedInStatus" style="display:none;">
        <span id="loggedInEmail"></span>
        <button id="logoutButton" style="display:none;"></button>
    </div>

    <!-- Auth script -->
    <script>
        {_get_auth_script(supabase_url, supabase_publishable_key)}
    </script>

    <!-- Shell interaction: history + suggestions -->
    <script>
    (function () {{
        'use strict';

        var HISTORY_KEY = 'fp_query_history';
        var MAX_HISTORY = 20;

        function loadHistory() {{
            try {{ return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); }}
            catch (e) {{ return []; }}
        }}

        function saveHistory(items) {{
            localStorage.setItem(HISTORY_KEY, JSON.stringify(items));
        }}

        function escapeHtml(s) {{
            return String(s)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;');
        }}

        function formatTs(ts) {{
            var d = new Date(ts);
            var now = new Date();
            var diffMin = Math.floor((now - d) / 60000);
            if (diffMin < 1) return 'Zojuist';
            if (diffMin < 60) return diffMin + 'm geleden';
            var diffH = Math.floor(diffMin / 60);
            if (diffH < 24) return diffH + 'u geleden';
            return d.toLocaleDateString('nl-NL', {{ day: 'numeric', month: 'short' }});
        }}

        function renderHistory() {{
            var list = document.getElementById('historyList');
            var footer = document.getElementById('historyClearFooter');
            if (!list) return;

            var items = loadHistory();

            if (items.length === 0) {{
                list.innerHTML = '<div class="fp-history-empty">Nog geen vragen gesteld</div>';
                if (footer) footer.style.display = 'none';
                return;
            }}

            if (footer) footer.style.display = '';
            list.innerHTML = '';

            items.forEach(function (item, i) {{
                var btn = document.createElement('button');
                btn.className = 'fp-history-item';
                btn.style.animationDelay = (i * 25) + 'ms';
                btn.innerHTML =
                    '<span class="fp-history-item-text">' + escapeHtml(item.text) + '</span>' +
                    '<span class="fp-history-item-ts">' + formatTs(item.ts) + '</span>';
                btn.addEventListener('click', function () {{
                    var chat = document.querySelector('vanna-chat');
                    if (chat) chat.sendMessage(item.text);
                }});
                list.appendChild(btn);
            }});
        }}

        function addToHistory(text) {{
            if (!text || !text.trim()) return;
            var items = loadHistory().filter(function (i) {{ return i.text !== text; }});
            items.unshift({{ text: text, ts: Date.now() }});
            saveHistory(items.slice(0, MAX_HISTORY));
            renderHistory();
        }}

        function setupChatListeners(chat) {{
            chat.addEventListener('message-sent', function (e) {{
                var text = e.detail && e.detail.message && e.detail.message.content;
                if (text) addToHistory(text);
            }});
        }}

        document.addEventListener('DOMContentLoaded', function () {{
            // Render existing history on load
            renderHistory();

            // Wire up clear history button
            var clearBtn = document.getElementById('clearHistoryBtn');
            if (clearBtn) {{
                clearBtn.addEventListener('click', function () {{
                    localStorage.removeItem(HISTORY_KEY);
                    renderHistory();
                }});
            }}

            // Watch for vanna-chat being added to DOM (created by auth script after login)
            var mount = document.getElementById('chatMount');
            if (mount) {{
                var observer = new MutationObserver(function (mutations) {{
                    mutations.forEach(function (m) {{
                        m.addedNodes.forEach(function (node) {{
                            if (node.tagName === 'VANNA-CHAT') {{
                                setupChatListeners(node);
                                observer.disconnect();
                            }}
                        }});
                    }});
                }});
                observer.observe(mount, {{ childList: true }});
            }}
        }});
    }})();
    </script>

    <script>
        // Fallback if web component fails to load
        if (!customElements.get('vanna-chat')) {{
            setTimeout(function() {{
                if (!customElements.get('vanna-chat')) {{
                    var el = document.querySelector('vanna-chat');
                    if (el) {{
                        el.innerHTML = '<div style="padding:40px;text-align:center;color:#7A7590;font-family:Outfit,sans-serif;">' +
                            '<p style="font-size:15px;margin:0 0 8px;">Component kon niet worden geladen.</p>' +
                            '<p style="font-size:13px;margin:0;">Controleer uw verbinding en herlaad de pagina.</p>' +
                            '</div>';
                    }}
                }}
            }}, 5000);
        }}
    </script>
</body>
</html>"""


def _get_login_form_html(supabase_url: str) -> str:
    """Return the login form HTML block (Supabase or demo)."""
    if supabase_url:
        return """
            <div id="step-password">
                <div class="mb-5">
                    <label for="emailInput" class="block mb-2 text-sm font-medium text-fp-black" style="font-size:14px;letter-spacing:0.01em;">E-mailadres</label>
                    <input type="email" id="emailInput" placeholder="u@voorbeeld.nl"
                        class="w-full px-5 py-4 text-sm border border-fp-edge rounded-sm focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:border-transparent bg-white" style="font-size:15px;" />
                </div>
                <div class="mb-6">
                    <label for="passwordInput" class="block mb-2 text-sm font-medium text-fp-black" style="font-size:14px;letter-spacing:0.01em;">Wachtwoord</label>
                    <input type="password" id="passwordInput" placeholder="••••••••"
                        class="w-full px-5 py-4 text-sm border border-fp-edge rounded-sm focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:border-transparent bg-white" style="font-size:15px;" />
                </div>
                <button id="loginButton"
                    class="w-full px-5 py-4 bg-fp-black text-white font-medium rounded-sm hover:bg-fp-violet border-l-[3px] border-l-fp-saffron focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:ring-offset-2 transition disabled:bg-gray-400 disabled:cursor-not-allowed" style="font-size:15px;letter-spacing:0.02em;">
                    Inloggen
                </button>
            </div>

            <div id="step-mfa" class="hidden">
                <p class="text-sm text-slate-600 mb-4">Voer de 6-cijferige code in vanuit uw authenticator-app.</p>
                <div class="mb-5">
                    <label for="totpInput" class="block mb-2 text-sm font-medium text-fp-black">2FA-code</label>
                    <input type="text" id="totpInput" placeholder="123456" maxlength="6" inputmode="numeric"
                        class="w-full px-4 py-3 text-sm border border-fp-edge rounded-sm focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:border-transparent bg-white tracking-widest text-center text-lg" />
                </div>
                <button id="verifyButton"
                    class="w-full px-4 py-3 bg-fp-black text-white text-sm font-medium rounded-sm hover:bg-fp-violet border-l-[3px] border-l-fp-saffron focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:ring-offset-2 transition disabled:bg-gray-400 disabled:cursor-not-allowed">
                    Verifieer
                </button>
            </div>

            <div id="step-mfa-enroll" class="hidden">
                <div class="text-center mb-4">
                    <p class="text-sm font-medium text-fp-black mb-2">Tweefactorauthenticatie instellen</p>
                    <p class="text-xs text-slate-500 mb-4">Scan de QR-code hieronder met uw authenticator-app (bijv. <span class="font-semibold text-blue-600">Microsoft Authenticator</span>)</p>
                    <div id="enrollQrCode" class="inline-block p-3 bg-white border border-slate-200 rounded-sm mb-3"></div>
                    <p class="text-xs text-slate-400">Of voer deze code handmatig in: <code id="enrollSecret" class="font-mono bg-slate-100 px-2 py-1 rounded text-xs select-all"></code></p>
                </div>
                <div class="mb-5">
                    <label for="enrollTotpInput" class="block mb-2 text-sm font-medium text-fp-black">Verificatiecode</label>
                    <input type="text" id="enrollTotpInput" placeholder="123456" maxlength="6" inputmode="numeric"
                        class="w-full px-4 py-3 text-sm border border-fp-edge rounded-sm focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:border-transparent bg-white tracking-widest text-center text-lg" />
                    <p class="text-xs text-slate-500 mt-2">Voer de 6-cijferige code in die in uw authenticator-app wordt getoond.</p>
                </div>
                <button id="enrollVerifyButton"
                    class="w-full px-4 py-3 bg-fp-black text-white text-sm font-medium rounded-sm hover:bg-fp-violet border-l-[3px] border-l-fp-saffron focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:ring-offset-2 transition disabled:bg-gray-400 disabled:cursor-not-allowed">
                    Verifieer &amp; 2FA activeren
                </button>
            </div>

            <div id="step-set-password" class="hidden">
                <p class="text-sm text-slate-600 mb-5">U bent uitgenodigd voor FundPilot. Stel een wachtwoord in voor uw account.</p>
                <div class="mb-5">
                    <label for="setPasswordInput" class="block mb-2 text-sm font-medium text-fp-black" style="font-size:14px;">Nieuw wachtwoord</label>
                    <input type="password" id="setPasswordInput" placeholder="Minimaal 8 tekens"
                        class="w-full px-5 py-4 text-sm border border-fp-edge rounded-sm focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:border-transparent bg-white" style="font-size:15px;" />
                </div>
                <div class="mb-6">
                    <label for="confirmPasswordInput" class="block mb-2 text-sm font-medium text-fp-black" style="font-size:14px;">Bevestig wachtwoord</label>
                    <input type="password" id="confirmPasswordInput" placeholder="Herhaal wachtwoord"
                        class="w-full px-5 py-4 text-sm border border-fp-edge rounded-sm focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:border-transparent bg-white" style="font-size:15px;" />
                </div>
                <button id="setPasswordButton"
                    class="w-full px-5 py-4 bg-fp-black text-white font-medium rounded-sm hover:bg-fp-violet border-l-[3px] border-l-fp-saffron focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:ring-offset-2 transition disabled:bg-gray-400 disabled:cursor-not-allowed" style="font-size:15px;">
                    Wachtwoord instellen
                </button>
            </div>

            <div id="loginError" class="hidden mt-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700"></div>
        """
    else:
        return """
            <div class="mb-5">
                <label for="emailInput" class="block mb-2 text-sm font-medium text-fp-black">E-mailadres</label>
                <select id="emailInput"
                    class="w-full px-4 py-3 text-sm border border-fp-edge rounded-sm focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:border-transparent bg-white">
                    <option value="">Selecteer een e-mailadres...</option>
                    <option value="admin@example.com">admin@example.com</option>
                    <option value="user@example.com">user@example.com</option>
                </select>
            </div>
            <button id="loginButton"
                class="w-full px-4 py-3 bg-fp-black text-white text-sm font-medium rounded-sm hover:bg-fp-violet border-l-[3px] border-l-fp-saffron focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:ring-offset-2 transition disabled:bg-gray-400 disabled:cursor-not-allowed">
                Doorgaan
            </button>
            <div class="mt-5 p-3 bg-fp-black/10 border-l-4 border-fp-saffron rounded text-xs text-fp-black leading-relaxed">
                <strong>Demomodus:</strong> Dit is een frontend-only authenticatiedemo.
                Uw e-mailadres wordt opgeslagen als cookie en automatisch meegestuurd met alle API-verzoeken.
            </div>
        """


def _get_auth_script(supabase_url: str, supabase_publishable_key: str) -> str:
    """Return the JS auth logic (Supabase or demo cookie)."""
    if supabase_url and supabase_publishable_key:
        return f"""
        // ── Supabase Authentication ────────────────────────────────────────
        // Read URL hash IMMEDIATELY — before any async code or Supabase SDK can clear it.
        // Supabase JS SDK processes and clears #access_token from the hash asynchronously
        // during createClient(), so we must capture the invite type before that happens.
        const _hashParams = new URLSearchParams(window.location.hash.substring(1));
        let _isInviteLink = _hashParams.get('type') === 'invite';
        if (_isInviteLink) {{
            sessionStorage.setItem('fp_invite_flow', 'true');
        }} else if (sessionStorage.getItem('fp_invite_flow') === 'true') {{
            _isInviteLink = true;
        }}
        const _hashErrorDesc = _hashParams.get('error_description');

        import('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm').then(({{ createClient }}) => {{
            const supabase = createClient('{supabase_url}', '{supabase_publishable_key}');
            let _totpFactorId      = null;
            let _inviteScreenShown = false;  // guard against double-handling

            const loginContainer    = document.getElementById('loginContainer');
            const loggedInStatus    = document.getElementById('loggedInStatus');
            const loggedInEmail     = document.getElementById('loggedInEmail');
            const chatSections      = document.getElementById('chatSections');
            const stepPassword      = document.getElementById('step-password');
            const stepMfa           = document.getElementById('step-mfa');
            const stepMfaEnroll     = document.getElementById('step-mfa-enroll');
            const stepSetPassword   = document.getElementById('step-set-password');
            const loginError        = document.getElementById('loginError');
            const loginButton       = document.getElementById('loginButton');
            const verifyButton      = document.getElementById('verifyButton');
            const enrollVerifyBtn   = document.getElementById('enrollVerifyButton');
            const setPasswordBtn    = stepSetPassword ? document.getElementById('setPasswordButton') : null;
            const logoutButton      = document.getElementById('logoutButton');

            // Helper: determine if MFA enrollment is needed after auth
            const _requireMfa = document.documentElement.dataset.requireMfa === 'true';

            const _startMfaEnroll = async () => {{
                const {{ data: enrollData, error: enrollError }} = await supabase.auth.mfa.enroll({{ factorType: 'totp' }});
                if (enrollError) {{ showError(enrollError.message); return false; }}
                _totpFactorId = enrollData.id;
                const qrContainer = document.getElementById('enrollQrCode');
                qrContainer.innerHTML = '';
                const qrImg = document.createElement('img');
                qrImg.src = enrollData.totp.qr_code;
                qrImg.alt = '2FA QR Code';
                qrImg.style.cssText = 'width:200px;height:200px;';
                qrContainer.appendChild(qrImg);
                document.getElementById('enrollSecret').textContent = enrollData.totp.secret;
                return true;
            }};

            const showError = (msg) => {{
                loginError.textContent = msg;
                loginError.classList.remove('hidden');
            }};
            const hideError = () => loginError.classList.add('hidden');

            if (_hashErrorDesc) {{
                showError(decodeURIComponent(_hashErrorDesc.replace(/\+/g, ' ')));
            }}

            const injectToken = (token, email) => {{
                // Dynamically create vanna-chat ONLY after successful auth.
                // Headers MUST be set BEFORE appending to DOM, because the
                // component fires requestStarterUI() in firstUpdated().
                const mount = document.getElementById('chatMount');
                let chat = mount.querySelector('vanna-chat');
                const isNew = !chat;
                if (isNew) {{
                    chat = document.createElement('vanna-chat');
                    chat.setAttribute('no-header', '');
                    chat.setAttribute('startingstate', 'maximized');
                    chat.setAttribute('api-base', mount.dataset.apiBase || '');
                    chat.setAttribute('sse-endpoint', mount.dataset.sseEndpoint || '');
                    chat.setAttribute('ws-endpoint', mount.dataset.wsEndpoint || '');
                    chat.setAttribute('poll-endpoint', mount.dataset.pollEndpoint || '');
                }}

                // Set auth header, then mount (order matters!)
                const mountAndShow = () => {{
                    chat.setAttribute('user-email', email || '');
                    chat.setCustomHeaders({{ 'Authorization': `Bearer ${{token}}` }});
                    if (isNew) mount.appendChild(chat);
                    loginContainer.classList.add('hidden');
                    loginContainer.style.display = 'none';
                    loggedInStatus.classList.remove('hidden');
                    chatSections.classList.remove('hidden');
                    loggedInEmail.textContent = email;
                    // Update top bar
                    const navEmail = document.getElementById('navUserEmail');
                    const navDisplay = document.getElementById('navUserDisplay');
                    const navLogout = document.getElementById('navLogoutBtn');
                    if (navEmail) navEmail.textContent = email;
                    if (navDisplay) navDisplay.style.display = '';
                    if (navLogout) navLogout.style.display = '';
                }};

                if (typeof chat.setCustomHeaders === 'function') {{
                    mountAndShow();
                }} else {{
                    // Component JS not loaded yet — wait for definition, then mount
                    customElements.whenDefined('vanna-chat').then(() => mountAndShow());
                }}
            }};

            // Show invite set-password screen (called from either getSession or onAuthStateChange)
            const _showInviteSetup = () => {{
                if (_inviteScreenShown) return;
                _inviteScreenShown = true;
                history.replaceState(null, '', window.location.pathname);
                stepPassword.classList.add('hidden');
                stepSetPassword.classList.remove('hidden');
                document.getElementById('setPasswordInput').focus();
            }};

            // Check for existing valid session on page load
            supabase.auth.getSession().then(async ({{ data }}) => {{
                const session = data?.session;
                if (session && session.user) {{
                    if (_isInviteLink) {{
                        _showInviteSetup();
                    }} else {{
                        const {{ data: aalData }} = await supabase.auth.mfa.getAuthenticatorAssuranceLevel();
                        const isAal1 = aalData?.currentLevel === 'aal1';
                        // Supabase AAL levels require aal2 if MFA is enrolled or if requireMfa is true and we enforce it
                        const {{ data: mfaData }} = await supabase.auth.mfa.listFactors();
                        const totpFactor = mfaData?.totp?.[0];
                        
                        if (isAal1 && (totpFactor || _requireMfa)) {{
                            if (totpFactor) {{
                                _totpFactorId = totpFactor.id;
                                stepPassword.classList.add('hidden');
                                stepMfa.classList.remove('hidden');
                                document.getElementById('totpInput').focus();
                            }} else {{
                                const ok = await _startMfaEnroll();
                                if (ok) {{
                                    stepPassword.classList.add('hidden');
                                    stepMfaEnroll.classList.remove('hidden');
                                    document.getElementById('enrollTotpInput').focus();
                                }}
                            }}
                        }} else {{
                            injectToken(session.access_token, session.user.email);
                        }}
                    }}
                }}
            }}).catch(err => console.error('Session restore failed:', err));

            // Set password (invite flow)
            if (setPasswordBtn) {{
                setPasswordBtn.addEventListener('click', async () => {{
                    hideError();
                    const pwd     = document.getElementById('setPasswordInput').value;
                    const confirm = document.getElementById('confirmPasswordInput').value;
                    if (pwd.length < 8) {{ showError('Wachtwoord moet minimaal 8 tekens bevatten.'); return; }}
                    if (pwd !== confirm) {{ showError('Wachtwoorden komen niet overeen.'); return; }}

                    setPasswordBtn.disabled = true;
                    setPasswordBtn.textContent = 'Bezig...';

                    const {{ error: updateError }} = await supabase.auth.updateUser({{ password: pwd }});
                    setPasswordBtn.disabled = false;
                    setPasswordBtn.textContent = 'Wachtwoord instellen';

                    if (updateError) {{ showError(updateError.message); return; }}

                    sessionStorage.removeItem('fp_invite_flow');
                    _isInviteLink = false;

                    // Password set — get fresh session, then handle MFA
                    const {{ data: sd }} = await supabase.auth.getSession();
                    const session = sd?.session;
                    if (!session) {{ showError('Er is een fout opgetreden. Probeer opnieuw in te loggen.'); return; }}

                    const {{ data: mfaData }} = await supabase.auth.mfa.listFactors();
                    const totpFactor = mfaData?.totp?.[0];

                    if (totpFactor) {{
                        _totpFactorId = totpFactor.id;
                        stepSetPassword.classList.add('hidden');
                        stepMfa.classList.remove('hidden');
                        document.getElementById('totpInput').focus();
                    }} else if (_requireMfa) {{
                        const ok = await _startMfaEnroll();
                        if (ok) {{
                            stepSetPassword.classList.add('hidden');
                            stepMfaEnroll.classList.remove('hidden');
                            document.getElementById('enrollTotpInput').focus();
                        }}
                    }} else {{
                        injectToken(session.access_token, session.user?.email || '');
                    }}
                }});
            }}

            // Token refresh + invite fallback handler
            supabase.auth.onAuthStateChange((event, session) => {{
                if ((event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') && session && session.user) {{
                    if (_isInviteLink && !_inviteScreenShown) {{
                        // Invite session arrived via onAuthStateChange (race condition fallback)
                        _showInviteSetup();
                    }} else if (!_isInviteLink) {{
                        const chat = document.querySelector('vanna-chat');
                        if (chat) {{
                            chat.setCustomHeaders({{ 'Authorization': `Bearer ${{session.access_token}}` }});
                        }}
                    }}
                }}
                if (event === 'SIGNED_OUT') {{
                    sessionStorage.removeItem('fp_invite_flow');
                    _isInviteLink = false;
                    // Remove vanna-chat from DOM to destroy cached state/tokens
                    const chat = document.querySelector('vanna-chat');
                    if (chat) chat.remove();
                    loginContainer.classList.remove('hidden');
                    loginContainer.style.display = '';
                    loggedInStatus.classList.add('hidden');
                    chatSections.classList.add('hidden');
                    // Hide top bar user info
                    const navDisplay = document.getElementById('navUserDisplay');
                    const navLogout = document.getElementById('navLogoutBtn');
                    if (navDisplay) navDisplay.style.display = 'none';
                    if (navLogout) navLogout.style.display = 'none';
                }}
            }});

            // Sign in with email + password
            loginButton.addEventListener('click', async () => {{
                hideError();
                const email    = document.getElementById('emailInput').value.trim();
                const password = document.getElementById('passwordInput').value;
                if (!email || !password) {{ showError('Voer uw e-mailadres en wachtwoord in.'); return; }}

                loginButton.disabled = true;
                loginButton.textContent = 'Bezig met inloggen...';

                const {{ data, error }} = await supabase.auth.signInWithPassword({{ email, password }});
                loginButton.disabled = false;
                loginButton.textContent = 'Inloggen';

                if (error) {{ showError(error.message); return; }}

                // Check if MFA is required (AAL1 → need AAL2)
                const {{ data: mfaData }} = await supabase.auth.mfa.listFactors();
                const totpFactor = mfaData?.totp?.[0];

                if (totpFactor) {{
                    // Store factor ID — challenge is created fresh on each verify attempt
                    _totpFactorId = totpFactor.id;

                    stepPassword.classList.add('hidden');
                    stepMfa.classList.remove('hidden');
                    document.getElementById('totpInput').focus();
                }} else if (!_requireMfa) {{
                    // No MFA enrolled and MFA not required — proceed directly
                    injectToken(data.session.access_token, email);
                }} else {{
                    // MFA required but not enrolled — start TOTP enrollment
                    const ok = await _startMfaEnroll();
                    if (ok) {{
                        stepPassword.classList.add('hidden');
                        stepMfaEnroll.classList.remove('hidden');
                        document.getElementById('enrollTotpInput').focus();
                    }}
                }}
            }});

            // Verify TOTP code
            verifyButton.addEventListener('click', async () => {{
                hideError();
                const code = document.getElementById('totpInput').value.trim();
                if (!code) {{ showError('Voer uw 2FA-code in.'); return; }}

                verifyButton.disabled = true;
                verifyButton.textContent = 'Bezig met verifiëren...';

                try {{
                    // Always create a fresh challenge — challenges are single-use,
                    // so a retry after a previous failure would 422 with the old one.
                    const {{ data: freshChallenge, error: chErr }} = await supabase.auth.mfa.challenge({{ factorId: _totpFactorId }});
                    if (chErr) {{
                        verifyButton.disabled = false;
                        verifyButton.textContent = 'Verifieer';
                        showError(chErr.message);
                        return;
                    }}

                    const {{ data, error }} = await supabase.auth.mfa.verify({{
                        factorId:    _totpFactorId,
                        challengeId: freshChallenge.id,
                        code,
                    }});
                    verifyButton.disabled = false;
                    verifyButton.textContent = 'Verifieer';

                    if (error) {{ showError(error.message); return; }}

                    // Supabase JS v2 may return the session as data.session or data
                    // itself may be the session object. Try both, then fall back to
                    // getSession().
                    let session = data?.session;
                    if (!session && data?.access_token) session = data;
                    if (!session) {{
                        const {{ data: sd }} = await supabase.auth.getSession();
                        session = sd?.session;
                    }}
                    if (!session) {{ showError('Verificatie geslaagd, maar de sessie kon niet worden opgehaald. Herlaad de pagina en probeer het opnieuw.'); return; }}
                    injectToken(session.access_token, session.user?.email || data?.user?.email || '');
                }} catch (err) {{
                    verifyButton.disabled = false;
                    verifyButton.textContent = 'Verifieer';
                    console.error('MFA verify error:', err);
                    showError('Er is een onverwachte fout opgetreden tijdens de verificatie.');
                }}
            }});

            // Verify enrollment TOTP code
            enrollVerifyBtn.addEventListener('click', async () => {{
                hideError();
                const code = document.getElementById('enrollTotpInput').value.trim();
                if (!code) {{ showError('Voer de 6-cijferige code in vanuit uw authenticator-app.'); return; }}

                enrollVerifyBtn.disabled = true;
                enrollVerifyBtn.textContent = 'Bezig met verifiëren...';

                try {{
                    // Challenge + verify to complete enrollment and elevate to AAL2
                    const {{ data: challengeData, error: challengeError }} = await supabase.auth.mfa.challenge({{ factorId: _totpFactorId }});
                    if (challengeError) {{
                        enrollVerifyBtn.disabled = false;
                        enrollVerifyBtn.textContent = 'Verifieer en 2FA activeren';
                        showError(challengeError.message);
                        return;
                    }}

                    const {{ data: verifyData, error: verifyError }} = await supabase.auth.mfa.verify({{
                        factorId:    _totpFactorId,
                        challengeId: challengeData.id,
                        code,
                    }});
                    enrollVerifyBtn.disabled = false;
                    enrollVerifyBtn.textContent = 'Verifieer en 2FA activeren';

                    if (verifyError) {{ showError(verifyError.message); return; }}

                    let session = verifyData?.session;
                    if (!session && verifyData?.access_token) session = verifyData;
                    if (!session) {{
                        const {{ data: sd }} = await supabase.auth.getSession();
                        session = sd?.session;
                    }}
                    if (!session) {{ showError('Verificatie geslaagd, maar de sessie kon niet worden opgehaald. Herlaad de pagina en probeer het opnieuw.'); return; }}
                    injectToken(session.access_token, session.user?.email || verifyData?.user?.email || '');
                }} catch (err) {{
                    enrollVerifyBtn.disabled = false;
                    enrollVerifyBtn.textContent = 'Verifieer en 2FA activeren';
                    console.error('MFA enrollment verify error:', err);
                    showError('Er is een onverwachte fout opgetreden tijdens de verificatie.');
                }}
            }});

            // Enter key support
            document.getElementById('passwordInput').addEventListener('keypress', (e) => {{ if (e.key === 'Enter') loginButton.click(); }});
            document.getElementById('totpInput').addEventListener('keypress',    (e) => {{ if (e.key === 'Enter') verifyButton.click(); }});
            document.getElementById('enrollTotpInput').addEventListener('keypress', (e) => {{ if (e.key === 'Enter') enrollVerifyBtn.click(); }});

            // Logout
            logoutButton.addEventListener('click', async () => {{
                sessionStorage.removeItem('fp_invite_flow');
                await supabase.auth.signOut();
                stepPassword.classList.remove('hidden');
                stepMfa.classList.add('hidden');
                stepMfaEnroll.classList.add('hidden');
                if (stepSetPassword) stepSetPassword.classList.add('hidden');
                document.getElementById('emailInput').value       = '';
                document.getElementById('passwordInput').value    = '';
                document.getElementById('totpInput').value        = '';
                document.getElementById('enrollTotpInput').value  = '';
                document.getElementById('setPasswordInput').value   = '';
                document.getElementById('confirmPasswordInput').value = '';
            }});
        }});
        """
    else:
        # Legacy demo cookie auth
        return """
        const getCookie = (name) => {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            return parts.length === 2 ? parts.pop().split(';').shift() : null;
        };
        const setCookie = (name, value) => {
            const expires = new Date(Date.now() + 365 * 864e5).toUTCString();
            document.cookie = `${name}=${value}; expires=${expires}; path=/; SameSite=Lax`;
        };
        const deleteCookie = (name) => {
            document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        };
        const showNavUser = (email) => {
            const navEmail = document.getElementById('navUserEmail');
            const navDisplay = document.getElementById('navUserDisplay');
            const navLogout = document.getElementById('navLogoutBtn');
            if (navEmail) navEmail.textContent = email;
            if (navDisplay) navDisplay.style.display = '';
            if (navLogout) navLogout.style.display = '';
        };
        const hideNavUser = () => {
            const navDisplay = document.getElementById('navUserDisplay');
            const navLogout = document.getElementById('navLogoutBtn');
            if (navDisplay) navDisplay.style.display = 'none';
            if (navLogout) navLogout.style.display = 'none';
        };
        const ensureChat = (email) => {
            const mount = document.getElementById('chatMount');
            if (!mount.querySelector('vanna-chat')) {
                const chat = document.createElement('vanna-chat');
                chat.setAttribute('no-header', '');
                chat.setAttribute('starting-state', 'maximized');
                chat.setAttribute('api-base', mount.dataset.apiBase || '');
                chat.setAttribute('sse-endpoint', mount.dataset.sseEndpoint || '');
                chat.setAttribute('ws-endpoint', mount.dataset.wsEndpoint || '');
                chat.setAttribute('poll-endpoint', mount.dataset.pollEndpoint || '');
                if (email) chat.setAttribute('user-email', email);
                mount.appendChild(chat);
            }
        };
        document.addEventListener('DOMContentLoaded', () => {
            const loginContainer = document.getElementById('loginContainer');
            const loggedInStatus = document.getElementById('loggedInStatus');
            const loggedInEmail  = document.getElementById('loggedInEmail');
            const chatSections   = document.getElementById('chatSections');
            const emailInput     = document.getElementById('emailInput');
            const loginButton    = document.getElementById('loginButton');
            const logoutButton   = document.getElementById('logoutButton');

            const email = getCookie('vanna_email');
            if (email) {
                loginContainer.classList.add('hidden');
                loginContainer.style.display = 'none';
                loggedInStatus.classList.remove('hidden');
                chatSections.classList.remove('hidden');
                loggedInEmail.textContent = email;
                showNavUser(email);
                ensureChat(email);
            }
            loginButton.addEventListener('click', () => {
                const email = emailInput.value.trim();
                if (!email) { alert('Selecteer een e-mailadres'); return; }
                setCookie('vanna_email', email);
                loginContainer.classList.add('hidden');
                loginContainer.style.display = 'none';
                loggedInStatus.classList.remove('hidden');
                chatSections.classList.remove('hidden');
                loggedInEmail.textContent = email;
                showNavUser(email);
                ensureChat(email);
            });
            logoutButton.addEventListener('click', () => {
                deleteCookie('vanna_email');
                loginContainer.classList.remove('hidden');
                loginContainer.style.display = '';
                loggedInStatus.classList.add('hidden');
                hideNavUser();
                chatSections.classList.add('hidden');
                emailInput.value = '';
            });
            emailInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') loginButton.click(); });
        });
        """


# Backward compatibility - default production HTML
INDEX_HTML = get_index_html()
