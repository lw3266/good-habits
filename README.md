# G00D-Habits
HACKNYU 2025

**Inspiration**
We considered apps like Duolingo, which we realized we used frequently due to its fun gamified and interactive experience. We wanted to apply similar principles to habit tracking, making it more than just a to-do list.
What it does

**Description:** 
Good Habits is a web app that helps users build and maintain positive habits. The web app provides a dashboard where users can track their progress and receive AI-generated motivational and helpful messages.

**How we built it:**
We developed the web app using Streamlit for a simple and effective UI, and using a sqlite database to store user progress and information. We also connected the system to a generative AI model to generate personalized responses and motivational messages based on user habits and progress.

**Challenges we ran into:**
One of the biggest challenges was merging GitHub branches, correctly merging different database formats. Another challenge was appropriately implementing OpenAI integration into the web app and having it have access to the context of the users' progress as stored in the database.

**Accomplishments that we're proud of:**
We successfully built a functional prototype that combines AI-driven habit tracking with gamification. The AI model responses provide meaningful motivation. We also had to design the AI-generated messages to be both engaging and genuinely helpful rather than generic. We're proud of how we managed to create a smooth user experience within 24hrs.

**What we learn:**
We gained hands-on experience integrating AI models into real-world applications. We also learned about data cleanliness by having to manage unwieldy structural differences between development branches. Working across different platforms taught us valuable lessons in coordination in API's.
What's next for Good Habits

**What's next for G00D-Habits**
With more time, we would have implement a browser extension using JavaScript to monitor user activity. The browser extension would supplement the sense of accountability by sending notifications and tracking browsing habits. We also would want to possibly have browser extension's capabilities integrated with other productivity tools. Furthermore, we may have include more gamification features, such as progress graphing and competition with other users, as well as deploying the app to other platforms.

**Built With**
-javascript
-python
-sqlite
-streamlit
