'use client';
import { useTheme } from 'next-themes';
import { useCallback, useEffect, useState } from 'react';
import Select from '../ui/Select';

type Theme = 'light';

const ThemeSwitcher = ({ className }: { className?: string }) => {
  const [mounted, setMounted] = useState(false);

  const { theme, setTheme } = useTheme();

  const isTheme = useCallback((t: Theme) => t === theme, [theme]);

  const handleThemeSwitch = (theme: Theme) => {
    setTheme(theme);
  };

  useEffect(() => {
    setMounted(true);
  }, []);

  // Force light theme on mount
  useEffect(() => {
    if (theme !== 'light') {
      setTheme('light');
    }
  }, [theme, setTheme]);

  // Avoid Hydration Mismatch
  if (!mounted) {
    return null;
  }

  return (
    <Select
      className={className}
      value={theme}
      onChange={(e) => handleThemeSwitch(e.target.value as Theme)}
      options={[
        { value: 'light', label: 'Light' },
      ]}
    />
  );
};

export default ThemeSwitcher;
