console.log("🚀 Content script loaded!");

// Function to get logged-in user
function getLoggedInUser() {
  const userElement = document.getElementById("user-info");
  if (userElement) {
    // Trim any whitespace just to be safe.
    return userElement.textContent.trim();
  }
  return null;
}

// Function to check login state when an event occurs
function checkUserLogin() {
  const username = getLoggedInUser();
  console.log(username ? `✅ Detected logged-in user: ${username}` : "❌ No user detected.");
}

// Run when the page loads
window.addEventListener("load", () => {
  console.log("🔄 Page fully loaded. Checking user login...");
  checkUserLogin();
});

// Observe changes in the DOM to detect login state changes dynamically
const observer = new MutationObserver(() => {
  checkUserLogin();
});

// Start observing the body for changes (e.g., login state changes)
observer.observe(document.body, { childList: true, subtree: true });

// Function to send tab data to background.js when an event occurs
function sendTabData() {
  let username = getLoggedInUser();
  if (!username) {
    console.log("No logged-in user; skipping tab data update.");
    return;
  }
  let pageTitle = document.title;
  let pageURL = window.location.href;
  chrome.runtime.sendMessage(
    { action: "updateTab", title: pageTitle, url: pageURL, username: username },
    (response) => {
      console.log("📤 Tab data sent:", response);
    }
  );
}



// Detect title and URL changes (useful for SPAs where the URL may not change)
let lastTitle = document.title;
let lastURL = window.location.href;

// Observe changes in the document title
const titleObserver = new MutationObserver(() => {
  if (document.title !== lastTitle) {
    lastTitle = document.title;
    sendTabData();
  }
});

// Observe changes in the URL (for SPAs using history API)
const urlObserver = new MutationObserver(() => {
  if (window.location.href !== lastURL) {
    lastURL = window.location.href;
    sendTabData();
  }
});

// Start observing title changes
titleObserver.observe(document.querySelector("title"), { childList: true });

// Hook into pushState and replaceState to detect URL changes
const originalPushState = history.pushState;
const originalReplaceState = history.replaceState;

history.pushState = function (...args) {
  originalPushState.apply(this, args);
  sendTabData();
};

history.replaceState = function (...args) {
  originalReplaceState.apply(this, args);
  sendTabData();
};

// Initial data send when script loads
sendTabData();
