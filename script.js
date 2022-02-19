const getCurrentSystem = () => {
	const userAgent = navigator.userAgent
	if (userAgent.includes("Linux")) {
		return "Linux"
	}
	if (userAgent.includes("Macintosh")) {
		return "macOS"
	}
	if (userAgent.includes("Windows")) {
		if (userAgent.includes("x64")) {
			return "Windows (64-bit)"
		}
		return "Windows (32-bit)"
	}
	return null
}

const currentSystem = document.getElementById("current-system")
currentSystem.textContent = getCurrentSystem()