import Image from "next/image";

interface QuivrLogoProps {
  size: number;
  color?: "white" | "black" | "primary" | "accent";
}

const customLogoUrl = process.env.NEXT_PUBLIC_LOGO_URL;

export const QuivrLogo = ({
  size,
  color = "white",
}: QuivrLogoProps): JSX.Element => {
  // If custom logo is set, always use it (ignores color variants)
  if (customLogoUrl) {
    const isExternalUrl = customLogoUrl.startsWith("http");

    return (
      <Image
        src={customLogoUrl}
        alt="Logo"
        width={size}
        height={size}
        unoptimized={isExternalUrl}
      />
    );
  }

  // Default Quivr logo with color variants
  let src = "/logo-white.svg";
  if (color === "primary") {
    src = "/logo-primary.svg";
  } else if (color === "accent") {
    src = "/logo-accent.svg";
  } else if (color === "black") {
    src = "/logo-black.svg";
  }

  return <Image src={src} alt="Logo" width={size} height={size} />;
};
