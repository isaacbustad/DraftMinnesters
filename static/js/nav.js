function toggleNav(event, elementId) { 
  console.log("Toggling navigation to element ID:", elementId);
  // Hide all elements with class="nav-content"
  const element = document.getElementsByClassName("nav-content");
  for (let i = 0; i < element.length; i++) {
    element[i].style.display = "none";
  }
  
  // Remove the class "active" from all elements with class="nav-links"
  const tabs = document.getElementsByClassName("nav-links");
  for (let i = 0; i < tabs.length; i++) {
    tabs[i].className = tabs[i].className.replace(" active", "");
  }

  const activeElement = document.getElementById(elementId);
  if (activeElement) {
    activeElement.style.display = "block";
  }
  // Add the "active" class to the button that opened the tab
  event.currentTarget.className += " active";
}