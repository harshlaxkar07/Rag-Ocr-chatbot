/* Document Chat — chat front end for the RAG + OCR chatbot API. */
(function () {
  "use strict";

  const { $, $$, el, esc, icon, http, toast, relative } = UI;

  http.base = "";

  const STORE_KEY = "docchat-threads";
  let threads = [];
  let activeId = null;
  let pending = false;

  const SUGGESTIONS = [
    { t: "Summarise the documents", d: "Give me the key points across everything that has been ingested.", ic: "fileText" },
    { t: "Find a specific detail", d: "What does the document say about the architecture?", ic: "search" },
    { t: "Compare two sections", d: "How does the workflow section differ from the overview?", ic: "layers" },
    { t: "Explain a concept", d: "Explain retrieval-augmented generation in simple terms.", ic: "brain" },
  ];

  /* ---------------- persistence ---------------- */
  function load() {
    try {
      threads = JSON.parse(UI.store.get(STORE_KEY) || "[]");
    } catch (_) {
      threads = [];
    }
    if (!Array.isArray(threads)) threads = [];
  }

  function save() {
    try {
      UI.store.set(STORE_KEY, JSON.stringify(threads.slice(0, 40)));
    } catch (_) {
      /* storage unavailable — threads stay in memory for this session */
    }
  }

  const current = () => threads.find((t) => t.id === activeId) || null;

  function newThread() {
    const thread = {
      id: Date.now() + "-" + Math.random().toString(36).slice(2, 7),
      title: "New conversation",
      at: new Date().toISOString(),
      messages: [],
    };
    threads.unshift(thread);
    activeId = thread.id;
    save();
    renderThreads();
    renderMessages();
    $("#prompt").focus();
  }

  /* ---------------- connection ---------------- */
  async function ping() {
    const node = $("#conn");
    const text = $(".conn-text", node);
    try {
      await http.get("/openapi.json");
      node.className = "conn online";
      text.textContent = "API connected";
    } catch (_) {
      node.className = "conn offline";
      text.textContent = "API unreachable";
    }
  }

  /* ---------------- markdown-lite ---------------- */
  function render(text) {
    const blocks = String(text || "").split(/```/);
    let out = "";

    blocks.forEach((block, i) => {
      if (i % 2 === 1) {
        const lines = block.split("\n");
        if (lines[0] && !lines[0].includes(" ")) lines.shift();
        out += `<pre><code>${esc(lines.join("\n").trim())}</code></pre>`;
        return;
      }

      const html = esc(block)
        .replace(/`([^`\n]+)`/g, "<code>$1</code>")
        .replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>")
        .replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>");

      html.split(/\n{2,}/).forEach((para) => {
        const trimmed = para.trim();
        if (!trimmed) return;

        const lines = trimmed.split("\n");
        const bulleted = lines.every((l) => /^\s*[-*•]\s+/.test(l));
        const numbered = lines.every((l) => /^\s*\d+[.)]\s+/.test(l));

        if (bulleted) {
          out += `<ul>${lines.map((l) => `<li>${l.replace(/^\s*[-*•]\s+/, "")}</li>`).join("")}</ul>`;
        } else if (numbered) {
          out += `<ol>${lines.map((l) => `<li>${l.replace(/^\s*\d+[.)]\s+/, "")}</li>`).join("")}</ol>`;
        } else {
          out += `<p>${lines.join("<br>")}</p>`;
        }
      });
    });

    return out || "<p></p>";
  }

  /* ---------------- rendering ---------------- */
  function renderThreads() {
    const host = $("#threadList");
    if (!threads.length) {
      host.innerHTML = `<p class="xs dim" style="padding:6px 11px">No conversations yet.</p>`;
      return;
    }

    host.innerHTML = threads
      .map(
        (t) => `
      <button class="thread ${t.id === activeId ? "active" : ""}" data-thread="${esc(t.id)}">
        ${icon("chat", 15)}
        <span class="tt">${esc(t.title)}</span>
        <span class="td" data-drop="${esc(t.id)}" role="button" aria-label="Delete conversation">${icon("x", 13)}</span>
      </button>`
      )
      .join("");

    $$("#threadList .thread").forEach((b) =>
      b.addEventListener("click", (e) => {
        if (e.target.closest("[data-drop]")) return;
        activeId = b.dataset.thread;
        renderThreads();
        renderMessages();
      })
    );

    $$("#threadList [data-drop]").forEach((b) =>
      b.addEventListener("click", (e) => {
        e.stopPropagation();
        const id = b.dataset.drop;
        threads = threads.filter((t) => t.id !== id);
        if (activeId === id) activeId = threads.length ? threads[0].id : null;
        save();
        renderThreads();
        renderMessages();
      })
    );
  }

  function renderMessages() {
    const thread = current();
    const host = $("#messages");
    $("#threadTitle").textContent = thread ? thread.title : "New conversation";

    if (!thread || !thread.messages.length) {
      host.innerHTML = `
        <div class="welcome">
          <div class="welcome-mark">${icon("chat", 30)}</div>
          <h2>Ask your documents anything</h2>
          <p>Questions are answered from the content that has been ingested and indexed — including pages that were read with OCR.</p>
          <div class="suggestions">
            ${SUGGESTIONS.map(
              (s, i) => `
              <button class="suggestion" data-sug="${i}">
                <div class="st">${icon(s.ic, 15)} ${esc(s.t)}</div>
                <div class="sd">${esc(s.d)}</div>
              </button>`
            ).join("")}
          </div>
        </div>`;

      $$("#messages .suggestion").forEach((b) =>
        b.addEventListener("click", () => {
          $("#prompt").value = SUGGESTIONS[Number(b.dataset.sug)].d;
          autosize();
          send();
        })
      );
      return;
    }

    host.innerHTML = `<div class="thread-inner">${thread.messages
      .map((m, i) => messageHtml(m, i))
      .join("")}</div>`;

    $$("#messages [data-copy-msg]").forEach((b) =>
      b.addEventListener("click", () => {
        const msg = thread.messages[Number(b.dataset.copyMsg)];
        if (msg) UI.copy(msg.text);
      })
    );
    $$("#messages [data-retry]").forEach((b) =>
      b.addEventListener("click", () => {
        const msg = thread.messages[Number(b.dataset.retry)];
        if (msg) {
          $("#prompt").value = msg.text;
          autosize();
          send();
        }
      })
    );

    scrollDown();
  }

  function messageHtml(m, i) {
    if (m.role === "user") {
      return `
      <div class="msg user">
        <div class="msg-avatar">${icon("user", 17)}</div>
        <div class="msg-body">
          <div class="msg-role">You</div>
          <div class="msg-text">${render(m.text)}</div>
          <div class="msg-actions">
            <button class="btn btn-sm btn-ghost" data-retry="${i}" title="Ask again">${icon("refresh", 13)}</button>
            <button class="btn btn-sm btn-ghost" data-copy-msg="${i}" title="Copy">${icon("copy", 13)}</button>
          </div>
        </div>
      </div>`;
    }

    return `
    <div class="msg bot">
      <div class="msg-avatar">${icon("bot", 17)}</div>
      <div class="msg-body">
        <div class="msg-role">Assistant${m.at ? ` · ${esc(relative(m.at))}` : ""}</div>
        <div class="msg-text">${m.error ? `<p class="muted">${esc(m.text)}</p>` : render(m.text)}</div>
        <div class="msg-actions">
          <button class="btn btn-sm btn-ghost" data-copy-msg="${i}" title="Copy">${icon("copy", 13)}</button>
        </div>
      </div>
    </div>`;
  }

  function showTyping() {
    const inner = $(".thread-inner", $("#messages"));
    if (!inner) return;
    const node = el("div", { class: "msg bot", id: "typing" });
    node.innerHTML = `
      <div class="msg-avatar">${icon("bot", 17)}</div>
      <div class="msg-body">
        <div class="msg-role">Assistant</div>
        <div class="typing"><span></span><span></span><span></span></div>
      </div>`;
    inner.append(node);
    scrollDown();
  }

  const hideTyping = () => {
    const node = $("#typing");
    if (node) node.remove();
  };

  function scrollDown() {
    const host = $("#messages");
    host.scrollTop = host.scrollHeight;
  }

  /* ---------------- sending ---------------- */
  async function send() {
    if (pending) return;

    const input = $("#prompt");
    const question = input.value.trim();
    if (!question) return;

    if (!current()) newThread();
    const thread = current();

    thread.messages.push({ role: "user", text: question, at: new Date().toISOString() });
    if (thread.messages.length === 1) {
      thread.title = question.length > 42 ? question.slice(0, 42) + "…" : question;
    }
    input.value = "";
    autosize();
    save();
    renderThreads();
    renderMessages();

    pending = true;
    $("#sendBtn").classList.add("loading");
    showTyping();

    try {
      const data = await http.post("/chat/", { question });
      thread.messages.push({
        role: "bot",
        text: data.answer || "",
        at: new Date().toISOString(),
      });
    } catch (err) {
      thread.messages.push({
        role: "bot",
        text: err.message,
        error: true,
        at: new Date().toISOString(),
      });
      toast(err.message, "error");
    } finally {
      pending = false;
      $("#sendBtn").classList.remove("loading");
      hideTyping();
      save();
      renderMessages();
      input.focus();
    }
  }

  function autosize() {
    const input = $("#prompt");
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 190) + "px";
  }

  /* ---------------- export ---------------- */
  function exportChat() {
    const thread = current();
    if (!thread || !thread.messages.length) {
      toast("This conversation is empty", "info");
      return;
    }

    const body = thread.messages
      .map((m) => `## ${m.role === "user" ? "You" : "Assistant"}\n\n${m.text}\n`)
      .join("\n");
    const text = `# ${thread.title}\n\n_${UI.date(thread.at, true)}_\n\n${body}`;

    const url = URL.createObjectURL(new Blob([text], { type: "text/markdown" }));
    const a = el("a", { href: url, download: `${thread.title.replace(/[^\w\s-]/g, "").trim() || "conversation"}.md` });
    document.body.append(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    toast("Conversation downloaded", "success");
  }

  /* ---------------- boot ---------------- */
  function init() {
    UI.initTheme();
    UI.hydrateIcons();
    $$("[data-theme-toggle]").forEach((b) => b.addEventListener("click", UI.toggleTheme));

    const sidebar = $(".sidebar");
    const menuBtn = $(".menu-btn");
    let scrim = null;
    const closeSidebar = () => {
      sidebar.classList.remove("open");
      if (scrim) { scrim.remove(); scrim = null; }
    };
    menuBtn.addEventListener("click", () => {
      if (sidebar.classList.contains("open")) return closeSidebar();
      sidebar.classList.add("open");
      scrim = el("div", { class: "scrim", onclick: closeSidebar });
      document.body.append(scrim);
    });

    load();
    if (threads.length) activeId = threads[0].id;
    renderThreads();
    renderMessages();

    $("#newChat").addEventListener("click", newThread);
    $("#exportChat").addEventListener("click", exportChat);

    const input = $("#prompt");
    input.addEventListener("input", autosize);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send();
      }
    });

    $("#composer").addEventListener("submit", (e) => {
      e.preventDefault();
      send();
    });

    ping();
    input.focus();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
