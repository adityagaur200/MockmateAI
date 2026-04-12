import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import UploadResumeSection from "@/components/UploadResumeSection";
import Footer from "@/components/Footer";

const Index = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      const timer = window.setTimeout(() => {
        navigate("/auth");
      }, 5000);

      return () => window.clearTimeout(timer);
    }
  }, [navigate]);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <HeroSection />
      <div id="upload">
        <UploadResumeSection />
      </div>
      <Footer />
    </div>
  );
};

export default Index;
