import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ArrowDown } from "lucide-react";

const HeroSection = () => {
  return (
    <section className="relative pt-32 pb-16 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-subtle opacity-50" />
      <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full bg-primary/5 blur-3xl" />

      <div className="container relative">
        <motion.div
          className="max-w-2xl mx-auto text-center"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border bg-background text-xs font-medium text-muted-foreground mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse-soft" />
            AI-powered interview practice
          </div>

          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight leading-[1.1] mb-5">
            Practice Real
            <br />
            Interviews with{" "}
            <span className="text-gradient">AI</span>
          </h1>

          <p className="text-lg text-muted-foreground max-w-xl mx-auto mb-8 leading-relaxed">
            Upload your resume and job description. Get AI-generated questions,
            practice mock interviews, and receive personalized feedback.
          </p>

          <Button
            size="lg"
            className="bg-gradient-primary hover:shadow-glow transition-all duration-300 text-base px-8 h-12"
            onClick={() =>
              document.getElementById("upload")?.scrollIntoView({ behavior: "smooth" })
            }
          >
            Get Started
            <ArrowDown className="ml-2 h-4 w-4" />
          </Button>
        </motion.div>
      </div>
    </section>
  );
};

export default HeroSection;
