import { useState } from "react";
import { Controller, FormProvider, useForm } from "react-hook-form";

import { useUserApi } from "@/lib/api/user/useUserApi";
import { CompanySize, UsagePurpose } from "@/lib/api/user/user";
import { Modal } from "@/lib/components/ui/Modal/Modal";
import { useOnboardingContext } from "@/lib/context/OnboardingProvider/hooks/useOnboardingContext";
import { useSupabase } from "@/lib/context/SupabaseProvider";

import styles from "./OnboardingModal.module.scss";

import { OnboardingProps } from "../OnboardingModal/types/types";
import { FieldHeader } from "../ui/FieldHeader/FieldHeader";
import { QuivrButton } from "../ui/QuivrButton/QuivrButton";
import { SingleSelector } from "../ui/SingleSelector/SingleSelector";
import { TextInput } from "../ui/TextInput/TextInput";

export const OnboardingModal = (): JSX.Element => {
  const {
    isOnboardingModalOpened,
    setIsOnboardingModalOpened,
    isBrainCreated,
  } = useOnboardingContext();
  const { supabase } = useSupabase();

  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [passwordError, setPasswordError] = useState<string | null>(null);

  const methods = useForm<OnboardingProps>({
    defaultValues: {
      username: "",
      companyName: "",
      companySize: undefined,
      usagePurpose: "",
    },
  });
  const { watch } = methods;
  const username = watch("username");

  const { updateUserIdentity } = useUserApi();

  const companySizeOptions = Object.entries(CompanySize).map(([, value]) => ({
    label: value,
    value: value,
  }));

  const usagePurposeOptions = Object.entries(UsagePurpose).map(
    ([key, value]) => ({
      label: value,
      value: key,
    })
  );

  const submitForm = async () => {
    setPasswordError(null);

    // Validate password if user filled at least one of the password fields.
    if (password || passwordConfirm) {
      if (password.length < 8) {
        setPasswordError("Das Passwort muss mindestens 8 Zeichen lang sein.");

        return;
      }
      if (password !== passwordConfirm) {
        setPasswordError("Die Passwörter stimmen nicht überein.");

        return;
      }
      const { error } = await supabase.auth.updateUser({ password });
      if (error) {
        setPasswordError(error.message);

        return;
      }
    }

    await updateUserIdentity({
      username: methods.getValues("username"),
      company: methods.getValues("companyName"),
      onboarded: isBrainCreated,
      company_size: methods.getValues("companySize"),
      usage_purpose: methods.getValues("usagePurpose") as
        | UsagePurpose
        | undefined,
    });
    window.location.reload();
  };

  return (
    <FormProvider {...methods}>
      <Modal
        title="Welcome to Quivr!"
        desc="Let us know a bit more about you to get started."
        isOpen={isOnboardingModalOpened}
        setOpen={setIsOnboardingModalOpened}
        CloseTrigger={<div />}
        unclosable={true}
      >
        <div className={styles.modal_content_wrapper}>
          <div className={styles.form_wrapper}>
            <div>
              <FieldHeader
                iconName="key"
                label="Neues Passwort"
                mandatory={true}
              />
              <TextInput
                label="mindestens 8 Zeichen"
                inputValue={password}
                setInputValue={setPassword}
                crypted={true}
              />
            </div>
            <div>
              <FieldHeader
                iconName="key"
                label="Passwort bestätigen"
                mandatory={true}
              />
              <TextInput
                label="erneut eingeben"
                inputValue={passwordConfirm}
                setInputValue={setPasswordConfirm}
                crypted={true}
              />
              {passwordError && (
                <div className={styles.password_error}>{passwordError}</div>
              )}
            </div>
            <div>
              <FieldHeader iconName="user" label="Username" mandatory={true} />
              <Controller
                name="username"
                render={({ field }) => (
                  <TextInput
                    label="Choose a username"
                    inputValue={field.value as string}
                    setInputValue={field.onChange}
                  />
                )}
              />
            </div>
            <div>
              <FieldHeader iconName="office" label="Company" />
              <Controller
                name="companyName"
                render={({ field }) => (
                  <TextInput
                    label="Your company name"
                    inputValue={field.value as string}
                    setInputValue={field.onChange}
                  />
                )}
              />
            </div>
            <div>
              <FieldHeader iconName="goal" label="Usage Purpose" />
              <Controller
                name="usagePurpose"
                render={({ field }) => (
                  <SingleSelector
                    iconName="goal"
                    options={usagePurposeOptions}
                    placeholder="In what context will you be using Quivr"
                    selectedOption={
                      field.value
                        ? {
                            label: field.value as string,
                            value: field.value as string,
                          }
                        : undefined
                    }
                    onChange={field.onChange}
                  />
                )}
              />
            </div>
            <div>
              <FieldHeader iconName="hashtag" label="Size of your company" />
              <Controller
                name="companySize"
                render={({ field }) => (
                  <SingleSelector
                    iconName="hashtag"
                    options={companySizeOptions}
                    placeholder="Number of employees in your company"
                    selectedOption={
                      field.value
                        ? {
                            label: field.value as string,
                            value: field.value as string,
                          }
                        : undefined
                    }
                    onChange={field.onChange}
                  />
                )}
              />
            </div>
          </div>
          <div className={styles.button_wrapper}>
            <QuivrButton
              iconName="chevronRight"
              label="Submit"
              color="primary"
              onClick={() => void submitForm()}
              disabled={!username || !password || !passwordConfirm}
            />
          </div>
        </div>
      </Modal>
    </FormProvider>
  );
};
