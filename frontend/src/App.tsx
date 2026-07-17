import { ThemeProvider } from "./providers/theme-provider";
import { AppRoutes } from "./routes/AppRoutes";
import { Toaster } from "./components/ui/sonner";


function App() {
  return (
    <ThemeProvider
      defaultTheme="light"
      storageKey="vite-ui-theme"
    >
        <AppRoutes />
        <Toaster position="top-right" richColors />
    </ThemeProvider>
  );
}

export default App;