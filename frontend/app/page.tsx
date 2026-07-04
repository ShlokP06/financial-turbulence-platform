import { AmbientBackground } from "@/components/layout/AmbientBackground";
import { Nav } from "@/components/marketing/Nav";
import { Hero } from "@/components/marketing/Hero";
import { Pipeline } from "@/components/marketing/Pipeline";
import { Results } from "@/components/marketing/Results";
import { Methodology } from "@/components/marketing/Methodology";
import { TechStack } from "@/components/marketing/TechStack";
import { Footer } from "@/components/marketing/Footer";

export default function Home() {
  return (
    <>
      <AmbientBackground />
      <Nav />
      <main id="main">
        <Hero />
        <Pipeline />
        <Results />
        <Methodology />
        <TechStack />
      </main>
      <Footer />
    </>
  );
}
