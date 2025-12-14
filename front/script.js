// ATTENTION : en Docker, le front doit appeler le service "api"
const API_BASE = "http://api:8000";

function loadStatus() {
  fetch(`${API_BASE}/status`)
    .then(r => r.json())
    .then(data => {
      document.getElementById("status").innerText = `API status : ${data.status}`;
    })
    .catch(err => console.error(err));
}

function loadItems() {
  fetch(`${API_BASE}/items`)
    .then(r => r.json())
    .then(items => {
      const ul = document.getElementById("items");
      ul.innerHTML = "";
      items.forEach(item => {
        const li = document.createElement("li");
        li.innerText = `${item.id} - ${item.name}`;
        ul.appendChild(li);
      });
    })
    .catch(err => console.error(err));
}

window.addEventListener("load", () => {
  loadStatus();
  loadItems();
});
