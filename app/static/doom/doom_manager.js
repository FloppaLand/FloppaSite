const KEYCODE_REMAPPING = {
    38: 87, // W
    37: 65, // A
    40: 83, // S
    39: 68, // D
    188: 81, // Q
    190: 69 //E
}

document.addEventListener("touchstart", (e) => {
    const canvasContainer = document.querySelector(
        ".captcha-canvas-container",
    );
    if (
        !canvasContainer.contains(e.target) &&
        captchaContainer.matches(":focus")
    ) {
        captchaContainer.blur();
    }
});

const canvas = document.getElementById("canvas");
const statusElement = document.getElementById("status");
const progressElement = document.getElementById("progress");
const verifyButton = document.getElementById("verify-button");
const captchaContainer = document.querySelector(".captcha-container");
const refreshButton = document.getElementById("refresh-button");
const SkinForm = document.getElementById("SkinForm")

SkinForm.onsubmit = function ()
{ 
  captchaContainer.style.display = "block"
  return false
}

let enemiesKilled = 0;


function restartGame() {
    enemiesKilled = 0;
    updateVerifyButton();

    // Track game start
    va("event", { name: "game_start" });

    // Call the native DOOM restart function directly
    Module["_G_DoReborn"]();
}

function updateVerifyButton() {
    const verifySpan = verifyButton.querySelector("span");
    verifySpan.textContent = `${enemiesKilled}/3`;
    verifyButton.setAttribute(
        "aria-label",
        `Verify, ${enemiesKilled} out of 3 monsters killed`,
    );

    if (enemiesKilled >= 3) {
        verifyButton.style.backgroundColor = "#4285f4";
        verifyButton.style.color = "white";
        verifyButton.style.cursor = "pointer";
    } else {
        verifyButton.style.backgroundColor = "#f0f0f0";
        verifyButton.style.color = "#888";
        verifyButton.style.cursor = "default";
    }
}

// prevent losing focus when it's tapped
refreshButton.addEventListener("mousedown", (e) => {
    e.preventDefault();
});

refreshButton.addEventListener("click", (e) => {
    e.preventDefault();
    captchaContainer.focus();
    restartGame();
});

function showSuccess() {

    // Track successful solve
    va("event", { name: "captcha_solved", data: { kills: enemiesKilled } });

    // Pause the game
    Module.pauseMainLoop();

    // Hide the captcha container completely
    captchaContainer.style.display = "none";

    SkinForm.submit()

}

captchaContainer.addEventListener("focus", () => {
    va("event", { name: "game_resume" });
    Module.resumeMainLoop();
});

captchaContainer.addEventListener("blur", () => {
    va("event", { name: "game_pause" });
    Module.pauseMainLoop();
});

// Mobile controls handling
const mobileControls = {
    up: { keyCode: 38 }, // Arrow Up
    down: { keyCode: 40 }, // Arrow Down
    left: { keyCode: 37 }, // Arrow Left
    right: { keyCode: 39 }, // Arrow Right
    fire: { keyCode: 32 }, // Space
};

function ensureGameFocused() {
    if (!captchaContainer.matches(":focus")) {
        captchaContainer.focus();
    }
}

function simulateKeyEvent(type, keyCode) {
    const event = new KeyboardEvent(type, {
        keyCode: keyCode,
        bubbles: true,
        cancelable: true,
    });
    captchaContainer.dispatchEvent(event);
}

function handleTouchStart(key) {
    return (e) => {
        e.preventDefault();
        ensureGameFocused();
        simulateKeyEvent("keydown", mobileControls[key].keyCode);
    };
}

function handleTouchEnd(key) {
    return (e) => {
        e.preventDefault();
        ensureGameFocused();
        simulateKeyEvent("keyup", mobileControls[key].keyCode);
    };
}

// Ensure controls are clickable even when game is not focused
document.querySelector(".mobile-controls").addEventListener(
    "touchstart",
    (e) => {
        ensureGameFocused();
    },
    { passive: false },
);

// Setup touch controls
document
    .querySelectorAll(".d-pad button, .fire-button")
    .forEach((button) => {
        let key = button.className.split(" ")[0];
        if (!key || key === "fire-button") key = "fire";

        button.addEventListener("touchstart", handleTouchStart(key));
        button.addEventListener("touchend", handleTouchEnd(key));
        button.addEventListener("touchcancel", handleTouchEnd(key));
    });

var Module = {
    keyboardListeningElement: captchaContainer,
    arguments: [
        "-autoreborn",
        "-nomenu",
        "-fast",
        "-skill",
        "6",
        "-warp",
        "e1m1",
    ],
    preRun: [
        function () {
            SDL.defaults.copyOnLock = false;

            // Store the original lookupKeyCodeForEvent function
            const originalLookupKeyCodeForEvent = SDL.lookupKeyCodeForEvent;

            // Create a wrapper that modifies key behavior
            SDL.lookupKeyCodeForEvent = function (event) {
                // Ignore Escape key by returning 0
                if (event.keyCode === 27) {
                    captchaContainer.blur();
                    return 0;
                }

                // Ignore Ctrl key by returning 0
                if (event.keyCode === 17) {
                    return 0;
                }

                // Treat Spacebar (keyCode 32) as Ctrl
                if (event.keyCode === 32) {
                    return originalLookupKeyCodeForEvent({ ...event, keyCode: 17 });
                }

                if (event.keyCode === 38) {
                    return originalLookupKeyCodeForEvent({ ...event, keyCode: 17 });
                }

                for (const [key, value] of Object.entries(KEYCODE_REMAPPING)) {
                    if (event.keyCode === value) {
                    return originalLookupKeyCodeForEvent({ ...event, keyCode: key });
                }
                }

                if (event.keyCode === 32) {
                    return originalLookupKeyCodeForEvent({ ...event, keyCode: 17 });
                }

                // For all other keys, use the original function
                return originalLookupKeyCodeForEvent(event);
            };
        },
    ],
    postRun: [],
    onPlayerBorn: function () {
        document
            .querySelector(".status-message.death")
            .classList.remove("visible");
    },
    onPlayerDeath: function () {
        va("event", { name: "player_death", data: { kills: enemiesKilled } });
        enemiesKilled = 0;
        updateVerifyButton();
        document
            .querySelector(".status-message.death")
            .classList.add("visible");
    },
    onEnemyKilled: function () {
        enemiesKilled++;
        va("event", { name: "enemy_killed", data: { kills: enemiesKilled } });
        updateVerifyButton();

        // Get the icon path
        const iconPath = verifyButton.querySelector(
            ".captcha-verify-icon",
        );

        // Reset animations
        verifyButton.style.animation = "none";
        iconPath.style.animation = "none";
        verifyButton.offsetHeight; // Trigger reflow

        // Set end colors based on kill count
        const isComplete = enemiesKilled >= 3;
        verifyButton.style.setProperty(
            "--end-color",
            isComplete ? "#4285f4" : "#f0f0f0",
        );
        iconPath.style.setProperty(
            "--end-icon-color",
            isComplete ? "white" : "#888888",
        );

        // Trigger animations
        verifyButton.style.animation = "killFlash 0.8s ease forwards";
        iconPath.style.animation = "iconFlash 0.5s ease forwards";

        // Show success message when 3 enemies are killed
        if (enemiesKilled === 3) {
            showSuccess();
        }
    },
    print: function (text) {
        if (arguments.length > 1)
            text = Array.prototype.slice.call(arguments).join(" ");
        console.log(text);
    },
    printErr: function (text) {
        if (arguments.length > 1)
            text = Array.prototype.slice.call(arguments).join(" ");
        console.error(text);
    },
    canvas: canvas,
    setStatus: function (text) {
        if (!Module.setStatus.last)
            Module.setStatus.last = { time: Date.now(), text: "" };
        if (text === Module.setStatus.last.text) return;
        const m = text.match(/([^(]+)$$(\d+(\.\d+)?)\/(\d+)$$/);
        const now = Date.now();
        if (m && now - Module.setStatus.last.time < 30) return;
        Module.setStatus.last.time = now;
        Module.setStatus.last.time = now;
        Module.setStatus.last.text = text;
        if (m) {
            text = m[1];
            progressElement.value = parseInt(m[2]) * 100;
            progressElement.max = parseInt(m[4]) * 100;
            progressElement.hidden = false;
        } else {
            progressElement.value = null;
            progressElement.max = null;
            progressElement.hidden = true;
        }
        statusElement.innerHTML = text;
    },
    totalDependencies: 0,
    monitorRunDependencies: function (left) {
        this.totalDependencies = Math.max(this.totalDependencies, left);
        Module.setStatus(
            left
                ? "Подготовка... (" +
                (this.totalDependencies - left) +
                "/" +
                this.totalDependencies +
                ")"
                : "Загрузка завершена.",
        );
    },
};
Module.setStatus("Загрузка...");
window.onerror = function () {
    Module.setStatus("Ошибка");
    Module.setStatus = function (text) {
        if (text) Module.printErr("[post-exception status] " + text);
    };
};