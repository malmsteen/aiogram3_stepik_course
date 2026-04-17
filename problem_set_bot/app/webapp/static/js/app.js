const tg = window.Telegram?.WebApp;
tg?.ready?.();

let hasChanges = false;
let originalCheckedState = [];

// Получаем данные из шаблона
const position = window.APP_CONFIG?.position || 0;

// Определяем десктоп
const isDesktop = tg?.platform === "tdesktop" || tg?.platform === "web";
console.info(
  "[WebApp] platform:",
  tg?.platform || "unknown",
  "isDesktop:",
  isDesktop,
);
console.info("[WebApp] initData length:", (tg?.initData || "").length);

// ========== ЗАГРУЗКА ДАННЫХ ==========
async function loadData() {
  // Сервер уже отрендерил чекбоксы с правильными отметками
  // (на основе параметра cart в URL). Никаких API-запросов не нужно.
  console.info("[WebApp] page loaded, position:", position);

  // Добавляем слушатели на чекбоксы
  document.querySelectorAll('input[type="checkbox"]').forEach((cb) => {
    cb.removeEventListener("change", checkChanges);
    cb.addEventListener("change", checkChanges);
  });

  // Сбрасываем трекинг (запоминаем исходное состояние чекбоксов)
  resetChangesTracking();
}

// ========== УПРАВЛЕНИЕ КНОПКОЙ И ЗАКРЫТИЕМ ==========
function closeWebApp() {
  // На десктопе tg.close не работает, просто показываем сообщение
  if (isDesktop) {
    notify("Закройте окно крестиком в правом верхнем углу.");
    return;
  }
  try {
    if (tg?.close) {
      tg.close();
      return;
    }
  } catch (error) {
    console.error("tg.close failed", error);
  }
  // Fallback для браузеров
  window.close();
  setTimeout(() => {
    if (document.visibilityState === "visible") {
      history.back();
    }
  }, 150);
}

function notify(message) {
  if (tg?.showAlert) {
    tg.showAlert(message);
    return;
  }
  alert(message);
}

function updateButton() {
  const btn = document.getElementById("save-btn");
  if (!btn) return;
  if (hasChanges) {
    btn.textContent = "💾 Сохранить изменения";
    btn.onclick = sendUpdate;
    if (tg?.enableClosingConfirmation) tg.enableClosingConfirmation();
  } else {
    btn.textContent = "✖️ Закрыть";
    btn.onclick = closeWebApp;
    if (tg?.disableClosingConfirmation) tg.disableClosingConfirmation();
  }
}

function checkChanges() {
  const current = Array.from(
    document.querySelectorAll('input[type="checkbox"]'),
  ).map((cb) => cb.checked);
  const changed =
    JSON.stringify(current) !== JSON.stringify(originalCheckedState);
  if (changed !== hasChanges) {
    hasChanges = changed;
    updateButton();
  }
}

function resetChangesTracking() {
  originalCheckedState = Array.from(
    document.querySelectorAll('input[type="checkbox"]'),
  ).map((cb) => cb.checked);
  hasChanges = false;
  updateButton();
}

// ========== СОХРАНЕНИЕ ==========
async function sendUpdate() {
  const initData = tg?.initData || "";
  const selected = Array.from(
    document.querySelectorAll('input[type="checkbox"]:checked'),
  ).map((cb) => cb.dataset.id);

  // Основной путь: отправляем initData на сервер
  if (initData) {
    const payload = {
      initData: initData,
      cart: selected,
      position: position > 0 ? position : undefined,
    };
    console.info("[WebApp] sending update_cart", {
      initDataLength: initData.length,
      selectedCount: selected.length,
      position: payload.position || null,
    });

    try {
      const response = await fetch("/api/update_cart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (result.status === "ok") {
        notify("✅ Корзина сохранена!");
        closeWebApp();
      } else {
        notify(`❌ Ошибка при сохранении: ${result.error || "неизвестная"}`);
      }
    } catch (err) {
      console.error(err);
      notify("❌ Ошибка сети");
    }
    return;
  }

  // Fallback 1: пробуем отправить через tg.sendData (мобилки с reply-клавиатурой)
  if (tg?.sendData) {
    const fallbackPayload = {
      task_ids: selected,
      position: position > 0 ? position : undefined,
    };
    console.info("[WebApp] initData empty, fallback sendData", {
      selectedCount: selected.length,
      position: fallbackPayload.position || null,
    });
    tg.sendData(JSON.stringify(fallbackPayload));
    closeWebApp();
    return;
  }

  // Fallback 2: на десктопе без initData — ничего не сохранить
  notify("❌ Невозможно сохранить: отсутствуют данные авторизации");
}

// Запуск загрузки после полной загрузки DOM
document.addEventListener("DOMContentLoaded", loadData);
