document.addEventListener("DOMContentLoaded", function () {
    off();
});

function on() {
  document.getElementById("overlay").style.display = "block";
}

function off() {
  document.getElementById("overlay").style.display = "none";
}

function OnWithData(matchNum) {
  
    fetch('/teamstats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ matchNum})
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('team1name').innerText = data.team1name;
        document.getElementById('team2name').innerText = data.team2name;

        document.getElementById('team1logo').src = data.team1logo;
        document.getElementById('team2logo').src = data.team2logo;
        
        document.getElementById('team1stats').innerText = data.team1stats;
        document.getElementById('team2stats').innerText = data.team2stats;

        document.getElementById('team1winchanse').innerText = data.team2winchanse;
        document.getElementById('team2winchanse').innerText = data.team2winchanse;
    });
  on();
}