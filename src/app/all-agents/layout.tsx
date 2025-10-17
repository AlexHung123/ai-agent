import type { ReactNode } from 'react';

export default function AllAgentsLayout({
  children,
}: {
  children: ReactNode;
}) {
  return <div>{children}</div>;
}