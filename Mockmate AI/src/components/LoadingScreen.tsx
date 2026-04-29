import { motion } from "framer-motion";

interface LoadingScreenProps {
  message?: string;
  detail?: string;
}

const LoadingScreen = ({
  message = "Loading your AI experience...",
  detail = "This may take a few seconds while we prepare everything for you.",
}: LoadingScreenProps) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col items-center gap-8"
      >
        {/* Animated Loading Spinner */}
        <div className="relative w-16 h-16">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0 rounded-full border-2 border-transparent border-t-primary border-r-primary"
          />
        </div>

        {/* Message */}
        <div className="text-center max-w-md">
          <h2 className="text-xl font-semibold text-foreground mb-2">
            {message}
          </h2>
          <p className="text-sm text-muted-foreground">
            {detail}
          </p>
        </div>

        {/* Loading Dots */}
        <div className="flex gap-2">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
              className="w-2 h-2 bg-primary rounded-full"
            />
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default LoadingScreen;
