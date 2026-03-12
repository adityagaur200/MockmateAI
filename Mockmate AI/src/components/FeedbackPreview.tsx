import { motion } from "framer-motion";
import { ChevronDown } from "lucide-react";

const questions = [
  "Describe your experience with React.js, highlighting any specific projects or components you've developed.",
  "Explain the differences between Spring Boot and Node.js and why you might choose one over the other for a specific project.",
];

const FeedbackPreview = () => {
  return (
    <section className="py-24">
      <div className="container">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            Detailed Interview Feedback
          </h2>
          <p className="text-muted-foreground max-w-lg mx-auto">
            After every session, get actionable insights to improve.
          </p>
        </motion.div>

        <motion.div
          className="max-w-3xl mx-auto rounded-2xl border bg-card p-8 shadow-card"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h3 className="text-2xl font-bold text-primary mb-1">Congratulation!</h3>
          <h4 className="text-xl font-bold mb-3">Here is your interview feedback</h4>
          <p className="text-primary font-medium mb-1">
            Your overall interview rating: <span className="font-bold">7/10</span>
          </p>
          <p className="text-sm text-muted-foreground mb-6">
            Find below interview question with correct answer, your answer and feedback for improvement
          </p>

          <div className="space-y-3">
            {questions.map((q) => (
              <div
                key={q}
                className="flex items-center justify-between rounded-xl bg-secondary p-4 cursor-pointer hover:bg-secondary/80 transition-colors"
              >
                <p className="text-sm font-medium pr-4">{q}</p>
                <ChevronDown className="h-5 w-5 shrink-0 text-muted-foreground" />
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default FeedbackPreview;
