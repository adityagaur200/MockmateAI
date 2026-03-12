import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

const CTASection = () => {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-subtle" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full bg-primary/5 blur-3xl" />

      <motion.div
        className="container relative text-center"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
          Ready to improve your interview skills?
        </h2>
        <p className="text-muted-foreground max-w-md mx-auto mb-8">
          Join thousands of candidates who landed their dream jobs with AI-powered practice.
        </p>
        <Button
          size="lg"
          className="bg-gradient-cta hover:shadow-glow transition-all duration-300 text-base px-8 h-12"
        >
          Start Your First Mock Interview
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </motion.div>
    </section>
  );
};

export default CTASection;
