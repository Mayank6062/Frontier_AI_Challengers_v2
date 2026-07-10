import type { ReactNode } from "react";
 
type SectionProps = {
  title: string;
  description?: string;
  children: ReactNode;
};
 
export function Section({ title, description, children }: SectionProps) {
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-slate-950">{title}</h2>
        {description ? <p className="mt-1 text-sm text-slate-500">{description}</p> : null}
      </div>
      {children}
    </section>
  );
}