import Image from "next/image";
import { useEffect, useState } from "react";

interface SchoolLogoProps {
  size: number;
  color?: "white" | "black" | "primary" | "accent";
  className?: string;
}

/**
 * Configurable school logo component that reads from environment variables.
 *
 * Environment Variables:
 * - NEXT_PUBLIC_SCHOOL_LOGO_PATH: Path to the school logo (default: /eckener-schule-logo.png)
 * - NEXT_PUBLIC_SCHOOL_NAME: Name of the school (default: Eckener-Schule)
 *
 * For schools with color-specific logos, you can use:
 * - NEXT_PUBLIC_SCHOOL_LOGO_WHITE: Path to white version
 * - NEXT_PUBLIC_SCHOOL_LOGO_BLACK: Path to black version
 * - NEXT_PUBLIC_SCHOOL_LOGO_PRIMARY: Path to primary color version
 * - NEXT_PUBLIC_SCHOOL_LOGO_ACCENT: Path to accent color version
 */
export const SchoolLogo = ({
  size,
  color = "white",
  className = "",
}: SchoolLogoProps): JSX.Element => {
  const [src, setSrc] = useState<string>("/eckener-schule-logo.png");
  const [alt, setAlt] = useState<string>("School Logo");

  useEffect(() => {
    // Get school name from environment or use default
    const schoolName = process.env.NEXT_PUBLIC_SCHOOL_NAME || "Eckener-Schule";
    setAlt(`${schoolName} Logo`);

    // Check for color-specific logos first
    const colorSpecificLogos = {
      white: process.env.NEXT_PUBLIC_SCHOOL_LOGO_WHITE,
      black: process.env.NEXT_PUBLIC_SCHOOL_LOGO_BLACK,
      primary: process.env.NEXT_PUBLIC_SCHOOL_LOGO_PRIMARY,
      accent: process.env.NEXT_PUBLIC_SCHOOL_LOGO_ACCENT,
    };

    // Use color-specific logo if available, otherwise use default logo path
    const colorLogo = colorSpecificLogos[color];
    if (colorLogo) {
      setSrc(colorLogo);
    } else {
      const defaultLogo =
        process.env.NEXT_PUBLIC_SCHOOL_LOGO_PATH || "/eckener-schule-logo.png";
      setSrc(defaultLogo);
    }
  }, [color]);

  return (
    <Image
      src={src}
      alt={alt}
      width={size}
      height={size}
      className={className}
    />
  );
};
