import { useState } from "react";

import { FieldHeader } from "@/lib/components/ui/FieldHeader/FieldHeader";
import { QuivrButton } from "@/lib/components/ui/QuivrButton/QuivrButton";
import { TextInput } from "@/lib/components/ui/TextInput/TextInput";
import { useSupabase } from "@/lib/context/SupabaseProvider";

import styles from "./PasswordChange.module.scss";

interface PasswordChangeProps {
  highlight?: boolean;
}

export const PasswordChange = ({
  highlight = false,
}: PasswordChangeProps): JSX.Element => {
  const { supabase } = useSupabase();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const handleSubmit = async (): Promise<void> => {
    setMessage(null);

    if (newPassword.length < 8) {
      setMessage({
        type: "error",
        text: "Das Passwort muss mindestens 8 Zeichen lang sein.",
      });

      return;
    }

    if (newPassword !== confirmPassword) {
      setMessage({
        type: "error",
        text: "Die Passwörter stimmen nicht überein.",
      });

      return;
    }

    setIsLoading(true);
    try {
      const { error } = await supabase.auth.updateUser({
        password: newPassword,
      });

      if (error) {
        setMessage({ type: "error", text: error.message });
      } else {
        setMessage({
          type: "success",
          text: "Passwort erfolgreich geändert.",
        });
        setNewPassword("");
        setConfirmPassword("");
      }
    } catch (e) {
      setMessage({
        type: "error",
        text: "Unerwarteter Fehler beim Speichern des Passworts.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className={`${styles.password_change_wrapper} ${
        highlight ? styles.highlight : ""
      }`}
    >
      <div>
        <FieldHeader iconName="key" label="Neues Passwort" />
        <TextInput
          label="mindestens 8 Zeichen"
          inputValue={newPassword}
          setInputValue={setNewPassword}
          crypted={true}
        />
      </div>

      <div>
        <FieldHeader iconName="key" label="Passwort bestätigen" />
        <TextInput
          label="erneut eingeben"
          inputValue={confirmPassword}
          setInputValue={setConfirmPassword}
          crypted={true}
          onSubmit={() => void handleSubmit()}
        />
      </div>

      {message && (
        <div
          className={`${styles.message} ${
            message.type === "success" ? styles.success : styles.error
          }`}
        >
          {message.text}
        </div>
      )}

      <div className={styles.button_wrapper}>
        <QuivrButton
          label="Passwort speichern"
          color="primary"
          iconName="key"
          isLoading={isLoading}
          onClick={() => void handleSubmit()}
          disabled={!newPassword || !confirmPassword}
        />
      </div>
    </div>
  );
};
