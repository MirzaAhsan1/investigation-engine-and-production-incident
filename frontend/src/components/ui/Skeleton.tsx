import React from "react";

export interface SkeletonProps {
  className?: string;
  height?: string;
  width?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = "",
  height = "h-4",
  width = "w-full",
}) => {
  return (
    <div
      className={`bg-slate-800/60 animate-pulse rounded-md ${height} ${width} ${className}`}
    />
  );
};
