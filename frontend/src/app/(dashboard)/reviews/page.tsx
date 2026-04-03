"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import type { Review } from "@/types/review";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex items-center gap-0.5" aria-label={`${rating} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map((star) => (
        <span
          key={star}
          className={`text-lg ${
            star <= rating ? "text-yellow-500" : "text-muted-foreground/30"
          }`}
        >
          *
        </span>
      ))}
      <span className="ml-1 text-sm text-muted-foreground">
        {rating.toFixed(1)}
      </span>
    </div>
  );
}

export default function ReviewsPage() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    api
      .get("/companies/my")
      .then(async (res) => {
        const cId = res.data.id;
        const reviewsRes = await api.get(`/reviews/company/${cId}`);
        setReviews(reviewsRes.data.items ?? reviewsRes.data);
      })
      .catch(() => setError("Failed to load reviews."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-20 text-center">
        <p className="text-destructive">{error}</p>
      </div>
    );
  }

  const avgRating =
    reviews.length > 0
      ? reviews.reduce((sum, r) => sum + r.overall_rating, 0) / reviews.length
      : 0;

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Reviews</h1>

      {/* Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Overall Rating</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center gap-4">
          <div className="text-4xl font-bold">
            {reviews.length > 0 ? avgRating.toFixed(1) : "—"}
          </div>
          <div>
            {reviews.length > 0 && <StarRating rating={Math.round(avgRating)} />}
            <p className="text-sm text-muted-foreground">
              {reviews.length} review{reviews.length !== 1 ? "s" : ""}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Reviews list */}
      {reviews.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-muted-foreground">
              No reviews yet. Reviews will appear here once clients rate your
              company.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {reviews.map((review) => (
            <Card key={review.id}>
              <CardContent className="pt-6 space-y-3">
                <div className="flex items-center justify-between">
                  <p className="font-medium">
                    {review.reviewer_name ?? "Anonymous"}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(review.created_at).toLocaleDateString()}
                  </p>
                </div>
                <StarRating rating={review.overall_rating} />
                {(review.response_speed ||
                  review.communication ||
                  review.documentation) && (
                  <div className="flex gap-4 text-xs text-muted-foreground">
                    {review.response_speed != null && (
                      <span>Speed: {review.response_speed}/5</span>
                    )}
                    {review.communication != null && (
                      <span>Communication: {review.communication}/5</span>
                    )}
                    {review.documentation != null && (
                      <span>Documentation: {review.documentation}/5</span>
                    )}
                  </div>
                )}
                {review.comment && (
                  <>
                    <Separator />
                    <p className="text-sm">{review.comment}</p>
                  </>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
