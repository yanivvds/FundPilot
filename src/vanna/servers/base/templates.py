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
        body {{
            background: #F5F3EF;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
            font-family: 'Outfit', ui-sans-serif, system-ui, sans-serif;
            color: #1E1B26;
            margin: 0;
        }}

        body::before {{
            content: '';
            position: fixed;
            inset: 0;
            z-index: -1;
            background-image:
                linear-gradient(rgba(226, 223, 216, 0.4) 1px, transparent 1px),
                linear-gradient(90deg, rgba(226, 223, 216, 0.4) 1px, transparent 1px);
            background-size: 48px 48px;
            mask-image: radial-gradient(ellipse 80% 60% at 50% 40%, black 30%, transparent 70%);
            -webkit-mask-image: radial-gradient(ellipse 80% 60% at 50% 40%, black 30%, transparent 70%);
        }}

        /* FundPilot Navigation Bar */
        .fp-nav {{
            background: #141218;
            height: 56px;
            display: flex;
            align-items: center;
            padding: 0 24px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .fp-nav-logo {{
            font-family: 'Outfit', sans-serif;
            font-size: 15px;
            font-weight: 600;
            color: #FFFFFF;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .fp-nav-logo .fp-logo-mark {{
            height: 28px;
            width: auto;
            border-radius: 2px;
        }}

        .fp-nav-right {{
            margin-left: auto;
            display: flex;
            align-items: center;
            gap: 16px;
        }}

        .fp-nav-user {{
            font-size: 13px;
            color: rgba(255, 255, 255, 0.7);
            font-weight: 400;
        }}

        .fp-nav-user strong {{
            color: #FFFFFF;
            font-weight: 500;
        }}

        .fp-nav-btn {{
            padding: 6px 14px;
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 2px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 12px;
            font-weight: 500;
            font-family: 'Outfit', sans-serif;
            cursor: pointer;
            transition: all 0.15s ease;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .fp-nav-btn:hover {{
            color: #F0A500;
            border-color: rgba(240, 165, 0, 0.3);
        }}

        /* Loading bar */
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

        /* Chat container */
        .fp-chat-wrapper {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px;
        }}

        vanna-chat {{
            width: 100%;
            height: 100%;
            display: block;
        }}
    </style>
    {component_script}
</head>
<body>
    <!-- FundPilot Navigation -->
    <nav class="fp-nav" id="fpNav">
        <div class="fp-nav-logo">
            <img class="fp-logo-mark" src="/img/fund_pilot.png" alt="FundPilot">
            FundPilot
        </div>
        <div class="fp-nav-right">
            <span class="fp-nav-user" id="navUserDisplay" style="display:none;">
                <strong id="navUserEmail"></strong>
            </span>
            <button class="fp-nav-btn" id="navLogoutBtn" style="display:none;" onclick="document.getElementById('logoutButton').click()">
                Uitloggen
            </button>
        </div>
    </nav>

    {('    <div style="max-width:1200px;margin:0 auto;padding:12px 24px 0;"><div style="background:rgba(255,179,0,0.08);border:1px solid rgba(255,179,0,0.2);border-left:3px solid #F0A500;border-radius:2px;padding:10px 16px;font-size:13px;color:#D4920A;font-weight:500;">Development Mode: Loading components from local assets</div></div>' if dev_mode else "")}

    <!-- Login Form (shown before auth) -->
    <div id="loginContainer" style="max-width:420px;margin:120px auto 0;padding:0 24px;">
        <div style="background:#FFFFFF;border:1px solid #E2DFD8;border-radius:4px;padding:40px 32px;box-shadow:0 2px 8px rgba(20,18,24,0.06),0 12px 32px rgba(20,18,24,0.04);">
            <div style="text-align:center;margin-bottom:32px;">
                <img src="/img/fund_pilot.png" alt="FundPilot" style="height:80px;width:auto;margin-bottom:16px;display:block;margin-left:auto;margin-right:auto;">
                <h2 style="font-family:Fraunces,serif;font-size:24px;font-weight:600;color:#141218;margin:0 0 8px;letter-spacing:-0.01em;">Inloggen</h2>
                <p style="font-size:14px;color:#7A7590;margin:0;" id="loginSubtitle">{'Voer uw gegevens in om door te gaan' if supabase_url else 'Selecteer uw e-mailadres om in te loggen'}</p>
            </div>

            {'<!-- Supabase real login form -->' if supabase_url else '<!-- Demo login form -->'}
            {_get_login_form_html(supabase_url)}
        </div>
    </div>

    <!-- Hidden logged-in status tracker (used by nav) -->
    <div id="loggedInStatus" class="hidden" style="display:none;">
        <span id="loggedInEmail"></span>
        <button id="logoutButton" style="display:none;"></button>
    </div>

    <!-- Chat Container (shown after auth) -->
    <div id="chatSections" class="hidden">
        <div class="fp-chat-wrapper">
            <div id="chatMount"
                 data-api-base="{api_base_url}"
                 data-sse-endpoint="{api_base_url}/api/vanna/v2/chat_sse"
                 data-ws-endpoint="{api_base_url}/api/vanna/v2/chat_websocket"
                 data-poll-endpoint="{api_base_url}/api/vanna/v2/chat_poll">
                <!-- vanna-chat is NOT rendered until login succeeds -->
            </div>
        </div>
    </div>

    <script>
        {_get_auth_script(supabase_url, supabase_publishable_key)}
    </script>

    <script>
        // Artifact demo event listener
        document.addEventListener('DOMContentLoaded', () => {{
            const vannaChat = document.querySelector('vanna-chat');

            if (vannaChat) {{
                // Add artifact event listener to demonstrate external rendering
                vannaChat.addEventListener('artifact-opened', (event) => {{
                    const {{ artifactId, type, title, trigger }} = event.detail;

                    console.log('🎨 Artifact Event:', {{ artifactId, type, title, trigger }});

                    // For demo: open all artifacts externally
                    setTimeout(() => {{
                        const newWindow = window.open('', '_blank', 'width=900,height=700');
                        if (newWindow) {{
                            newWindow.document.write(event.detail.getStandaloneHTML());
                            newWindow.document.close();
                            newWindow.document.title = title || 'Vanna Artifact';
                            console.log(`📱 Opened ${{title}} in new window`);
                        }}
                    }}, 100);

                    // Prevent default in-chat rendering
                    event.detail.preventDefault();
                    console.log('✋ Showing placeholder in chat instead of full artifact');
                }});

                console.log('🎯 Artifact demo mode: All artifacts will open externally');
            }}
        }});

        // Fallback if web component doesn't load (only after login creates the element)
        if (!customElements.get('vanna-chat')) {{
            setTimeout(() => {{
                if (!customElements.get('vanna-chat')) {{
                    const el = document.querySelector('vanna-chat');
                    if (el) {{
                        el.innerHTML = `
                            <div class="p-10 text-center text-gray-600">
                                <h3 class="text-xl font-semibold mb-2">Vanna Chat Component</h3>
                                <p class="mb-2">Web component failed to load. Please check your connection.</p>
                                <p class="text-sm text-gray-400">
                                    {("Loading from: local static assets" if dev_mode else f"Loading from: {cdn_url}")}
                                </p>
                            </div>
                        `;
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
                <div class="mb-4">
                    <label for="emailInput" class="block mb-2 text-sm font-medium text-fp-black">E-mailadres</label>
                    <input type="email" id="emailInput" placeholder="u@voorbeeld.nl"
                        class="w-full px-4 py-3 text-sm border border-fp-edge rounded-sm focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:border-transparent bg-white" />
                </div>
                <div class="mb-5">
                    <label for="passwordInput" class="block mb-2 text-sm font-medium text-fp-black">Wachtwoord</label>
                    <input type="password" id="passwordInput" placeholder="••••••••"
                        class="w-full px-4 py-3 text-sm border border-fp-edge rounded-sm focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:border-transparent bg-white" />
                </div>
                <button id="loginButton"
                    class="w-full px-4 py-3 bg-fp-black text-white text-sm font-medium rounded-sm hover:bg-fp-violet border-l-[3px] border-l-fp-saffron focus:outline-none focus:ring-2 focus:ring-fp-saffron focus:ring-offset-2 transition disabled:bg-gray-400 disabled:cursor-not-allowed">
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
                    <p class="text-xs text-slate-500 mb-4">Scan de QR-code hieronder met uw authenticator-app (Google Authenticator, Authy, 1Password, etc.)</p>
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
        import('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm').then(({{ createClient }}) => {{
            const supabase = createClient('{supabase_url}', '{supabase_publishable_key}');
            let _totpFactorId = null;

            const loginContainer    = document.getElementById('loginContainer');
            const loggedInStatus    = document.getElementById('loggedInStatus');
            const loggedInEmail     = document.getElementById('loggedInEmail');
            const chatSections      = document.getElementById('chatSections');
            const stepPassword      = document.getElementById('step-password');
            const stepMfa           = document.getElementById('step-mfa');
            const stepMfaEnroll     = document.getElementById('step-mfa-enroll');
            const loginError        = document.getElementById('loginError');
            const loginButton       = document.getElementById('loginButton');
            const verifyButton      = document.getElementById('verifyButton');
            const enrollVerifyBtn   = document.getElementById('enrollVerifyButton');
            const logoutButton      = document.getElementById('logoutButton');

            const showError = (msg) => {{
                loginError.textContent = msg;
                loginError.classList.remove('hidden');
            }};
            const hideError = () => loginError.classList.add('hidden');

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
                    // Update nav bar
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

            // Check for existing valid session on page load
            supabase.auth.getSession().then(({{ data }}) => {{
                const session = data?.session;
                if (session && session.user) {{
                    injectToken(session.access_token, session.user.email);
                }}
            }}).catch(err => console.error('Session restore failed:', err));

            // Auto-refresh token and re-inject when Supabase rotates it
            supabase.auth.onAuthStateChange((event, session) => {{
                if ((event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') && session) {{
                    const chat = document.querySelector('vanna-chat');
                    if (chat) {{
                        chat.setCustomHeaders({{ 'Authorization': `Bearer ${{session.access_token}}` }});
                    }}
                }}
                if (event === 'SIGNED_OUT') {{
                    // Remove vanna-chat from DOM to destroy cached state/tokens
                    const chat = document.querySelector('vanna-chat');
                    if (chat) chat.remove();
                    loginContainer.classList.remove('hidden');
                    loginContainer.style.display = '';
                    loggedInStatus.classList.add('hidden');
                    chatSections.classList.add('hidden');
                    // Hide nav user info
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
                }} else if (document.documentElement.dataset.requireMfa !== 'true') {{
                    // No MFA enrolled and MFA not required — proceed directly
                    injectToken(data.session.access_token, email);
                }} else {{
                    // MFA required but not enrolled — start TOTP enrollment
                    const {{ data: enrollData, error: enrollError }} = await supabase.auth.mfa.enroll({{ factorType: 'totp' }});
                    if (enrollError) {{ showError(enrollError.message); return; }}
                    _totpFactorId = enrollData.id;

                    // Show QR code for the user to scan
                    const qrContainer = document.getElementById('enrollQrCode');
                    qrContainer.innerHTML = '';
                    const qrImg = document.createElement('img');
                    qrImg.src = enrollData.totp.qr_code;
                    qrImg.alt = '2FA QR Code';
                    qrImg.style.width = '200px';
                    qrImg.style.height = '200px';
                    qrContainer.appendChild(qrImg);
                    document.getElementById('enrollSecret').textContent = enrollData.totp.secret;

                    stepPassword.classList.add('hidden');
                    stepMfaEnroll.classList.remove('hidden');
                    document.getElementById('enrollTotpInput').focus();
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
                await supabase.auth.signOut();
                stepPassword.classList.remove('hidden');
                stepMfa.classList.add('hidden');
                stepMfaEnroll.classList.add('hidden');
                document.getElementById('emailInput').value       = '';
                document.getElementById('passwordInput').value    = '';
                document.getElementById('totpInput').value        = '';
                document.getElementById('enrollTotpInput').value  = '';
            }});
        }});
        """
    else:
        # Legacy demo cookie auth
        return """
        const getCookie = (name) => {{
            const value = `; ${{document.cookie}}`;
            const parts = value.split(`; ${{name}}=`);
            return parts.length === 2 ? parts.pop().split(';').shift() : null;
        }};
        const setCookie = (name, value) => {{
            const expires = new Date(Date.now() + 365 * 864e5).toUTCString();
            document.cookie = `${{name}}=${{value}}; expires=${{expires}}; path=/; SameSite=Lax`;
        }};
        const deleteCookie = (name) => {{
            document.cookie = `${{name}}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        }};
        const showNavUser = (email) => {{
            const navEmail = document.getElementById('navUserEmail');
            const navDisplay = document.getElementById('navUserDisplay');
            const navLogout = document.getElementById('navLogoutBtn');
            if (navEmail) navEmail.textContent = email;
            if (navDisplay) navDisplay.style.display = '';
            if (navLogout) navLogout.style.display = '';
        }};
        const hideNavUser = () => {{
            const navDisplay = document.getElementById('navUserDisplay');
            const navLogout = document.getElementById('navLogoutBtn');
            if (navDisplay) navDisplay.style.display = 'none';
            if (navLogout) navLogout.style.display = 'none';
        }};
        const ensureChat = (email = '') => {{
            const mount = document.getElementById('chatMount');
            if (!mount.querySelector('vanna-chat')) {{
                const chat = document.createElement('vanna-chat');
                chat.setAttribute('no-header', '');
                chat.setAttribute('api-base', mount.dataset.apiBase || '');
                chat.setAttribute('sse-endpoint', mount.dataset.sseEndpoint || '');
                chat.setAttribute('ws-endpoint', mount.dataset.wsEndpoint || '');
                chat.setAttribute('poll-endpoint', mount.dataset.pollEndpoint || '');
                if (email) chat.setAttribute('user-email', email);
                mount.appendChild(chat);
            }}
        }};
        }};
        document.addEventListener('DOMContentLoaded', () => {{
            const email = getCookie('vanna_email');
            if (email) {{
                loginContainer.classList.add('hidden');
                loginContainer.style.display = 'none';
                loggedInStatus.classList.remove('hidden');
                chatSections.classList.remove('hidden');
                loggedInEmail.textContent = email;
                showNavUser(email);
                ensureChat(email);
            }}
            loginButton.addEventListener('click', () => {{
                const email = emailInput.value.trim();
                if (!email) {{ alert('Selecteer een e-mailadres'); return; }}
                setCookie('vanna_email', email);
                loginContainer.classList.add('hidden');
                loginContainer.style.display = 'none';
                loggedInStatus.classList.remove('hidden');
                chatSections.classList.remove('hidden');
                loggedInEmail.textContent = email;
                showNavUser(email);
                ensureChat(email);
            }});
            logoutButton.addEventListener('click', () => {{
                deleteCookie('vanna_email');
                loginContainer.classList.remove('hidden');
                loginContainer.style.display = '';
                loggedInStatus.classList.add('hidden');
                hideNavUser();
                chatSections.classList.add('hidden');
                emailInput.value = '';
            }});
            emailInput.addEventListener('keypress', (e) => {{ if (e.key === 'Enter') loginButton.click(); }});
        }});
        """


# Backward compatibility - default production HTML
INDEX_HTML = get_index_html()
