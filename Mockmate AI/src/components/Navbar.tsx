import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Brain, Menu, X } from "lucide-react";

const navLinks = [
  { label: "Features", to: "/#features" },
  { label: "How It Works", to: "/how-it-works" },
  { label: "Dashboard", to: "/dashboard" },
  { label: "Performance", to: "/performance" },
];

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const isActive = (to: string) => location.pathname === to;

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-background/80 backdrop-blur-xl border-b shadow-card"
          : "bg-transparent"
      }`}
    >
      <div className="container flex items-center justify-between h-16">
        <Link to="/" className="flex items-center gap-2">
          <Brain className="h-7 w-7 text-primary" />
          <span className="font-semibold text-lg tracking-tight">Mockmate AI</span>
        </Link>

        <div className="hidden md:flex items-center gap-8">
          {navLinks.map((l) =>
            l.to.startsWith("/#") ? (
              <a
                key={l.label}
                href={l.to}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                {l.label}
              </a>
            ) : (
              <Link
                key={l.label}
                to={l.to}
                className={`text-sm transition-colors ${
                  isActive(l.to) ? "text-foreground font-medium" : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {l.label}
              </Link>
            )
          )}
          <Button size="sm" className="bg-gradient-primary hover:shadow-glow transition-shadow">
            Sign In
          </Button>
        </div>

        <button className="md:hidden" onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {mobileOpen && (
        <div className="md:hidden bg-background/95 backdrop-blur-xl border-b pb-4">
          <div className="container flex flex-col gap-3">
            {navLinks.map((l) =>
              l.to.startsWith("/#") ? (
                <a
                  key={l.label}
                  href={l.to}
                  className="text-sm text-muted-foreground py-2"
                  onClick={() => setMobileOpen(false)}
                >
                  {l.label}
                </a>
              ) : (
                <Link
                  key={l.label}
                  to={l.to}
                  className="text-sm text-muted-foreground py-2"
                  onClick={() => setMobileOpen(false)}
                >
                  {l.label}
                </Link>
              )
            )}
            <Button size="sm" className="bg-gradient-primary w-fit">Sign In</Button>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
