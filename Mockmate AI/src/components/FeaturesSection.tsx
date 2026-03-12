import { motion } from "framer-motion";
import { Sparkles, Video, Keyboard, BarChart3 } from "lucide-react";

const features = [
  {
    icon: Sparkles,
    title: "AI Generated Questions",
    description: "Smart questions tailored to your resume, job role, and experience level.",
  },
  {
    icon: Video,
    title: "Real Interview Simulation",
    description: "Experience a realistic interview environment with webcam and timed responses.",
  },
  {
    icon: Keyboard,
    title: "Voice or Text Answers",
    description: "Choose your preferred mode — speak naturally or type your responses.",
  },
  {
    icon: BarChart3,
    title: "Detailed Performance Feedback",
    description: "Get scored results with improvement suggestions for every question.",
  },
];

const FeaturesSection = () => {
  return (
    <section id="features" className="py-24 bg-gradient-subtle">
      <div className="container">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            Everything you need to prepare
          </h2>
          <p className="text-muted-foreground max-w-lg mx-auto">
            Powerful features designed to boost your interview confidence.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 gap-6 max-w-3xl mx-auto">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              className="group rounded-2xl border bg-card p-7 shadow-card hover:shadow-card-hover hover:-translate-y-1 transition-all duration-300"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
            >
              <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10 text-primary mb-4 group-hover:bg-gradient-primary group-hover:text-primary-foreground transition-all duration-300">
                <f.icon className="h-5 w-5" />
              </div>
              <h3 className="font-semibold mb-1.5">{f.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {f.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
