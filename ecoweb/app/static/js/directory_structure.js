function createFileStructure(parent, structure) {
    for (const key in structure) {
        if (key === "__files__") {
            // Add files to the parent element
            structure[key].forEach(file => {
                const fileElement = document.createElement("li");
                // Determine the icon based on the file extension
                let icon = "📄"; // Default icon
                if (file.endsWith(".css")) {
                        icon = "🎨";
                    } else if (file.endsWith(".do")) {
                        icon = "📄";
                    } else if (file.endsWith(".js")) {
                        icon = "📜";
                    } else if (file.endsWith(".html")) {
                        icon = "🌐";
                    }

                    // Add the file with the appropriate icon
                    fileElement.innerHTML = `<span class="file">${icon} ${file}</span>`;
                    parent.appendChild(fileElement);

                });
            } else {
                // Add folder to the parent element
                const folderElement = document.createElement("li");
                folderElement.innerHTML = `
                    <span class="folder">📁 ${key}</span>
                    <button class="toggle">
                        <img src="/static/toggle_down.png" alt="Toggle">
                    </button>
                `;

                const childList = document.createElement("ul");
                childList.classList.add("hidden"); // Initially hide subfolders
                folderElement.appendChild(childList);
                parent.appendChild(folderElement);

                // Add event listener to toggle visibility
                const toggleButton = folderElement.querySelector(".toggle");
                toggleButton.addEventListener("click", () => {
                    childList.classList.toggle("hidden");
                    const img = toggleButton.querySelector("img");
                    img.src = childList.classList.contains("hidden")
                        ? "/static/toggle_down.png"
                        : "/static/toggle_up.png";
                });

                // Recursive call for child directories
                createFileStructure(childList, structure[key]);
            }
        }
    }

    function initializeFileStructure() {
        const rootElement = document.getElementById("file-structure");
        try {
            createFileStructure(rootElement, directoryStructure);
        } catch (error) {
            console.error("Error creating file structure:", error);
        }
    }
   
    // Initialize the file structure
    // initializeFileStructure();
    document.addEventListener('DOMContentLoaded', initializeFileStructure);