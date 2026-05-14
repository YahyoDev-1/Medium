// ==========================================
// 1. CSRF TOKEN HELPER (Django xavfsizligi)
// ==========================================
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

// ==========================================
// 2. TUGMALAR UCHUN BOSISH (CLICK) HODISALARI
// ==========================================
document.addEventListener("click", function (e) {

  // A. LAYK TUGMASI (Like Toggle)
  const likeBtn = e.target.closest("#like-btn");
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

  // B. SAQLASH TUGMASI (Bookmark Toggle)
  const bBtn = e.target.closest("[data-bookmark-btn]");
  if (bBtn) {
    const id = bBtn.dataset.articleId || bBtn.getAttribute("data-article-id");
    if (!id) return;
    fetch(`/interactions/bookmark-toggle/${id}/`, {
      method: "POST",
      headers: {"X-CSRFToken": csrftoken, "Accept": "application/json"},
      credentials: "same-origin",
    })
    .then(res => res.json())
    .then(data => {
      if (data.saved) bBtn.classList.add("saved"); else bBtn.classList.remove("saved");
    })
    .catch(err => console.error("Bookmark toggle failed:", err));
  }

  // C. XATCHO'PDAN O'CHIRISH TUGMASI (Remove Bookmark)
  const removeBookmarkBtn = e.target.closest("[data-remove-bookmark]");
  if (removeBookmarkBtn) {
    const id = removeBookmarkBtn.dataset.articleId || removeBookmarkBtn.getAttribute("data-article-id");
    if (!id) return;
    fetch(`/interactions/bookmark-toggle/${id}/`, {
      method: "POST",
      headers: {"X-CSRFToken": csrftoken, "Accept": "application/json"},
      credentials: "same-origin",
    }).then(res => res.json()).then(data => {
        if (!data.saved) {
          const card = removeBookmarkBtn.closest(".card");
          if (card) card.remove();
        }
    }).catch(err => console.error("Remove bookmark failed", err));
  }

  // D. RO'YXATGA QO'SHISH (Add to List)
  const addToListBtn = e.target.closest("[data-add-to-list]");
  if (addToListBtn) {
    const articleId = addToListBtn.dataset.articleId || addToListBtn.getAttribute("data-article-id");
    if (!articleId) return;
    const listName = prompt("Enter a list name to save this story (existing lists will be reused):", "");
    if (listName === null) return;
    const form = new FormData();
    form.append("article_id", articleId);
    form.append("list_name", listName);

    fetch("/interactions/add-to-list/", {
      method: "POST",
      body: form,
      headers: {"X-CSRFToken": csrftoken},
      credentials: "same-origin",
    }).then(res => res.json())
      .then(data => {
        if (data && data.success) {
          alert(`Saved to list "${data.list_name}".`);
        } else {
          alert(data.error || "Could not save to list.");
        }
      })
      .catch(err => {
        console.error("Add to list failed", err);
        alert("Could not save to a list.");
      });
  }

  // E. RO'YXATDAN O'CHIRISH (Remove from List)
  const removeFromListBtn = e.target.closest("[data-remove-from-list]");
  if (removeFromListBtn) {
    const articleId = removeFromListBtn.dataset.articleId || removeFromListBtn.getAttribute("data-article-id");
    const listId = removeFromListBtn.dataset.listId || removeFromListBtn.getAttribute("data-list-id");
    if (!articleId || !listId) return;
    const form = new FormData();
    form.append("article_id", articleId);
    form.append("list_id", listId);

    fetch("/interactions/remove-from-list/", {
      method: "POST",
      body: form,
      headers: {"X-CSRFToken": csrftoken},
      credentials: "same-origin",
    }).then(res => res.json())
      .then(data => {
        if (data && data.success) {
          const card = removeFromListBtn.closest(".card");
          if (card) card.remove();
        } else {
          alert(data.error || "Could not remove from list.");
        }
      })
      .catch(err => {
        console.error("Remove from list failed", err);
        alert("Could not remove from list.");
      });
  }

  // F. FOLLOW TUGMASI (Follow Toggle)
  const followBtn = e.target.closest("#follow-btn");
  if (followBtn) {
    const authorId = followBtn.dataset.authorId;
    if (!authorId) return;

    fetch(`/notifications/follow/${authorId}/`, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
      },
      credentials: "same-origin",
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          alert(data.error);
          return;
        }

        if (data.is_following) {
          followBtn.textContent = "Following";
          followBtn.classList.add("following");
        } else {
          followBtn.textContent = "Follow";
          followBtn.classList.remove("following");
        }

        console.log(data.message);
        if (typeof loadNotificationsBadge === "function") {
          loadNotificationsBadge();
        }
      })
      .catch((err) => {
        console.error("Follow failed:", err);
        alert("Failed to update follow status. Please try again.");
      });
  }
});

// ==========================================
// 3. EDITOR VA MEDIA YUKLASH SAHIFASI YUKLANGANDA
// ==========================================
document.addEventListener("DOMContentLoaded", function () {
  const editor = document.getElementById("editor");
  const hiddenBody = document.querySelector("input[name='body_html']");
  const articleForm = document.getElementById("article-form");
  const mediaInput = document.getElementById("media-upload-input");
  const coverInput = document.getElementById("id_cover_image");
  const coverPreview = document.getElementById("cover-preview");

  if (articleForm && editor && hiddenBody) {
    articleForm.addEventListener("submit", function () {
      hiddenBody.value = editor.innerHTML.trim();
    });
  }

  if (mediaInput && editor) {
    mediaInput.addEventListener("change", function (ev) {
      const file = ev.target.files[0];
      if (!file) return;
      const form = new FormData();
      form.append("file", file);
      const loader = document.createElement("div");
      loader.textContent = "Uploading...";
      editor.appendChild(loader);

      fetch("/articles/upload-media/", {
        method: "POST",
        body: form,
        headers: {"X-CSRFToken": csrftoken},
        credentials: "same-origin",
      }).then(res => res.json()).then(data => {
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
