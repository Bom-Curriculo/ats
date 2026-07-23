import { Skeleton } from "@/components/ui/skeleton";

interface ResumeListSkeletonProps {
  count?: number;
}

export default function ResumeListSkeleton({ count = 3 }: ResumeListSkeletonProps) {
  return (
    <section className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: count }).map((_, index) => (
        <Skeleton key={index} className="h-48 rounded-2xl" />
      ))}
    </section>
  );
}
