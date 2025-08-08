document.addEventListener("DOMContentLoaded", () => {
  const popup = document.querySelector(".pop-section");
  const robo = document.querySelector(".robo");

  const observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          popup.classList.add("show");
          popup.classList.remove("hidden");
          robo.classList.add("show");
          robo.classList.remove("hidden");
        }
      });
    },
    { threshold: 0.3 }
  );

  observer.observe(popup);

  // Scroll to chat section when scroll indicator is clicked
  const scrollBtn = document.getElementById("scroll-down");
  const scrollTarget = document.getElementById("scroll-target");

  if (scrollBtn && scrollTarget) {
    scrollBtn.addEventListener("click", () => {
      scrollTarget.scrollIntoView({ behavior: "smooth" });
    });
  }

  // Scroll to chat section when arrow down key is pressed
  document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
      const target = document.getElementById("scroll-target");
      if (target) {
        target.scrollIntoView({ behavior: "smooth" });
      }
    }
  });

const sendBtn = document.getElementById("sendBtn");
const userInput = document.getElementById("userInput");
const chatDisplay = document.getElementById("chatDisplay");
addMessage("Namaste , So how you are feeling Today. If unfind Type 'random' for Random quotes ", "user");
sendBtn.addEventListener("click", async () => {
  const userMsg = userInput.value.trim();
  
  if (!userMsg) return;

  addMessage(userMsg, "bot");

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: userMsg })
    });

    const data = await response.json();
    const botReply = data.reply || "No response from server.";
    addMessage(botReply, "user");

  } catch (error) {
    console.error(error);
    addMessage("Error: Failed to connect to bot server.", "user");
  }

  userInput.value = "";
});

function addMessage(text, sender) {
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender);
  msgDiv.textContent = text;
  chatDisplay.appendChild(msgDiv);
  chatDisplay.scrollTop = chatDisplay.scrollHeight;
}
});

// Fallback scroll-based animation (in case IntersectionObserver fails)
window.addEventListener("scroll", () => {
  const section = document.querySelector(".pop-section");
  const trigger = window.innerHeight * 0.7;
  if (section) {
    const sectionTop = section.getBoundingClientRect().top;
    if (sectionTop < trigger) {
      section.classList.add("show");
    }
  }
});

