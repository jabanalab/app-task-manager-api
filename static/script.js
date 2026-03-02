const API_BASE_URL = ""; // Relative path to the Flask app

function showAuthView() {
    document.getElementById("auth-view").style.display = "block";
    document.getElementById("app-view").style.display = "none";
}

function showAppView(username) {
    document.getElementById("auth-view").style.display = "none";
    document.getElementById("app-view").style.display = "block";
    document.getElementById("welcome-message").innerText = `Welcome, ${username}!`;
    fetchTasks();
}

async function register() {
    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;
    const messageElement = document.getElementById("register-message");

    try {
        const response = await fetch(`${API_BASE_URL}/api/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        if (response.ok) {
            messageElement.style.color = "green";
            messageElement.innerText = data.message;
        } else {
            messageElement.style.color = "red";
            messageElement.innerText = data.message;
        }
    } catch (error) {
        messageElement.style.color = "red";
        messageElement.innerText = "Error during registration.";
    }
}

async function login() {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;
    const messageElement = document.getElementById("login-message");

    try {
        const response = await fetch(`${API_BASE_URL}/api/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        if (response.ok) {
            sessionStorage.setItem("username", data.username);
            showAppView(data.username);
        } else {
            messageElement.style.color = "red";
            messageElement.innerText = data.message;
        }
    } catch (error) {
        messageElement.style.color = "red";
        messageElement.innerText = "Error during login.";
    }
}

async function logout() {
    try {
        await fetch(`${API_BASE_URL}/api/logout`, { method: "POST" });
        showAuthView();
    } catch (error) {
        console.error("Error during logout:", error);
    }
}

async function fetchTasks() {
    const taskList = document.getElementById("task-list");
    taskList.innerHTML = "";
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks`);
        if (response.status === 401) {
            showAuthView();
            return;
        }
        const tasks = await response.json();
        tasks.forEach((task) => {
            const li = document.createElement("li");
            li.className = "task-item";
            // Intentional vulnerability: XSS in task description
            li.innerHTML = `
                <span class="${task.completed ? "completed" : ""}">${task.description}</span>
                <div>
                    ${!task.completed ? `<button onclick="completeTask(${task.id})">Complete</button>` : ""}
                    <button onclick="deleteTask(${task.id})">Delete</button>
                </div>
            `;
            taskList.appendChild(li);
        });
    } catch (error) {
        console.error("Error fetching tasks:", error);
    }
}

async function addTask() {
    const description = document.getElementById("new-task-description").value;
    if (!description) return;

    try {
        await fetch(`${API_BASE_URL}/api/tasks`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ description }),
        });
        document.getElementById("new-task-description").value = "";
        fetchTasks();
    } catch (error) {
        console.error("Error adding task:", error);
    }
}

async function completeTask(taskId) {
    try {
        await fetch(`${API_BASE_URL}/api/tasks/${taskId}/complete`, { method: "PUT" });
        fetchTasks();
    } catch (error) {
        console.error("Error completing task:", error);
    }
}

async function deleteTask(taskId) {
    try {
        await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, { method: "DELETE" });
        fetchTasks();
    } catch (error) {
        console.error("Error deleting task:", error);
    }
}

// Initial check
window.onload = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks`);
        if (response.ok) {
            const tasks = await response.json();
            // Assuming if tasks are returned, user is logged in. This is a simplification.
            // A more robust check would be an /api/user endpoint.
            const username = sessionStorage.getItem("username");
            if (username) {
                showAppView(username);
            } else {
                showAuthView();
            }
        } else {
            showAuthView();
        }
    } catch (error) {
        showAuthView();
    }
};
