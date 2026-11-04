import React from "react";
import { CheckCircle2, XCircle } from "lucide-react";
import { Button } from "./Button";

interface ApproveRejectButtonsProps {
  status: string;
  onApprove: () => void;
  onReject: () => void;
  isLoadingApprove?: boolean;
  isLoadingReject?: boolean;
  disabled?: boolean;
}

export const ApproveRejectButtons: React.FC<ApproveRejectButtonsProps> = ({
  status,
  onApprove,
  onReject,
  isLoadingApprove = false,
  isLoadingReject = false,
  disabled = false,
}) => {
  const statusUpper = (status || "").toUpperCase();
  const isPending = statusUpper === "PENDING" || statusUpper === "PENDING_APPROVAL";
  const isDisabled = !isPending || disabled || isLoadingApprove || isLoadingReject;

  return (
    <div className="flex items-center gap-2">
      <Button
        variant="secondary"
        size="sm"
        disabled={isDisabled}
        isLoading={isLoadingReject}
        onClick={onReject}
        leftIcon={<XCircle className="w-3.5 h-3.5 text-rose-400" />}
      >
        Reject
      </Button>
      <Button
        variant="primary"
        size="sm"
        disabled={isDisabled}
        isLoading={isLoadingApprove}
        onClick={onApprove}
        leftIcon={<CheckCircle2 className="w-3.5 h-3.5" />}
      >
        Approve
      </Button>
    </div>
  );
};
