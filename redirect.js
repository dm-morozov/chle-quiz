(() => {
    const TARGET_URL = 'https://pilotspace.ru/';
    const TOTAL_SECONDS = 30;
    let remaining = TOTAL_SECONDS;
    let isPaused = false;
    let timerId = null;

    const secondsEl = document.getElementById('timer-seconds');
    const progressFill = document.getElementById('progress-fill');
    const pauseBtn = document.getElementById('pause-btn');
    const pauseBtnText = document.getElementById('pause-btn-text');
    const copyBtn = document.getElementById('copy-btn');
    const copyStatus = document.getElementById('copy-status');

    function updateUi() {
        if (secondsEl) {
            secondsEl.textContent = remaining;
        }
        if (progressFill) {
            const percent = (remaining / TOTAL_SECONDS) * 100;
            progressFill.style.width = `${percent}%`;
        }
    }

    function tick() {
        if (isPaused) return;

        remaining--;
        if (remaining <= 0) {
            remaining = 0;
            updateUi();
            clearInterval(timerId);
            window.location.replace(TARGET_URL);
            return;
        }
        updateUi();
    }

    function togglePause() {
        isPaused = !isPaused;
        if (pauseBtnText) {
            pauseBtnText.textContent = isPaused ? 'Продолжить' : 'Пауза';
        }
        if (pauseBtn) {
            pauseBtn.setAttribute('aria-pressed', String(isPaused));
            pauseBtn.title = isPaused ? 'Возобновить обратный отсчёт' : 'Приостановить обратный отсчёт';
        }
    }

    function init() {
        updateUi();
        timerId = setInterval(tick, 1000);

        if (pauseBtn) {
            pauseBtn.addEventListener('click', togglePause);
        }

        if (copyBtn) {
            copyBtn.addEventListener('click', async () => {
                try {
                    await navigator.clipboard.writeText(TARGET_URL);
                    if (copyStatus) {
                        copyStatus.textContent = 'Ссылка скопирована!';
                        setTimeout(() => {
                            copyStatus.textContent = 'Скопировать';
                        }, 2500);
                    }
                } catch {
                    // Fallback
                    const input = document.createElement('input');
                    input.value = TARGET_URL;
                    document.body.appendChild(input);
                    input.select();
                    document.execCommand('copy');
                    document.body.removeChild(input);
                    if (copyStatus) {
                        copyStatus.textContent = 'Ссылка скопирована!';
                        setTimeout(() => {
                            copyStatus.textContent = 'Скопировать';
                        }, 2500);
                    }
                }
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
