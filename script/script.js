
const formSections = document.querySelectorAll('.form-section');
let currentSection = 0;

function showSection(index) {
    formSections.forEach((section, idx) => {
        section.style.display = idx === index ? 'block' : 'none';
    });
}

showSection(currentSection);

document.getElementById('nextToContact').addEventListener('click', () => {
    if (currentSection < formSections.length - 1) {
        currentSection++;
        showSection(currentSection);
    }
});

document.getElementById('prevToPersonal').addEventListener('click', () => {
    if (currentSection > 0) {
        currentSection--;
        showSection(currentSection);
    }
});

document.getElementById('nextToBusiness').addEventListener('click', () => {
    if (currentSection < formSections.length - 1) {
        currentSection++;
        showSection(currentSection);
    }
});

document.getElementById('prevToContact').addEventListener('click', () => {
    if (currentSection > 0) {
        currentSection--;
        showSection(currentSection);
    }
});



document.getElementById("multiStepForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    let formData = {
        first_name: document.getElementById("first_name").value,
        surname: document.getElementById("surname").value,
        register_username: document.getElementById("register_username").value,
        email: document.getElementById("email").value,
        phone_number: document.getElementById("phone_number").value,
        register_password: document.getElementById("register_password").value,
        description: document.getElementById("description").value
    };

    try {
        let response = await fetch("http://127.0.0.1:5000/api/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: formData
        });

        let data = await response.json();
        let messageBox = document.getElementById('message_box');
        document.getElementById("messageBox").innerText = data.message || data.error;
        document.getElementById("messageBox").style.color = data.message ? "green" : "red";

        if(data.messageBox) {
            document.getElementById('multiStepForm').reset();
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
    }
});

document.getElementById("login_btn").addEventListener("click", async function (event) {
    event.preventDefault(); 

    const username = document.getElementById("login_username").value;
    const password = document.getElementById("login_password").value;

    if (!username || !password) {
        alert("Please enter both username and password.");
        return;
    }

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                login_username: username,
                login_password: password,
            }),
        });

        const data = await response.json();

        if (response.ok) {
            alert("Login successful!");
            window.location.href = "/dashboard"; 
        } else {
            alert(data.error || "Invalid username or password.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred while logging in.");
    }
});
