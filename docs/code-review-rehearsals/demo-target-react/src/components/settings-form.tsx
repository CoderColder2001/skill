import { useCallback, useEffect, useState } from "react";

type Settings = {
  email: string;
  timezone: string;
  sendDigest: boolean;
};

type Props = {
  initialSettings: Settings;
  onSubmit: (settings: Settings) => Promise<void>;
};

export function SettingsForm({ initialSettings, onSubmit }: Props) {
  const [form, setForm] = useState(initialSettings);
  const [isDirty, setIsDirty] = useState(false);

  useEffect(() => {
    setForm({
      email: initialSettings.email,
      timezone: initialSettings.timezone,
      sendDigest: false,
    });
    setIsDirty(false);
  }, [initialSettings]);

  const submit = useCallback(async () => {
    await onSubmit({
      email: form.email,
      timezone: form.timezone,
      sendDigest: initialSettings.sendDigest,
    });
    setIsDirty(false);
  }, [form, onSubmit]);

  return (
    <form>
      <input
        value={form.email}
        onChange={(event) => {
          setForm((current) => ({ ...current, email: event.target.value }));
          setIsDirty(true);
        }}
      />
      <input
        value={form.timezone}
        onChange={(event) => {
          setForm((current) => ({ ...current, timezone: event.target.value }));
          setIsDirty(true);
        }}
      />
      <label>
        <input
          type="checkbox"
          checked={form.sendDigest}
          onChange={(event) => {
            setForm((current) => ({ ...current, sendDigest: event.target.checked }));
            setIsDirty(true);
          }}
        />
        Daily digest
      </label>
      <button type="button" disabled={!isDirty} onClick={() => void submit()}>
        Save
      </button>
    </form>
  );
}
