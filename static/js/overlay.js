// Modern Overlay Implementation
document.addEventListener("DOMContentLoaded", function () {
    closeOverlay();
});

function openOverlay() {
    const overlay = document.getElementById("overlay");
    if (overlay) {
        overlay.classList.add("active");
        document.body.style.overflow = "hidden";
    }
}

function closeOverlay() {
    const overlay = document.getElementById("overlay");
    if (overlay) {
        overlay.classList.remove("active");
        document.body.style.overflow = "";
    }
}

// Close overlay when clicking backdrop
document.addEventListener("click", function(event) {
    const overlay = document.getElementById("overlay");
    if (event.target === overlay) {
        closeOverlay();
    }
});

// Close overlay on Escape key
document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        closeOverlay();
    }
});

function showMatchDetails(match) {
    if (!match) return;

    const homeTeam = match.home_team;
    const awayTeam = match.away_team;
    
    // Update header
    const headerTitle = document.getElementById("overlay-header-title");
    if (headerTitle) {
        const homeCode = homeTeam.code || homeTeam.name.substring(0, 3).toUpperCase();
        const awayCode = awayTeam.code || awayTeam.name.substring(0, 3).toUpperCase();
        headerTitle.textContent = `${homeCode} vs ${awayCode}`;
    }

    // Update team 1 (home)
    updateTeamSection("team1", homeTeam, match.home_win_percentage || homeTeam.win_percentage);
    
    // Update team 2 (away)
    updateTeamSection("team2", awayTeam, match.away_win_percentage || awayTeam.win_percentage);

    // Update probability scale
    updateProbabilityScale(
        match.home_win_percentage || homeTeam.win_percentage,
        match.away_win_percentage || awayTeam.win_percentage,
        match.draw_percentage
    );

    // Update match details
    updateMatchDetails(match);

    // Open overlay
    openOverlay();
}

function updateTeamSection(prefix, team, winPercentage) {
    const nameEl = document.getElementById(`${prefix}-name`);
    const logoEl = document.getElementById(`${prefix}-logo`);
    const winPctEl = document.getElementById(`${prefix}-win-pct`);
    const fallbackEl = document.getElementById(`${prefix}-fallback`);
    const statsTitleEl = document.getElementById(`${prefix}-stats-title`);

    if (nameEl) nameEl.textContent = team.name;
    if (statsTitleEl) statsTitleEl.textContent = `${team.name} Stats`;
    
    if (logoEl) {
        logoEl.src = team.logo;
        logoEl.alt = team.name;
        logoEl.style.display = "block";
        if (fallbackEl) fallbackEl.style.display = "none";
        logoEl.onerror = function() {
            this.style.display = "none";
            if (fallbackEl) {
                fallbackEl.style.display = "flex";
                const code = team.code || team.name.substring(0, 3).toUpperCase();
                fallbackEl.textContent = code[0];
            }
        };
    }
    if (winPctEl) winPctEl.textContent = `${winPercentage.toFixed(1)}%`;
}

function updateProbabilityScale(homeWin, awayWin, draw) {
    const scale = document.getElementById("probability-scale");
    
    if (!scale) return;

    // Calculate position (0 = home wins, 100 = away wins, 50 = draw)
    // Weighted average: home at 0, draw at 50, away at 100
    const total = homeWin + draw + awayWin;
    if (total === 0) return;

    const position = (awayWin * 100 + draw * 50) / total;
    
    // Update bar width and position to show probability
    const bar = document.getElementById("probability-bar");
    if (bar) {
        const barWidth = Math.max(homeWin, awayWin, draw);
        bar.style.width = `${barWidth}%`;
        // Position the bar to show which team is favored
        bar.style.left = `${Math.min(position, 100 - barWidth)}%`;
    }
}

function updateMatchDetails(match) {
    // League info
    const leagueEl = document.getElementById("detail-league");
    if (leagueEl) {
        const league = match.league_name || "League";
        const season = match.season || "Current";
        leagueEl.textContent = `${league} (${season})`;
    }

    // Round
    const roundEl = document.getElementById("detail-round");
    if (roundEl) {
        roundEl.textContent = match.round || "Regular Season";
    }

    // Venue
    const venueEl = document.getElementById("detail-venue");
    if (venueEl) {
        const venue = match.venue_name || "Unknown Venue";
        const city = match.venue_city ? `, ${match.venue_city}` : "";
        venueEl.textContent = `${venue}${city}`;
    }

    // Referee
    const refereeEl = document.getElementById("detail-referee");
    if (refereeEl) {
        refereeEl.textContent = match.referee || "TBD";
    }

    // Date
    const dateEl = document.getElementById("detail-date");
    if (dateEl) {
        dateEl.textContent = match.date || "TBD";
    }

    // Status
    const statusEl = document.getElementById("detail-status");
    if (statusEl) {
        statusEl.textContent = match.status_long || "Scheduled";
    }

    // Draw percentage
    const drawEl = document.getElementById("detail-draw");
    if (drawEl) {
        drawEl.textContent = `${(match.draw_percentage || 0).toFixed(1)}%`;
    }
}

// Legacy function for backward compatibility
function OnWithData(matchNum) {
    // This function is kept for compatibility but should use match data directly
    // Instead, use showMatchDetails(match) with the match object
    console.warn("OnWithData is deprecated. Use showMatchDetails(match) instead.");
}
