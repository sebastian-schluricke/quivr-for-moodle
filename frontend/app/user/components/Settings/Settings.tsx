import { useEffect, useRef } from "react";

import { Icon } from "@/lib/components/ui/Icon/Icon";

import { ApiKeyConfig } from "./ApiKeyConfig";
import { InfoSection } from "./InfoSection/InfoSection";
import { PasswordChange } from "./PasswordChange";
import styles from "./Settings.module.scss";

import { StripePricingOrManageButton } from "../StripePricingOrManageButton";

const showTokensSettings = process.env.NEXT_PUBLIC_SHOW_TOKENS === "true";

type InfoDisplayerProps = {
  email: string;
  username: string;
  remainingCredits: number;
  passwordSetupRequested?: boolean;
};

export const Settings = ({
  email,
  username,
  remainingCredits,
  passwordSetupRequested = false,
}: InfoDisplayerProps): JSX.Element => {
  const passwordSectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (passwordSetupRequested && passwordSectionRef.current) {
      passwordSectionRef.current.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  }, [passwordSetupRequested]);

  return (
    <div className={styles.settings_wrapper}>
      <span className={styles.title}>
        General settings and main information
      </span>
      {passwordSetupRequested && (
        <div className={styles.setup_banner}>
          <Icon name="key" color="primary" size="normal" />
          <span>
            <strong>Bitte setze jetzt dein Passwort</strong>
            <br />
            Damit du dich beim nächsten Mal direkt anmelden kannst, vergib bitte
            ein eigenes Passwort.
          </span>
        </div>
      )}
      <div className={styles.infos_wrapper}>
        <InfoSection iconName="email" title="Email">
          <span className={styles.bold}>{email}</span>
        </InfoSection>
        <InfoSection iconName="user" title="Username">
          <span className={styles.bold}>{username}</span>
        </InfoSection>
        {!!showTokensSettings && (
          <InfoSection iconName="coin" title="Remaining credits">
            <div className={styles.remaining_credits}>
              <span className={styles.credits}>{remainingCredits}</span>
              <Icon name="coin" color="gold" size="normal" />
            </div>
          </InfoSection>
        )}
        <InfoSection iconName="key" title="Passwort">
          <div ref={passwordSectionRef}>
            <PasswordChange highlight={passwordSetupRequested} />
          </div>
        </InfoSection>
        <InfoSection iconName="key" title="Quivr API Key">
          <div className={styles.text_and_button}>
            <span className={styles.text}>
              The Quivr API key is a unique identifier that allows you to access
              and interact with{" "}
              <a
                href="https://api.quivr.app/docs"
                target="_blank"
                rel="noopener noreferrer"
                className={styles.link}
              >
                Quivr&apos;s API.
              </a>
            </span>
            <div className={styles.button}>
              <ApiKeyConfig />
            </div>
          </div>
        </InfoSection>
        {!!showTokensSettings && (
          <InfoSection iconName="star" title="My plan" last={true}>
            <div className={styles.text_and_button}>
              <span className={styles.text}>
                Customize your subscription to best suit your needs. By
                upgrading to a premium plan, you gain access to a host of
                additional benefits, including significantly more chat credits
                and the ability to create more Brains.
              </span>
              <div className={styles.button}>
                <StripePricingOrManageButton small={true} />
              </div>
            </div>
          </InfoSection>
        )}
      </div>
    </div>
  );
};
