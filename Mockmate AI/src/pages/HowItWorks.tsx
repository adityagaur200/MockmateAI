import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { motion } from "framer-motion";
import { Upload, Cpu, MessageSquare, BarChart3, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

const steps = [
  {
    icon: Upload,
    title: "Upload Resume & Job Description",
    description:
      "Share your resume and the job posting you're targeting. Our AI analyzes both to understand your background and the role requirements.",
    detail: "Supports PDF, DOCX, and plain text formats. You can also paste content directly.",
  },
  {
    icon: Cpu,
    title: "AI Generates Interview Questions",
    description:
      "Our AI creates realistic, role-specific questions based on your profile, the job description, and current industry trends.",
    detail: "Questions span behavioral, technical, and situational categories tailored to your level.",
  },
  {
    icon: MessageSquare,
    title: "Take the Mock Interview",
    description:
      "Answer questions via voice or text in a realistic interview simulation with webcam support and timed responses.",
    detail: "Choose between voice recording or text input. Sessions can be paused and resumed.",
  },
  {
    icon: BarChart3,
    title: "Get Detailed Feedback",
    description:
      "Receive a comprehensive performance score with actionable improvement suggestions for every question you answered.",
    detail: "View correct answers, compare with yours, and track progress over time.",
  },
];

const HowItWorksPage = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <section className="pt-32 pb-24">
        <div className="container">
          <motion.div
            className="text-center mb-20"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
              How It Works
            </h1>
            <p className="text-lg text-muted-foreground max-w-xl mx-auto">
              Four simple steps from uploading your resume to landing your dream job.
            </p>
          </motion.div>

          <div className="max-w-3xl mx-auto space-y-8">
            {steps.map((step, i) => (
              <motion.div
                key={step.title}
                className="group relative flex gap-6 items-start"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                {/* Timeline line */}
                {i < steps.length - 1 && (
                  <div className="absolute left-6 top-14 w-px h-[calc(100%+2rem)] bg-border" />
                )}
                <div className="shrink-0 w-12 h-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center group-hover:bg-gradient-primary group-hover:text-primary-foreground transition-all duration-300 z-10">
                  <step.icon className="h-5 w-5" />
                </div>
                <div className="rounded-2xl border bg-card p-6 shadow-card hover:shadow-card-hover transition-all duration-300 flex-1">
                  <span className="text-xs font-medium text-muted-foreground">Step {i + 1}</span>
                  <h3 className="text-lg font-semibold mt-1 mb-2">{step.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed mb-2">
                    {step.description}
                  </p>
                  <p className="text-xs text-muted-foreground/70 italic">{step.detail}</p>
                </div>
              </motion.div>
            ))}
          </div>

          <motion.div
            className="text-center mt-16"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Link to="/dashboard">
              <Button size="lg" className="bg-gradient-primary hover:shadow-glow transition-all duration-300 text-base px-8 h-12">
                Go to Dashboard
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>
      <Footer />
    </div>
  );
};

export default HowItWorksPage;
