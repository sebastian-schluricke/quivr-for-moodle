import { useEffect, useRef, useState } from "react";

import { useUserApi } from "@/lib/api/user/useUserApi";
import { useHelpContext } from "@/lib/context/HelpProvider/hooks/useHelpContext";
import { useUserData } from "@/lib/hooks/useUserData";

import styles from "./HelpWindow.module.scss";

import { Icon } from "../ui/Icon/Icon";

export const HelpWindow = (): JSX.Element => {
  const { isVisible, setIsVisible } = useHelpContext();
  const [loadingOnboarded, setLoadingOnboarded] = useState(false);
  const helpWindowRef = useRef<HTMLDivElement>(null);
  const { userIdentityData } = useUserData();
  const { updateUserIdentity } = useUserApi();

  const closeHelpWindow = async () => {
    setIsVisible(false);
    if (userIdentityData && !userIdentityData.onboarded) {
      setLoadingOnboarded(true);
      await updateUserIdentity({
        ...userIdentityData,
        username: userIdentityData.username,
        onboarded: true,
      });
    }
  };

  useEffect(() => {
    if (
      userIdentityData?.username &&
      !userIdentityData.onboarded &&
      !loadingOnboarded
    ) {
      setIsVisible(true);
    }
  });

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        helpWindowRef.current &&
        !helpWindowRef.current.contains(event.target as Node)
      ) {
        void (async () => {
          try {
            await closeHelpWindow();
          } catch (error) {
            console.error("Error while closing help window", error);
          }
        })();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  });

  return (
    <div
      className={`${styles.help_wrapper} ${isVisible ? styles.visible : ""}`}
      ref={helpWindowRef}
    >
      <div className={styles.header}>
        <span className={styles.title}>🧠 Was ist Quivr?</span>
        <Icon
          name="close"
          size="normal"
          color="black"
          handleHover={true}
          onClick={() => closeHelpWindow()}
        />
      </div>
      <div className={styles.content}>
        <div className={styles.section}>
          <span className={styles.title}>
            🧱 Ein KI-Assistent für deinen Unterricht
          </span>
          <span className={styles.section_content}>
            Ein <strong>Brain</strong> ist eine KI-gestützte Wissensbasis, die
            aus deinen Moodle-Kursmaterialien lernt und Schüler:innen fachlich
            fundierte Antworten gibt.
            <ul>
              <li>
                <strong>📚 Moodle-Anbindung</strong>
                <br /> Verbinde dein Brain direkt mit einem Moodle-Kurs. Alle
                Abschnitte, PDFs, Skripte und Texte werden automatisch
                eingelesen und indexiert — ohne manuellen Upload.
              </li>
              <li>
                <strong>🎯 Didaktische Steuerung</strong>
                <br /> Lege pro Moodle-Aktivität fest, wie die KI antworten
                soll: sokratisch mit Rückfragen, als Quizmaster, in einfacher
                Sprache oder als Mathe-Tutor. Fertige Vorlagen erleichtern den
                Einstieg.
              </li>
              <li>
                <strong>🤖 Aktuelle KI-Modelle</strong>
                <br /> Im Hintergrund arbeiten leistungsfähige KI-Modelle, die
                deine Kursinhalte verstehen und darauf basierend antworten.
                Die Schüler:innen sehen das nicht — sie sehen nur den Chat
                ihrer Aktivität.
              </li>
            </ul>
            <p>
              Ein Brain kann für mehrere Aktivitäten genutzt werden. So kannst
              du mit einer einzigen Wissensbasis verschiedene Lernszenarien
              gestalten. 🤝
            </p>
          </span>
        </div>
        <div className={styles.section}>
          <span className={styles.title}>
            🗂️ So richtest du ein Brain ein
          </span>
          <span className={styles.section_content}>
            <p>
              1. <strong>&bdquo;Create Brain&ldquo;</strong> klicken und einen
              Namen vergeben (z.B. &bdquo;Fachschule ET —
              Betriebswirtschaftslehre&ldquo;).
              <br />
              2. Als Quelle <strong>Moodle</strong> wählen und dich einmalig
              mit deinen Moodle-Zugangsdaten anmelden.
              <br />
              3. Den gewünschten Kurs auswählen — die Materialien werden
              automatisch importiert.
              <br />
              4. In Moodle die Aktivität{" "}
              <strong>&bdquo;Quivr Chat&ldquo;</strong> anlegen, das Brain
              auswählen und optional eigene Instruktionen setzen.
            </p>
          </span>
        </div>
        <div className={styles.section}>
          <div className={styles.title}>💬 Direkt mit dem Brain chatten</div>
          <span className={styles.section_content}>
            <p>
              Hier in Quivr kannst du jederzeit selbst mit deinen Brains
              sprechen — z.B. um zu prüfen, ob die KI die Kursmaterialien
              korrekt verstanden hat, bevor deine Schüler:innen damit
              arbeiten.
            </p>
            <p>
              Drücke <strong>@</strong>, um zwischen deinen Brains zu wechseln.
            </p>
          </span>
        </div>
      </div>
    </div>
  );
};
