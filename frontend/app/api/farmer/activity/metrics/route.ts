import { NextResponse } from "next/server";

export async function GET() {
  // TODO: Replace with real service call and return ActivityMetric[].
  // Example shape:
  // return NextResponse.json([{ id, label, value, status, icon, color }]);
  return NextResponse.json(
    { message: "TODO: Implement farmer activity metrics endpoint" },
    { status: 501 },
  );
}
