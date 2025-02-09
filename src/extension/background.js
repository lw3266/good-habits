// Object to store tab information
let tabsData = {};

// Listen for messages from content.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("Received message:", message); // Debugging: Check if username is included in message
  if (message.action === "updateTab") {
    const tabId = sender.tab && sender.tab.id;
    let username = message.username || null;
    if (tabId) {
      if (tabsData[tabId]) {
        tabsData[tabId].title = message.title;
        tabsData[tabId].url = message.url;
        tabsData[tabId].username = username;
      } else {
        tabsData[tabId] = { title: message.title, url: message.url, openedAt: Date.now(), username: username };
      }
      updateDatabase();
      sendResponse({ status: "success", data: tabsData[tabId] });
    } else {
      sendResponse({ status: "failed", message: "No tab ID found." });
    }
  }
});


// When a new tab is created, record it (if not already recorded)
chrome.tabs.onCreated.addListener((tab) => {
  const tabId = tab.id;
  if (!tabsData[tabId]) {
    // Note: tab.title may not be available immediately; a subsequent update will fix it.
    tabsData[tabId] = { title: tab.title || "New Tab", url: tab.url, openedAt: Date.now() };
  }
  console.log(`Tab Opened: ${tab.title} (ID: ${tabId})`);
  updateDatabase();
});

// When a tab is updated (for example, finishes loading)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete") {
    // If the tab already exists, update its title and URL without changing openedAt.
    if (tabsData[tabId]) {
      tabsData[tabId].title = tab.title;
      tabsData[tabId].url = tab.url;
    } else {
      tabsData[tabId] = { title: tab.title, url: tab.url, openedAt: Date.now() };
    }
    console.log(`Tab Updated: ${tab.title} (ID: ${tabId})`);
    updateDatabase();
  } else {
    // For non-complete updates, update title and URL if we already have an entry.
    if (tabsData[tabId]) {
      tabsData[tabId].title = tab.title;
      tabsData[tabId].url = tab.url;
      updateDatabase();
    }
  }
});

// When a tab is closed, log its duration and remove it from our record.
chrome.tabs.onRemoved.addListener((tabId) => {
  if (tabsData[tabId]) {
    let timeSpent = (Date.now() - tabsData[tabId].openedAt) / 1000; // in seconds
    console.log(
      `Tab Closed: ${tabsData[tabId].title} (ID: ${tabId}). Time spent: ${timeSpent.toFixed(2)}s`
    );
    delete tabsData[tabId];
    updateDatabase();
  }
});

function updateDatabase() {
  console.log("Updating database...");
  const tabDurations = Object.entries(tabsData).map(([id, tab]) => {
    if (!tab.username) {
      console.error("Username missing for tab: ", tab);  // Ensure username is present
    }
    const duration = (Date.now() - tab.openedAt) / 1000;
    return { username: tab.username, title: tab.title, url: tab.url, duration };
  });
  console.log("Tab Durations:", tabDurations);
  sendToDatabase(tabDurations);  // Send data to the server
  updateNotification();  // Update the notification
}



function sendToDatabase(tabData) {
  fetch("http://127.0.0.1:5000/store_tabs", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(tabData)
  })
  .then(response => response.json())
  .then(data => console.log("Server response:", data))
  .catch(error => console.error("Error sending data:", error));
}

// Create or update a Chrome notification with current tab statistics.
function updateNotification() {
  const tabCount = Object.keys(tabsData).length;
  let details = "";
  for (const id in tabsData) {
    const duration = (Date.now() - tabsData[id].openedAt) / 1000;
    details += `${tabsData[id].title}: ${duration.toFixed(2)}s\n`;
  }
  const message = `Open Tabs: ${tabCount}\n${details}`;

  // Create/update a notification with a fixed ID.
  chrome.notifications.create(
    "tabStats",
    {
      type: "basic",
      iconUrl: "icon.png", // Make sure you include this icon in your extension directory.
      title: "Tab Statistics",
      message: message,
      priority: 2,
    },
    (notificationId) => {
      console.log("Notification updated", notificationId);
    }
  );
}
