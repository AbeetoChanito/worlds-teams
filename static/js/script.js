document.addEventListener("DOMContentLoaded", function() {
    function fetchTeams() {
        fetch('/teams')
            .then(response => response.json())
            .then(data => {
                const tableBody = document.querySelector("#teamsTable tbody");
                tableBody.innerHTML = "";

                data.forEach(team => {
                    const row = document.createElement("tr");
                    row.innerHTML = `<td>${team.team_number}</td>
                                     <td>${team.qualifications.join(", ")}</td>`;
                    tableBody.appendChild(row);
                });
            })
            .catch(error => console.error("Error fetching teams:", error));
    }

    fetchTeams();
});
