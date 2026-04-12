import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Interview from "@/pages/Interview";
import Index from "./pages/Index.tsx";
import HowItWorksPage from "./pages/HowItWorks.tsx";
import DashboardPage from "./pages/Dashboard.tsx";
import AnalysisDetail from "./pages/AnalysisDetail.tsx";
import NotFound from "./pages/NotFound.tsx";
import Resume from "./components/Resume.tsx";
import AuthPage from "./pages/AuthPage.tsx";


const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/resume" element={<Resume />} />
          <Route path="/interview" element={<Interview />} />
          <Route path="/how-it-works" element={<HowItWorksPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/analysis/:interviewId" element={<AnalysisDetail />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
