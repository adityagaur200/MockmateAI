import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import UploadResumeSection from "@/components/UploadResumeSection";
import Footer from "@/components/Footer";

const Index = () => {
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
