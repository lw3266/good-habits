console.log("Content script loaded!");

// Function to get logged-in user
function getLoggedInUser() {
    const userElement = document.getElementById("user-info");
    if (userElement) {
        return userElement.textContent.trim();
    }
    return null;
}

// Function to check login state
function checkUserLogin() {
    const username = getLoggedInUser();
    if (username) {
        console.log(username ? `✅ Detected logged-in user: ${username}` : "❌ No user detected.");
    }
}

// Run when the page loads
window.addEventListener("load", () => {
    console.log("🔄 Page fully loaded. Checking user login...");
    checkUserLogin();
});

// Run every 5 seconds to detect login state changes
setInterval(checkUserLogin, 5000);
