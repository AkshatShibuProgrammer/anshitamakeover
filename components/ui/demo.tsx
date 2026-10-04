"use client";

import { WorksWheel, type WorksWheelItem } from "@/components/ui/works-wheel";

// Authentic high-resolution editorial & bridal couture imagery from verified Unsplash sources.
// Images are configured with object-contain to render fully without cropping.
const WORKS: WorksWheelItem[] = [
  {
    title: "Imperial Vivah Suite",
    image: "https://images.unsplash.com/photo-1594744803329-e58b31de8bf5?auto=format&fit=crop&w=1200&q=80",
    href: "#imperial-vivah",
  },
  {
    title: "Banarasi Heritage Mukut",
    image: "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=1200&q=80",
    href: "#banarasi-heritage",
  },
  {
    title: "18-Hour Cry-Proof HD",
    image: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=1200&q=80",
    href: "#cry-proof-hd",
  },
  {
    title: "Sangeet Dance Glamour",
    image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=1200&q=80",
    href: "#sangeet-glamour",
  },
  {
    title: "Celestial Golden Glow",
    image: "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?auto=format&fit=crop&w=1200&q=80",
    href: "#celestial-glow",
  },
  {
    title: "High-Fashion Editorial",
    image: "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=1200&q=80",
    href: "#high-fashion",
  },
  {
    title: "Royal Velvet Draping",
    image: "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=1200&q=80",
    href: "#royal-velvet",
  },
  {
    title: "Kundan Eye Architecture",
    image: "https://images.unsplash.com/photo-1509967419530-da38b4704bc6?auto=format&fit=crop&w=1200&q=80",
    href: "#eye-architecture",
  },
  {
    title: "Cathedral Nuptials",
    image: "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=crop&w=1200&q=80",
    href: "#cathedral-nuptials",
  },
];

export default function WorksWheelDemo() {
  return (
    <div className="bg-background text-foreground w-full h-screen">
      <WorksWheel items={WORKS} label="Repertoire '26" action="Explore" />
    </div>
  );
}
