/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#0B0E14", // Very dark background
                surface: "#151923",    // Sidebar/Header background
                card: "#1C212E",       // Card background
                primary: "#FFE600",    // EY Yellow
                secondary: "#00B4D8",  // Blue accent
                success: "#10B981",    // Green accent
                text: "#FFFFFF",
                "text-muted": "#9CA3AF",
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
