// CSRF helper for fetch requests using cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie("csrftoken");

// Like toggle
document.addEventListener("click", function (e) {
    const likeBtn = e.target.closest && e.target.closest("#like-btn");
    if (likeBtn) {
        const articleId = likeBtn.dataset.articleId;
        fetch(`/interactions/like-toggle/${articleId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "Accept": "application/json",
            },
            credentials: "same-origin",
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.liked) {
                    likeBtn.classList.add("liked");
                } else {
                    likeBtn.classList.remove("liked");
                }
                const countEl = likeBtn.querySelector(".count");
                if (countEl) countEl.textContent = data.count;
            })
            .catch((err) => console.error("Like toggle failed:", err));
    }
});

// Editor: sync contenteditable to hidden body_html on submit
document.addEventListener("DOMContentLoaded", function () {
    const editor = document.getElementById("editor");
    const hiddenBody = document.querySelector("input[name='body_html']");
    const articleForm = document.getElementById("article-form");
    if (articleForm && editor && hiddenBody) {
        articleForm.addEventListener("submit", function () {
            // Transfer editor innerHTML
            hiddenBody.value = editor.innerHTML.trim();
        });
    }

    // Tags input: allow comma separated and Enter to add
    const tagsInput = document.getElementById("id_tags_raw");
    if (tagsInput) {
        // replace commas -> normalized
        tagsInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                // allow submission if SHIFT+Enter? no, we interpret as finishing tags
                const val = tagsInput.value.trim();
                tagsInput.value = val;
                // keep default behavior; submission will include tags
            }
        });
        // on blur, normalize commas and whitespace
        tagsInput.addEventListener("blur", function () {
            const val = tagsInput.value.split(",").map(s => s.trim()).filter(Boolean).join(", ");
            tagsInput.value = val;
        });
    }
});

// CSRF helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie("csrftoken");

// Like toggle (delegated)
document.addEventListener("click", function (e) {
    const likeBtn = e.target.closest && e.target.closest("#like-btn");
    if (likeBtn) {
        const articleId = likeBtn.dataset.articleId;
        fetch(`/interactions/like-toggle/${articleId}/`, {
            method: "POST",
            headers: {"X-CSRFToken": csrftoken, "Accept": "application/json"},
            credentials: "same-origin",
        })
            .then(res => res.json())
            .then(data => {
                if (data.liked) likeBtn.classList.add("liked"); else likeBtn.classList.remove("liked");
                const countEl = likeBtn.querySelector(".count");
                if (countEl) countEl.textContent = data.count;
            })
            .catch(err => console.error("Like toggle failed:", err));
    }

    // Bookmark toggle via button with data-bookmark
    const bookmarkBtn = e.target.closest && e.target.closest("[data-bookmark-btn]");
    if (bookmarkBtn) {
        const articleId = bookmarkBtn.datasetArticleId || bookmarkBtn.dataset.articleId || bookmarkBtn.dataset["articleId"];
        // Support button attribute data-article-id etc:
        const id = bookmarkBtn.dataset.articleId || bookmarkBtn.getAttribute("data-article-id");
        if (!id) return;
        fetch(`/interactions/bookmark-toggle/${id}/`, {
            method: "POST",
            headers: {"X-CSRFToken": csrftoken, "Accept": "application/json"},
            credentials: "same-origin",
        })
            .then(res => res.json())
            .then(data => {
                if (data.saved) bookmarkBtn.classList.add("saved"); else bookmarkBtn.classList.remove("saved");
                const countEl = bookmarkBtn.querySelector(".count");
                if (countEl) countEl.textContent = data.count;
            })
            .catch(err => console.error("Bookmark toggle failed:", err));
    }
});

// Editor: sync contenteditable to hidden body_html on submit and handle media upload
document.addEventListener("DOMContentLoaded", function () {
    const editor = document.getElementById("editor");
    const hiddenBody = document.querySelector("input[name='body_html']");
    const articleForm = document.getElementById("article-form");
    const mediaInput = document.getElementById("media-upload-input");

    if (articleForm && editor && hiddenBody) {
        articleForm.addEventListener("submit", function () {
            hiddenBody.value = editor.innerHTML.trim();
        });
    }

    // media upload handling: send file via fetch to upload endpoint and insert media into editor
    if (mediaInput && editor) {
        mediaInput.addEventListener("change", function (ev) {
            const file = ev.target.files[0];
            if (!file) return;
            const form = new FormData();
            form.append("file", file);
            // Show temporary loader
            const loader = document.createElement("div");
            loader.textContent = "Uploading...";
            editor.appendChild(loader);

            fetch("/articles/upload-media/", {
                method: "POST",
                body: form,
                headers: {"X-CSRFToken": csrftoken},
                credentials: "same-origin",
            })
                .then(res => res.json())
                .then(data => {
                    loader.remove();
                    if (data && data.url) {
                        if (data.type === "image") {
                            const img = document.createElement("img");
                            img.src = data.url;
                            img.style.maxWidth = "100%";
                            img.style.display = "block";
                            editor.appendChild(img);
                        } else if (data.type === "video") {
                            const video = document.createElement("video");
                            video.controls = true;
                            const src = document.createElement("source");
                            src.src = data.url;
                            video.appendChild(src);
                            video.style.maxWidth = "100%";
                            editor.appendChild(video);
                        } else {
                            // file: insert link
                            const a = document.createElement("a");
                            a.href = data.url;
                            a.textContent = data.name || "Download file";
                            a.target = "_blank";
                            editor.appendChild(a);
                        }
                    } else {
                        alert("Upload failed.");
                    }
                })
                .catch(err => {
                    loader.remove();
                    console.error("Upload error", err);
                    alert("Upload failed.");
                })
                .finally(() => {
                    // clear the input for future uploads
                    mediaInput.value = "";
                });
        });
    }

    // Tags input normalization
    const tagsInput = document.getElementById("id_tags_raw");
    if (tagsInput) {
        tagsInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                const val = tagsInput.value.trim();
                tagsInput.value = val;
            }
        });
        tagsInput.addEventListener("blur", function () {
            const val = tagsInput.value.split(",").map(s => s.trim()).filter(Boolean).join(", ");
            tagsInput.value = val;
        });
    }
});