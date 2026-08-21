import React from "react";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "glow" | "outline";
  padding?: "none" | "sm" | "md" | "lg";
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = "default",
  padding = "md",
  className = "",
  ...props
}) => {
  const paddingStyles = {
    none: "p-0",
    sm: "p-3",
    md: "p-5",
    lg: "p-6",
  };

  const variantStyles = {
    default:
      "bg-slate-900/80 backdrop-blur-md border border-slate-800/80 rounded-xl shadow-xl shadow-black/20",
    glow:
      "bg-slate-900/90 backdrop-blur-md border border-indigo-500/30 rounded-xl shadow-lg shadow-indigo-500/10",
    outline:
      "bg-transparent border border-slate-800 rounded-xl",
  };

  return (
    <div
      className={`${variantStyles[variant]} ${paddingStyles[padding]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = "",
  ...props
}) => (
  <div className={`flex items-center justify-between pb-4 border-b border-slate-800/60 mb-4 ${className}`} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
  children,
  className = "",
  ...props
}) => (
  <h3 className={`text-base font-semibold text-slate-100 flex items-center gap-2 ${className}`} {...props}>
    {children}
  </h3>
);

export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({
  children,
  className = "",
  ...props
}) => (
  <p className={`text-xs text-slate-400 mt-1 ${className}`} {...props}>
    {children}
  </p>
);

export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  padding?: "none" | "sm" | "md" | "lg";
}

export const CardContent: React.FC<CardContentProps> = ({
  children,
  padding = "none",
  className = "",
  ...props
}) => {
  const paddingStyles = {
    none: "p-0",
    sm: "p-3",
    md: "p-4",
    lg: "p-6",
  };

  return (
    <div className={`${paddingStyles[padding]} ${className}`} {...props}>
      {children}
    </div>
  );
};
